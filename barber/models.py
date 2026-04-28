from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from django.core.exceptions import ValidationError
import re
from django.core.validators import RegexValidator 

from django.contrib.auth.models import User

class Service(models.Model):
    barber = models.ForeignKey('Barber', on_delete=models.CASCADE, related_name='services', verbose_name="Sartarosh", null=True)
    title = models.TextField(verbose_name="Sarlavhani kiriting", blank=True)
    name = models.CharField(max_length=200, verbose_name="Xizmat nomi")
    description = models.TextField(verbose_name="Tavsifi", blank=True)
    price = models.DecimalField(max_digits=50, decimal_places=2, verbose_name="Narxi")
    time = models.CharField(max_length=150, verbose_name="Vaqt (soat:dakika)", default="60 minut")
    image = models.ImageField(upload_to="services", verbose_name="Xizmat rasmini kiriting", blank=True, null=True)

    class Meta:
        verbose_name = "Xizmat"
        verbose_name_plural = "Xizmatlar"

    def __str__(self):
        return self.name

    @property
    def get_features(self):
        return Feature.objects.filter(service=self.id)


class Feature(models.Model):
    name = models.CharField(max_length=200, verbose_name="Xususiyat nomi")
    service = models.ManyToManyField(Service, related_name='features', verbose_name="Xizmat")

    class Meta:
        verbose_name = "Xizmat qoshimchasi"
        verbose_name_plural = "Xizmatlar xususiyatlari"

    def __str__(self):
        return self.name


class DopService(models.Model):
    barber = models.ForeignKey('Barber', on_delete=models.CASCADE, related_name='dopservices', verbose_name="Sartarosh", null=True)
    title = models.TextField(verbose_name="Sarlavhani kiriting", blank=True)
    name = models.CharField(max_length=200, verbose_name="Xizmat nomi")
    description = models.TextField(verbose_name="Tavsifi", blank=True)
    price = models.DecimalField(max_digits=50, decimal_places=2, verbose_name="Narxi")
    time = models.CharField(max_length=150, verbose_name="Vaqt (soat:dakika)", default="30 minut")
    image = models.ImageField(upload_to="services", verbose_name="Xizmat rasmini kiriting", blank=True, null=True)

    class Meta:
        verbose_name = "Qo'shimcha xizmat"
        verbose_name_plural = "Qo'shimcha Xizmatlar"

    def __str__(self):
        return self.name


class Review(models.Model):
    name = models.CharField(max_length=255, verbose_name="Foydalanuvchi nomi")
    comment = models.TextField(verbose_name="Izoh")
    stars = models.PositiveIntegerField(verbose_name="Yulduzlar soni")
    status = models.BooleanField(default=False, verbose_name="Status")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Izoh"
        verbose_name_plural = "Izohlar"


class Banner(models.Model):
    image = models.ImageField(upload_to='banners/', verbose_name="Birinchi banner rasmi", blank=True, null=True)
    image1 = models.ImageField(upload_to='banners/', verbose_name="Ikkinchi banner rasmi", blank=True, null=True)

    class Meta:
        verbose_name = "Banner"
        verbose_name_plural = "Bannlar"


class About(models.Model):
    image = models.ImageField(upload_to='about/', verbose_name="Rasm")
    text = RichTextUploadingField(verbose_name="Matn")

    class Meta:
        verbose_name = "Haqida"
        verbose_name_plural = "Haqida"


class Gallery(models.Model):
    barber = models.ForeignKey('Barber', on_delete=models.CASCADE, related_name='gallery', null=True, blank=True, verbose_name="Sartarosh")
    image = models.ImageField(upload_to='gallery/', verbose_name="Rasm")
    date_upload = models.DateTimeField(auto_now_add=True, verbose_name="Yuklangan sana")

    class Meta:
        verbose_name = "Galereya"
        verbose_name_plural = "Galereyalar"


class Barber(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Django foydalanuvchi")
    telegram_id = models.CharField(max_length=50, blank=True, null=True, unique=True, verbose_name="Telegram ID")
    is_approved = models.BooleanField(default=False, verbose_name="Tasdiqlangan")
    name = models.CharField(max_length=255, verbose_name="Ism")
    experience = models.PositiveIntegerField(verbose_name="Tajriba yillari")
    description = models.TextField(verbose_name="Tavsif")
    image = models.ImageField(upload_to='barbers/', verbose_name="Rasm", null=True, blank=True)
    age = models.PositiveIntegerField(verbose_name="Yoshi")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Sartarosh"
        verbose_name_plural = "Sartaroshlar"


class Socials(models.Model):
    name = models.CharField(max_length=100, verbose_name="Sosyal Medya Adı")
    icon = models.ImageField(upload_to="icon/photos", verbose_name="Social media iconini kiriting png holatda")
    link = models.CharField(max_length=200, verbose_name="Akkaunt linkini kiriting")

    class Meta:
        verbose_name = "Ijtimoiy tarmoq"
        verbose_name_plural = "Ijtimoiy tarmoqlar"

    def __str__(self):
        return self.name


class Contacts(models.Model):
    phone = models.CharField(max_length=100, verbose_name="Telefon")
    address = models.CharField(max_length=100, verbose_name="Manzil")
    latitude = models.CharField(max_length=100, verbose_name="Kenglik")
    longitude = models.CharField(max_length=700, verbose_name="Uzunlik")
    logo = models.ImageField(upload_to="logo/photos", verbose_name="Logotip")

    class Meta:
        verbose_name = "Aloqa"
        verbose_name_plural = "Aloqa"

    def __str__(self):
        return self.address


class Video(models.Model):
    title = models.CharField(max_length=200, verbose_name="Sarlavha")
    link = models.CharField(max_length=200, verbose_name="Havola")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    image = models.ImageField(upload_to="header/image", verbose_name="Rasm")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Video"
        verbose_name_plural = "Videolar"


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('approved', 'Tasdiqlangan'),
        ('rejected', 'Rad etilgan'),
    ]

    barber = models.ForeignKey(Barber, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    dopservice = models.ForeignKey(DopService, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField()
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=15)
    service_time = models.DurationField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True, null=True, verbose_name="Rad etish sababi")

    def __str__(self):
        return f"Appointment for {self.customer_name} with {self.barber.name} on {self.date}"


class Availability(models.Model):
    barber = models.ForeignKey(Barber, on_delete=models.CASCADE)
    DAY_CHOICES = [
        ('mon', 'Mon'),
        ('tue', 'Tue'),
        ('wed', 'Wed'),
        ('thu', 'Thu'),
        ('fri', 'Fri'),
        ('sat', 'Sat'),
        ('sun', 'Sun'),
    ]

    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    lunch_start_time = models.TimeField(null=True, blank=True)
    lunch_end_time = models.TimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['barber', 'day_of_week'], name='uniq_barber_day_availability'),
        ]

    def __str__(self):
        return f"{self.barber.name}'s availability on {self.day_of_week}"


# ── SIGNALS ────────────────────────────────────────────────
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import time


@receiver(post_save, sender=Barber)
def create_default_availability(sender, instance, created, **kwargs):
    if created:
        default_start = time(8, 0)   # 08:00
        default_end = time(17, 0)   # 17:00
        lunch_start = time(12, 0)   # 12:00
        lunch_end = time(13, 0)     # 13:00

        for day_key, _ in Availability.DAY_CHOICES:
            Availability.objects.get_or_create(
                barber=instance,
                day_of_week=day_key,
                defaults={
                    'start_time': default_start,
                    'end_time': default_end,
                    'lunch_start_time': lunch_start,
                    'lunch_end_time': lunch_end,
                }
            )


class Richtext(models.Model):
    content = RichTextUploadingField(verbose_name="Maqola", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
