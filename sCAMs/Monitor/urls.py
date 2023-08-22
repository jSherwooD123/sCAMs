from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("View/<int:pk>/", views.view_cam, name = "view_cam"),
    path("Manage/", views.manage, name="manage"),
    path("Manage/<int:pk>/", views.manage_cam, name = "manage_cam"),
    path("Video_query/", views.video_query, name = "video_query"),
    path("Delete_camera/<int:pk>/", views.delete_camera, name = "delete_camera"),
    path("Delete_room/<int:pk>/", views.delete_room, name = "delete_room"),
    path("Delete_video/<int:pk>/", views.delete_video, name = "delete_video"),
    path("Download_video/<int:pk>/", views.download_video, name = "download_video"),
]