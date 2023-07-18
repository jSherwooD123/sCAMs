from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("View/<int:pk>/", views.view_cam, name = "view_cam"),
    path("Manage/", views.manage, name="manage"),
    path("Manage/<int:pk>/", views.manage_cam, name = "manage_cam"),
    path("Delete_camera/<int:pk>/", views.delete_camera, name = "delete_camera"),
    path("Delete_room/<int:pk>/", views.delete_room, name = "delete_room")
]