from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("Manage/", views.manage, name="manage"),
    path("Delete_camera/<int:pk>/", views.delete_camera, name = "delete_camera"),
    path("Delete_room/<int:pk>/", views.delete_room, name = "delete_room")
]