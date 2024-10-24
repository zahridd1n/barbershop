from rest_framework import serializers
from . import models

class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Feature
        fields = ('name',)
        
class ServiceSerializer(serializers.ModelSerializer):
    get_features = serializers.SerializerMethodField()  # Yangi maydon sifatida belgilash

    class Meta:
        model = models.Service
        fields = ('id','title', 'description', 'name', 'price', 'time', 'image','get_features')  # To'g'ri formatda

    def get_get_features(self, obj):
        # Xususiyatlarni olish va faqat name qiymatini qaytarish
        return [feature.name for feature in obj.get_features]


class DopServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DopService
        fields = ('id','title', 'description', 'name', 'price', 'time', 'image') 


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Review
        fields = "__all__"

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Banner
        fields = "__all__"

class AboutSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.About
        fields = "__all__"

class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Gallery
        fields = "__all__"

class BarberSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Barber
        fields = "__all__"


class ContactsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Contacts
        fields = ['id', 'phone', 'address', 'latitude', 'longitude', 'logo']

class SocialSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Socials
        fields = ['name', 'link', 'icon']


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Video
        fields = ['id', 'title', 'link','image']


class BarberSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Barber
        fields = ['id', 'name', 'experience', 'description', 'image', 'age']


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Booking
        fields = ['barber', 'service', 'dopservice', 'date', 'customer_name', 'customer_phone']

class RichtextSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Richtext
        fields = ['content']