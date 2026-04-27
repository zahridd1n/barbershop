from django.contrib import admin
from .models import *

class BarberOwnedAdmin(admin.ModelAdmin):
    """Har bir barber faqat o'z ma'lumotlarini ko'radi va tahrirlaydi"""
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        barber = Barber.objects.filter(user=request.user).first()
        if barber:
            return qs.filter(barber=barber)
        return qs.none()

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and not getattr(obj, 'barber', None):
            barber = Barber.objects.filter(user=request.user).first()
            if barber:
                obj.barber = barber
        super().save_model(request, obj, form, change)

admin.site.register(Review)
admin.site.register(About)
admin.site.register(Banner)
admin.site.register(Barber)
admin.site.register(Feature)
admin.site.register(Video)
admin.site.register(Richtext)

@admin.register(Gallery)
class GalleryAdmin(BarberOwnedAdmin):
    list_display = ('id', 'barber', 'date_upload')

@admin.register(Booking)
class BookingAdmin(BarberOwnedAdmin):
    list_display = ('customer_name', 'barber', 'service', 'date', 'price')
    list_filter = ('date', 'barber')

@admin.register(Availability)
class AvailabilityAdmin(BarberOwnedAdmin):
    list_display = ('barber', 'day_of_week', 'start_time', 'end_time')

@admin.register(Contacts)
class ContactsAdmin(admin.ModelAdmin):
    list_display = ('phone', 'address', 'latitude', 'longitude', 'logo')

@admin.register(Socials)
class SocialsAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'link')

@admin.register(Service)
class ServiceAdmin(BarberOwnedAdmin):
    list_display = ('name', 'barber', 'price', 'time')
    search_fields = ('name', 'description')

@admin.register(DopService)
class DopServiceAdmin(BarberOwnedAdmin):
    list_display = ('name', 'barber', 'price', 'time')
    search_fields = ('name', 'description')

