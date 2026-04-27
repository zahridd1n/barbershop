from django.urls import path
from . import views

app_name = 'barber'

urlpatterns = [
    path('headers/', views.Header.as_view()),
    path('services/', views.ServiceView.as_view()),
    path('dopservices/', views.DopServiceView.as_view()),
    path('availability/', views.AvailableTimes.as_view(), name='availability'),
    path('barbers/', views.Barbers.as_view(), name='availability'),
    path('bookings/', views.BookingView.as_view(), name='booking-create'),

    # Dashboard API (autentifikatsiya talab qilinadi)
    path('dashboard/profile/', views.BarberDashboardProfileView.as_view(), name='dashboard-profile-api'),
    path('dashboard/services/', views.BarberDashboardServiceView.as_view(), name='dashboard-services-api'),
    path('dashboard/services/<int:pk>/', views.BarberDashboardServiceDetailView.as_view(), name='dashboard-service-detail-api'),
    path('dashboard/dopservices/', views.BarberDashboardDopServiceView.as_view(), name='dashboard-dopservices-api'),
    path('dashboard/dopservices/<int:pk>/', views.BarberDashboardDopServiceDetailView.as_view(), name='dashboard-dopservice-detail-api'),
    path('dashboard/gallery/', views.BarberDashboardGalleryView.as_view(), name='dashboard-gallery-api'),
    path('dashboard/gallery/<int:pk>/', views.BarberDashboardGalleryDeleteView.as_view(), name='dashboard-gallery-delete-api'),
    path('dashboard/bookings/', views.BarberDashboardBookingsView.as_view(), name='dashboard-bookings-api'),

    # Public API
    path('barber/<int:pk>/', views.BarberDetailPublicView.as_view(), name='barber-detail-api'),
]
