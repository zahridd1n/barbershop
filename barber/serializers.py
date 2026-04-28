from rest_framework import serializers
from . import models


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Feature
        fields = ('name',)

class ServiceSerializer(serializers.ModelSerializer):
    get_features = serializers.SerializerMethodField()

    class Meta:
        model = models.Service
        fields = ('id','title', 'description', 'name', 'price', 'time', 'get_features')

    def get_get_features(self, obj):
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
        fields = ['barber', 'service', 'dopservice', 'date', 'customer_name', 'customer_phone', 'service_time', 'price']

class RichtextSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Richtext
        fields = ['content']


# ── DASHBOARD SERIALIZERS ────────────────────────────────

class BarberProfileUpdateSerializer(serializers.ModelSerializer):
    """Barber profilini tahrirlash uchun"""
    class Meta:
        model = models.Barber
        fields = ['id', 'name', 'experience', 'age', 'description', 'image']
        extra_kwargs = {
            'image': {'required': False},
        }


class ServiceCreateUpdateSerializer(serializers.ModelSerializer):
    """Xizmat qo'shish/tahrirlash uchun"""
    barber = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = models.Service
        fields = ['id', 'title', 'name', 'description', 'price', 'time', 'image', 'barber']
        extra_kwargs = {
            'image': {'required': False},
        }


class DopServiceCreateUpdateSerializer(serializers.ModelSerializer):
    """Qo'shimcha xizmat qo'shish/tahrirlash uchun"""
    barber = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = models.DopService
        fields = ['id', 'title', 'name', 'description', 'price', 'time', 'image', 'barber']
        extra_kwargs = {
            'image': {'required': False},
        }


class GalleryCreateSerializer(serializers.ModelSerializer):
    """Gallery rasm yuklash uchun"""
    class Meta:
        model = models.Gallery
        fields = ['id', 'image', 'date_upload']
        read_only_fields = ['date_upload']


class BookingDetailSerializer(serializers.ModelSerializer):
    """Buyurtma batafsil ko'rsatish (nested)"""
    service_name = serializers.CharField(source='service.name', read_only=True)
    service_price = serializers.DecimalField(source='service.price', max_digits=50, decimal_places=2, read_only=True)
    dopservice_name = serializers.CharField(source='dopservice.name', read_only=True, default=None)
    dopservice_price = serializers.DecimalField(source='dopservice.price', max_digits=50, decimal_places=2, read_only=True, default=None)
    barber_name = serializers.CharField(source='barber.name', read_only=True)

    class Meta:
        model = models.Booking
        fields = [
            'id', 'date', 'customer_name', 'customer_phone',
            'service_time', 'price',
            'service_name', 'service_price',
            'dopservice_name', 'dopservice_price',
            'barber_name', 'status', 'rejection_reason',
        ]


class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Availability
        fields = ['day_of_week', 'start_time', 'end_time', 'lunch_start_time', 'lunch_end_time']


class BarberDetailPublicSerializer(serializers.ModelSerializer):
    """Public sahifa uchun barber batafsil ma'lumoti"""
    services = ServiceSerializer(many=True, read_only=True)
    dopservices = DopServiceSerializer(many=True, read_only=True)
    gallery = GallerySerializer(many=True, read_only=True, source='gallery.all')

    class Meta:
        model = models.Barber
        fields = [
            'id', 'name', 'experience', 'age', 'description', 'image',
            'services', 'dopservices', 'gallery',
        ]
