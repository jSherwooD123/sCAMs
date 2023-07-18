from django.shortcuts import render, redirect
from Monitor.models import Room, Camera, Video
from django.db.models import Prefetch
from .forms import CameraAdd, RoomAdd


def index(request):
    return redirect('/Manage/')

def view_cam(request, pk):
    queryset = Camera.objects.get(pk = pk)
    ip = f'http://{queryset.ip_address}:{queryset.port_num}/video_feed'

    return render(request, 'view_camera.html', {'addr' : ip})

def manage(request):
    camera_add = CameraAdd()
    room_add = RoomAdd()

    if request.method == 'POST':

        if 'camera_submit' in request.POST:
            camera_add = CameraAdd(request.POST)
            if camera_add.is_valid():
                camera_add.save()
                return redirect('/Manage/') 
             
        elif 'room_submit' in request.POST:
            room_add = RoomAdd(request.POST)
            if room_add.is_valid():
                room_add.save()
                return redirect('/Manage/')  

    rooms = Room.objects.prefetch_related('camera_set')

    return render(request, 'manage.html', {'rooms': rooms, 'camera_form': camera_add, 'room_form': room_add})

def manage_cam(request, pk):
    queryset = Camera.objects.get(pk = pk)
    return render(request, 'manage_camera.html', {'camera': queryset})

def delete_camera(request, pk):
    delete = Camera.objects.get(pk = pk)

    if request.method == "POST":
        delete.delete()
        return redirect('/Manage/')
    
    return render(request, 'camera_delete.html', {'camera': delete})

def delete_room(request, pk):
    delete = Room.objects.get(pk = pk)

    if request.method == "POST":
        delete.delete()
        return redirect('/Manage/')
    
    return render(request, 'room_delete.html', {'room': delete})