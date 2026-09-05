from django.urls import path

from . import views

urlpatterns = [
    path("auth/login", views.login),
    path("auth/register", views.register),
    path("auth/me", views.me),
    path("auth/logout", views.logout),
    path("guests", views.list_guests),
    path("guests/ensure", views.ensure_guest),
    path("guests/<str:email>/preference", views.save_preference),
    path("guests/<str:email>/select-room", views.select_room),
    path("guests/<str:email>/services", views.save_services),
    path("services", views.list_services),
    path("rooms", views.list_rooms),
    path("rooms/<str:room_id>/devices", views.patch_devices),
    path("rooms/<str:room_id>/bind", views.bind_guest),
    path("rooms/<str:room_id>/apply-scene", views.apply_scene),
    path("rooms/<str:room_id>/photo", views.upload_photo),
    path("hotel/overview", views.overview),
    path("hotel/trend", views.trend),
    path("hotel/service-requests", views.service_requests),
    path("hotel/service-requests/<str:room_id>/complete", views.complete_service_request),
    path("hotel/simulation", views.set_simulation),
]
