from django.urls import path
from .views import  *

urlpatterns = [
    path('karyawan', karyawan, name="karyawan"),
    path('postkaryawan', postkaryawan, name="postkaryawan"),
    path('face_recognition_absen', face_recognition_absen, name="face_recognition_absen"),
    path('master_user', master_user, name='master_user'),
    path('delete_karyawan/<str:nik>/', delete_karyawan, name='delete_karyawan'),
    path('update_karyawan/<str:nik>/', update_karyawan, name='update_karyawan'),
    path('absen/<str:nik>/', list_absensi, name='list_absen'),
    path('clear_absensi/',clear_absensi, name='clear_absensi'),
]
