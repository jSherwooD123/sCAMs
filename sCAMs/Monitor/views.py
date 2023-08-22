from Monitor.models import Room, Camera, Video
from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Prefetch
from zipfile import ZipFile
from .Scripts.schedualing import Cycle
from .forms import CameraAdd, RoomAdd, VideoFilter
import urllib.request
import os,threading

schedual = Cycle()

def check_connection(ip,port,name):
    ip =f'http://{ip}:{port}/video_feed'
    camera = Camera.objects.get(c_name=name)
    try:   
        connection = urllib.request.urlopen(ip).getcode()
        if connection == 200:
            camera.active = True

            isin = False
            for i,v in enumerate(schedual.cam_threads):
                if v.pk == camera.pk:
                    isin = True
                    if v.recording == False:
                        threading.Thread(target=schedual.cam_threads[i].startRecording,daemon=True).start()

            if not isin:
                schedual.addThread(camera)

        else:
            camera.active = False
    except:
       camera.active = False
    camera.last_active = timezone.now() 
    camera.save()

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
                check_connection(request.POST["ip_address"],request.POST["port_num"],request.POST["c_name"])
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

    if request.method == 'POST':
        if 'check_status' in request.POST:
            check_connection(queryset.ip_address,queryset.port_num,queryset.c_name)
            return redirect(f'/Manage/{queryset.pk}/')
        
    return render(request, 'manage_camera.html', {'camera': queryset})

def video_query(request):
    videos = Video.objects.all()
    form = VideoFilter()

    if request.method == 'POST':
        if 'SF' in request.POST:
            form = VideoFilter(request.POST)
            if form.is_valid():
                if form.cleaned_data['humans_detected'] is not None:
                    videos = videos.filter(humans_detected=form.cleaned_data['humans_detected'])

                created_after = form.cleaned_data.get('created_after')
                created_before = form.cleaned_data.get('created_before')
                if created_after and created_before:
                    videos = videos.filter(created_at__range=(created_after, created_before))
                
                camera_name = form.cleaned_data.get('camera')
                if camera_name:
                    videos = videos.filter(camera=camera_name)

        elif 'multiple_download' in request.POST:
            pk_lst = request.POST.getlist('selected')
            pk_lst = [int(i) for i in pk_lst]

            queryset = Video.objects.filter(pk__in=pk_lst)
            v_name_lst = [[obj.camera.pk,obj.v_name] for obj in queryset]
            loc_lst = [os.path.join(os.getcwd(),'Storage',f'{i[0]}',f'output_video_{i[1]}.mp4') for i in v_name_lst]

            zip_name = f'{datetime.now().strftime("%H_%M_%S")}.zip'
            zip_name = os.path.join(os.getcwd(),'ZIPS',zip_name)
            with ZipFile(zip_name, 'w') as zip_object:
                for  loc in loc_lst:
                    if os.path.exists(loc):
                        zip_object.write(loc, os.path.basename(loc))

            with open(zip_name,'rb') as x:                                       
                response = HttpResponse(x.read(),content_type="video/H264")      
                response['Content-Disposition']='inline;filename='+os.path.basename(zip_name) 
                return response
                        

    return render(request, 'video_query.html', {'videos': videos, 'form': form})

def delete_room(request, pk):
    delete = Room.objects.get(pk = pk)

    if request.method == "POST":
        if 'Delete' in request.POST:
            delete.delete()
            return redirect('/Manage/')
    
    return render(request, 'room_delete.html', {'room': delete})

def delete_camera(request, pk):
    delete = Camera.objects.get(pk = pk)

    for i,v in enumerate(schedual.cam_threads):
        if v.pk == delete.pk:
            del schedual.cam_threads[i]

    if request.method == "POST":
        if 'Delete' in request.POST:
            delete.delete()
            return redirect('/Manage/')
    
    return render(request, 'camera_delete.html', {'camera': delete})

def delete_video(request,pk):
    delete = Video.objects.get(pk=pk)
    file_name = f'output_video_{delete.v_name}.mp4'
    file_loc = os.path.join(os.getcwd(),'Storage',f'{delete.camera.pk}',file_name)

    if request.method == "POST":
        if 'Delete' in request.POST:
            delete.delete()
            
            try:
                os.remove(file_loc)
            except OSError:
                print('File not found')

            return redirect('/Video_query/')
        
    return render(request, 'video_delete.html', {'video': delete})

def download_video(request,pk):
    download = Video.objects.get(pk=pk)
    file_name = f'output_video_{download.v_name}.mp4'
    file_loc = os.path.join(os.getcwd(),'Storage',f'{download.camera.pk}',file_name)
    if os.path.exists(file_loc):                                             #If the file exists it will start to send 
            with open(file_loc,'rb') as x:                                       #Opens the file and reads in binary, asigns it to the variable x
                response = HttpResponse(x.read(),content_type="video/H264")      #creates response object, passing it the video and the content type
                #Passes the object the content-dispotion telling the browser to treat it like a file attachment
                response['Content-Disposition']='inline;filename='+os.path.basename(file_name) 
                return response



    
    