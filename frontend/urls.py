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

    # Barber Detail (public)
    path("barber/<int:barber_id>/", views.BarberDetailView.as_view(), name="barber-detail"),

    # Barber Dashboard
    path("dashboard/login/", views.DashboardLoginView.as_view(), name="dashboard-login"),
    path("dashboard/logout/", views.DashboardLogoutView.as_view(), name="dashboard-logout"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("dashboard/services/", views.DashboardServicesView.as_view(), name="dashboard-services"),
    path("dashboard/gallery/", views.DashboardGalleryView.as_view(), name="dashboard-gallery"),
    path("dashboard/bookings/", views.DashboardBookingsView.as_view(), name="dashboard-bookings"),
]
