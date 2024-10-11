from django.shortcuts import render, redirect , get_object_or_404
from .forms import KaryawanForm
from .models import Karyawan, Absen
import face_recognition
import numpy as np
from django.core.files.base import ContentFile
import base64
from django.http import JsonResponse
from django.contrib import messages
from django.core.files.storage import default_storage

def karyawan(request):
    return render(request, 'karyawan/karyawan.html')

def clear_absensi(request):
    if request.method == 'POST':
        Absen.objects.all().delete()
        messages.success(request, 'Data absensi berhasil dihapus.')
        return redirect('list_absensi')

    return redirect('list_absensi')

def list_absensi(request, nik):
    karyawan = get_object_or_404(Karyawan, nik=nik)
    kehadiran = Absen.objects.filter(nik=nik)  # Pastikan ini sesuai dengan field di model Absen
    
    context = {
        'karyawan': karyawan,  # Mengirimkan instance Karyawan
        'kehadiran': kehadiran,
    }
    return render(request, 'karyawan/list_absensi.html', context)

def postkaryawan(request):
    if request.method == 'POST':
        nik = request.POST['nik']
        name = request.POST['name']
        divisi = request.POST['divisi']
        photo_data = request.POST.get('photo', '')

        if photo_data:
            try:
                # Decode base64 image from the photo data
                format, imgstr = photo_data.split(';base64,')
                ext = format.split('/')[-1]
                data = ContentFile(base64.b64decode(imgstr), name=f'{nik}.{ext}')

                # Create new Karyawan entry
                karyawan = Karyawan(
                    nik=nik,
                    name=name,
                    divisi=divisi,
                    photo=data
                )
                karyawan.save()

                messages.success(request, 'Data karyawan berhasil diupload.')
                return redirect('karyawan')
            except Exception as e:
                messages.error(request, f'Gagal mengupload data karyawan: {e}')
        else:
            messages.error(request, 'Foto tidak tersedia atau tidak valid.')

    return redirect('karyawan')

def master_user(request):
    karyawan_list = Karyawan.objects.all()

    if request.method == 'POST':
        form = KaryawanForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data karyawan berhasil ditambahkan.')
            return redirect('master_user')
        else:
            messages.error(request, 'Terjadi kesalahan saat menambahkan data karyawan.')
    else:
        form = KaryawanForm()

    context = {
        'karyawan_list': karyawan_list,
        'form': form
    }
    return render(request, 'karyawan/master_user.html', context)

def delete_karyawan(request, nik):
    try:
        karyawan = Karyawan.objects.get(nik=nik)
        karyawan.delete()
        messages.success(request, 'Data karyawan berhasil dihapus.')
    except Karyawan.DoesNotExist:
        messages.error(request, 'Karyawan tidak ditemukan.')

    return redirect('master_user')

def update_karyawan(request, nik):
    try:
        karyawan = Karyawan.objects.get(nik=nik)
        if request.method == 'POST':
            form = KaryawanForm(request.POST, request.FILES, instance=karyawan)
            if form.is_valid():
                form.save()
                messages.success(request, 'Data karyawan berhasil diperbarui.')
                return redirect('master_user')
            else:
                messages.error(request, 'Terjadi kesalahan saat memperbarui data karyawan.')
        else:
            form = KaryawanForm(instance=karyawan)

        context = {
            'form': form,
            'karyawan': karyawan
        }
        return render(request, 'karyawan/update_karyawan.html', context)
    except Karyawan.DoesNotExist:
        messages.error(request, 'Karyawan tidak ditemukan.')
        return redirect('master_user')

def face_recognition_absen(request):
    if request.method == 'POST':
        photo_data = request.POST.get('photo')

        if not photo_data:
            return JsonResponse({'status': 'error', 'message': 'Foto tidak valid'})

        # Decode base64 photo
        format, imgstr = photo_data.split(';base64,')
        ext = format.split('/')[-1]
        photo_data = ContentFile(base64.b64decode(imgstr), name=f'temp_photo.{ext}')

        try:
            # Process the uploaded base64 photo
            img_data = base64.b64decode(imgstr)
            temp_file_name = f'temp_photo.{ext}'
            temp_file_path = default_storage.save(temp_file_name, ContentFile(img_data))
            temp_file_full_path = default_storage.path(temp_file_path)

            # Load the uploaded photo
            uploaded_image = face_recognition.load_image_file(temp_file_full_path)
            uploaded_encoding = face_recognition.face_encodings(uploaded_image)

            if len(uploaded_encoding) == 0:
                default_storage.delete(temp_file_path)
                return JsonResponse({'status': 'error', 'message': 'Tidak dapat mengenali wajah pada foto yang diunggah'})

            uploaded_encoding = uploaded_encoding[0]

            # Loop through all Karyawan and compare faces
            all_karyawan = Karyawan.objects.all()
            for karyawan in all_karyawan:
                karyawan_photo_path = karyawan.photo.path
                karyawan_photo = face_recognition.load_image_file(karyawan_photo_path)
                karyawan_encoding = face_recognition.face_encodings(karyawan_photo)

                if len(karyawan_encoding) == 0:
                    continue  
                karyawan_encoding = karyawan_encoding[0]

                # Compare the uploaded photo with the database photo
                results = face_recognition.compare_faces([karyawan_encoding], uploaded_encoding)

                if results[0]:
                    Absen.objects.create(nik=karyawan.nik)
                    default_storage.delete(temp_file_path)
                    messages.success(request, 'Berhasil Absen')
                    return JsonResponse({
                        'status': 'success', 
                        'message': 'Berhasil Absen',
                        'nik': karyawan.nik,
                        'name': karyawan.name
                    })

            default_storage.delete(temp_file_path)
            return JsonResponse({'status': 'error', 'message': 'Wajah tidak cocok dengan data manapun'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Gagal memproses absensi: {e}'})

    return render(request, 'karyawan/absen_camera.html')