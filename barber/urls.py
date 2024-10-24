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

]
