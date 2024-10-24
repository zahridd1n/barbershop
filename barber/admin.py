from django.contrib import admin
from .models import *

admin.site.register(Review)
admin.site.register(About)
admin.site.register(Banner)
admin.site.register(Gallery)
admin.site.register(Barber)
admin.site.register(Feature)
admin.site.register(Availability)
admin.site.register(Booking)
admin.site.register(Video)
admin.site.register(Richtext)





@admin.register(Contacts)
class ContactsAdmin(admin.ModelAdmin):
    list_display = ('phone', 'address', 'latitude', 'longitude', 'logo')


@admin.register(Socials)
class SocialsAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'link')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'time')  # Maydonlar to'g'ri kiritildi
    search_fields = ('name', 'description')  # Nom va tavsif bo'yicha qidiruv

@admin.register(DopService)
class DopServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'time')  # Maydonlar to'g'ri kiritildi
    search_fields = ('name', 'description')  # Nom va tavsif bo'yicha qidiruv


