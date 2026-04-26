from django.urls import path

from . import views

app_name = "frontend"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("services/", views.ServicesView.as_view(), name="services"),
    path("barbers/", views.BarbersView.as_view(), name="barbers"),
    path("gallery/", views.GalleryView.as_view(), name="gallery"),
    path("booking/", views.BookingView.as_view(), name="booking"),
    path("barber-room/<int:barber_id>/", views.BarberBookingsView.as_view(), name="barber-room"),
]
