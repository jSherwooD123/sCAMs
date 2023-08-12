from django.db import models
from django.utils import timezone

class Room(models.Model):
    r_name = models.CharField(max_length = 16, unique = True)
    added_at = models.DateTimeField(auto_now_add = True)

class Camera(models.Model):
    ip_address = models.GenericIPAddressField(unique = True)
    port_num = models.IntegerField()
    c_name = models.CharField(max_length = 16, unique = True)
    active = models.BooleanField(default = False)
    last_active = models.DateTimeField(null = True)
    added_at = models.DateTimeField(auto_now_add = True)

    room = models.ForeignKey(Room, on_delete=models.CASCADE)

class Video(models.Model):
    v_name = models.TextField()
    humans_checked = models.BooleanField(default = False)
    humans_dectected = models.BooleanField(null = True)
    created_at = models.DateTimeField(auto_now_add = True)
    
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)