from decimal import Decimal, InvalidOperation
from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from . import models
from . import serializers
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.utils import timezone


class ServiceView(APIView):
    def get(self, request, id=None):
        if id is not None:
            try:
                service = models.Service.objects.get(id=id)
                service_sr = serializers.ServiceSerializer(service, context={'request': request})

                return Response({
                    'success': True,
                    'message': 'success',
                    'data': service_sr.data
                })
            except models.Service.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Xizmat topilmadi'
                }, status=status.HTTP_404_NOT_FOUND)

        barber_id = request.GET.get('barber_id')
        if barber_id:
            services = models.Service.objects.filter(barber_id=barber_id)
        else:
            services = models.Service.objects.all()
        services_sr = serializers.ServiceSerializer(services, many=True, context={'request': request})

        return Response({
            'success': True,
            'message': 'success',
            'data': {
                'services': services_sr.data,
            }
        })


from rest_framework import status
class DopServiceView(APIView):
    def get(self, request, id=None):
        if id is not None:
            try:
                service = models.DopService.objects.get(id=id)
                service_sr = serializers.DopServiceSerializer(service, context={'request': request})

                return Response({
                    'success': True,
                    'message': 'success',
                    'data': service_sr.data
                })
            except models.DopService.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Xizmat topilmadi'
                }, status=status.HTTP_404_NOT_FOUND)

        barber_id = request.GET.get('barber_id')
        if barber_id:
            services = models.DopService.objects.filter(barber_id=barber_id)
        else:
            services = models.DopService.objects.all()
        services_sr = serializers.DopServiceSerializer(services, many=True, context={'request': request})

        return Response({
            'success': True,
            'message': 'success',
            'data': {
                'services': services_sr.data,
            }
        })


class Header(APIView):
    def get(self, request):
        banners = models.Banner.objects.all()
        reviews = models.Review.objects.filter(status=True)
        about = models.About.objects.all()
        gallery_asc = models.Gallery.objects.all().order_by('date_upload')
        gallery_desc = models.Gallery.objects.all().order_by('-date_upload')
        socials = models.Socials.objects.all()
        contact = models.Contacts.objects.all()
        video = models.Video.objects.all()
        maqola = models.Richtext.objects.order_by('-created_at').first()

        banners_sr = serializers.BannerSerializer(banners, many=True, context={'request': request})
        reviews_sr = serializers.ReviewSerializer(reviews, many=True, context={'request': request})
        about_sr = serializers.AboutSerializer(about, many=True, context={'request': request})
        gallery_1 = serializers.GallerySerializer(gallery_asc, many=True, context={'request': request})
        gallery_2 = serializers.GallerySerializer(gallery_desc, many=True, context={'request': request})
        contacts_sr = serializers.ContactsSerializer(contact, many=True, context={'request': request})
        socials_sr = serializers.SocialSerializer(socials, many=True, context={'request': request})
        video_sr = serializers.VideoSerializer(video, many=True, context={'request': request})
        maqola_sr = serializers.RichtextSerializer(maqola, context={'request': request})
        data = {
            'banners': banners_sr.data,
            'reviews': reviews_sr.data,
            'about': about_sr.data,
            'gallery_asc': gallery_1.data,
            'gallery_desc': gallery_2.data,
            'contact': contacts_sr.data,
            'socials': socials_sr.data,
            'video': video_sr.data,
            'maqola': maqola_sr.data,
        }

        return Response({
            'success': True,
            'message': 'success',
            'data': data
        })

    def post(self, request):
        serializer = serializers.ReviewSerializer(data=request.data)
        if serializer.is_valid():
            review = serializer.save()

            text = f"""Saytdan xabar:\n
                🆕 Yangi izoh qoldirildi
                ⭐️ Yulduzlar soni: {review.stars}
                📝 Izoh: {review.comment}
                👤 Foydalanuvchi: {review.name}

XURMATLI ADMIN, SAYTDA YANGI IZOH MAVJUD!"""

            encoded_text = urllib.parse.quote_plus(text)
            url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={ADMIN_CHAT_ID}&text={encoded_text}'
            response = requests.get(url)
            if response.status_code != 200:
                print(f"Error: {response.status_code} - {response.text}")

            return Response({
                'success': True,
                'message': '🎉 Izoh muvaffaqiyatli saqlandi! Rahmat, fikringiz biz uchun muhim!',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            'success': False,
            'message': 'Izoh saqlashda xatolik!',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class Barbers(APIView):
    def get(self, request):
        banners = models.Barber.objects.all()
        banners_sr = serializers.BarberSerializer(banners, many=True, context={'request': request})
        data = {
            'banners': banners_sr.data,
        }

        return Response({
            'success': True,
            'message': 'success',
            'data': data
        })


import pytz
from datetime import timedelta, time, datetime
from django.utils import timezone


class AvailableTimes(APIView):
    def get(self, request):
        barber_id = request.GET.get('barber_id')
        service_time_minutes = request.GET.get('service_time')
        date_param = request.GET.get('date')
        uzbekistan_tz = pytz.timezone('Asia/Tashkent')
        today = datetime.now(uzbekistan_tz).date()

        if date_param:
            try:
                requested_date = datetime.strptime(date_param, "%d-%m-%Y").date()
            except ValueError:
                requested_date = today
        else:
            requested_date = today

        try:
            barber = models.Barber.objects.get(id=barber_id)
            weekday_key = self._weekday_key(requested_date)
            availability = models.Availability.objects.filter(barber=barber, day_of_week=weekday_key).first()
            if not availability:
                return Response({
                    "success": False,
                    "message": "Barber bu kun uchun ish vaqtini sozlamagan."
                }, status=status.HTTP_404_NOT_FOUND)
        except models.Barber.DoesNotExist:
            return Response({
                "success": False,
                "message": "Barber topilmadi."
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            service_time = timedelta(minutes=int(service_time_minutes)) if service_time_minutes else timedelta(minutes=60)
        except (TypeError, ValueError):
            service_time = timedelta(minutes=60)

        available_times = self.get_available_times(
            requested_date=requested_date,
            availability=availability,
            service_time=service_time,
        )

        data = {
            "date": requested_date.strftime("%Y-%m-%d"),
            "times": available_times,
            "dates": [((requested_date + timedelta(days=i)).strftime("%d-%m-%Y")) for i in range(7)]
        }

        if not available_times:
            data["message"] = "Bu sana uchun mavjud vaqtlar mavjud emas"

        response_data = {
            "success": True,
            "message": "Success",
            "data": data
        }

        return Response(response_data)

    def _weekday_key(self, d):
        return ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'][d.weekday()]

    def get_available_times(self, requested_date, availability, service_time):
        uzbekistan_tz = pytz.timezone('Asia/Tashkent')
        step = timedelta(minutes=30)

        work_start_dt = uzbekistan_tz.localize(datetime.combine(requested_date, availability.start_time))
        work_end_dt = uzbekistan_tz.localize(datetime.combine(requested_date, availability.end_time))

        lunch_start_dt = None
        lunch_end_dt = None
        if availability.lunch_start_time and availability.lunch_end_time:
            lunch_start_dt = uzbekistan_tz.localize(datetime.combine(requested_date, availability.lunch_start_time))
            lunch_end_dt = uzbekistan_tz.localize(datetime.combine(requested_date, availability.lunch_end_time))

        now_local = timezone.now().astimezone(uzbekistan_tz)

        bookings = models.Booking.objects.filter(barber=availability.barber)
        busy_intervals = []
        for b in bookings:
            b_start = b.date.astimezone(uzbekistan_tz)
            b_end = b_start + b.service_time
            if b_start.date() == requested_date:
                busy_intervals.append((b_start, b_end))

        def overlaps(a_start, a_end, b_start, b_end):
            return a_start < b_end and b_start < a_end

        available_times = []
        cursor = work_start_dt
        while cursor + service_time <= work_end_dt:
            if requested_date == now_local.date() and cursor < now_local:
                cursor = cursor + step
                continue

            slot_end = cursor + service_time

            if lunch_start_dt and lunch_end_dt and overlaps(cursor, slot_end, lunch_start_dt, lunch_end_dt):
                cursor = cursor + step
                continue

            is_busy = False
            for b_start, b_end in busy_intervals:
                if overlaps(cursor, slot_end, b_start, b_end):
                    is_busy = True
                    break

            if not is_busy:
                available_times.append(cursor.strftime('%H:%M'))

            cursor = cursor + step

        return available_times


from pytz import timezone as pytz_timezone

uzbekistan_tz = pytz_timezone('Asia/Tashkent')
from config.settings import BOT_TOKEN, ADMIN_CHAT_ID
import requests
import urllib.parse
import locale

try:
    locale.setlocale(locale.LC_TIME, 'uz_UZ.UTF-8')
except locale.Error:
    pass


class BookingView(APIView):
    def post(self, request):
        barber_id = request.data.get('barber_id')
        service_id = request.data.get('service_id')
        date_str = request.data.get('date')
        customer_name = request.data.get('customer_name')
        customer_phone = request.data.get('customer_phone')
        service_time_minutes = request.data.get('service_time')
        dopservice_id = request.data.get('dopservice_id')
        raw_price = request.data.get('price')

        uzbekistan_tz = pytz.timezone('Asia/Tashkent')

        try:
            local_datetime = uzbekistan_tz.localize(datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S"))
            if local_datetime < timezone.now().astimezone(uzbekistan_tz):
                return Response({'success': False, 'message': 'O\'tib ketgan vaqtni tanlab bo\'lmaydi.'}, status=status.HTTP_400_BAD_REQUEST)

            if local_datetime.minute % 30 != 0 or local_datetime.second != 0:
                return Response({'success': False, 'message': 'Vaqt 30 daqiqalik oraliqda bo\'lishi kerak.'}, status=status.HTTP_400_BAD_REQUEST)

            utc_datetime = local_datetime.astimezone(pytz.utc)
            service_time = timedelta(minutes=int(service_time_minutes))

            barber = get_object_or_404(models.Barber, id=barber_id)
            service = get_object_or_404(models.Service, id=service_id)

            availability = models.Availability.objects.filter(barber=barber, day_of_week=['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'][local_datetime.date().weekday()]).first()
            if not availability:
                return Response({'success': False, 'message': 'Bu kun uchun barber ish vaqti belgilanmagan.'}, status=status.HTTP_400_BAD_REQUEST)

            work_start_dt = uzbekistan_tz.localize(datetime.combine(local_datetime.date(), availability.start_time))
            work_end_dt = uzbekistan_tz.localize(datetime.combine(local_datetime.date(), availability.end_time))
            if local_datetime < work_start_dt or (local_datetime + service_time) > work_end_dt:
                return Response({'success': False, 'message': 'Tanlangan vaqt barber ish vaqtiga to\'g\'ri kelmaydi.'}, status=status.HTTP_400_BAD_REQUEST)

            if availability.lunch_start_time and availability.lunch_end_time:
                lunch_start_dt = uzbekistan_tz.localize(datetime.combine(local_datetime.date(), availability.lunch_start_time))
                lunch_end_dt = uzbekistan_tz.localize(datetime.combine(local_datetime.date(), availability.lunch_end_time))
                if (local_datetime < lunch_end_dt) and (lunch_start_dt < (local_datetime + service_time)):
                    return Response({'success': False, 'message': 'Tanlangan vaqt tushlik vaqtiga to\'g\'ri keladi.'}, status=status.HTTP_400_BAD_REQUEST)

            existing = models.Booking.objects.filter(barber=barber)
            for b in existing:
                b_start = b.date.astimezone(uzbekistan_tz)
                b_end = b_start + b.service_time
                if b_start.date() != local_datetime.date():
                    continue
                if local_datetime < b_end and b_start < (local_datetime + service_time):
                    return Response({'success': False, 'message': 'Bu vaqt band qilingan.'}, status=status.HTTP_400_BAD_REQUEST)

            dopservice = None
            dopservice_name = None
            if dopservice_id:
                dopservice = get_object_or_404(models.DopService, id=dopservice_id)
                dopservice_name = dopservice.name

            calculated_price = service.price + (dopservice.price if dopservice else 0)
            try:
                price = Decimal(str(raw_price).replace(' ', '').replace(',', '')) if raw_price not in (None, '') else calculated_price
            except (InvalidOperation, AttributeError):
                price = calculated_price

            models.Booking.objects.create(
                barber_id=barber.id,
                service_id=service.id,
                dopservice_id=dopservice.id if dopservice else None,
                date=utc_datetime,
                customer_name=customer_name,
                customer_phone=customer_phone,
                service_time=service_time,
                price=price,
            )

            month_name = local_datetime.strftime('%B')
            day = local_datetime.strftime('%d')
            time_value = local_datetime.strftime('%H:%M')

            dop_line = "➕ Qo'shimcha xizmat: " + dopservice_name if dopservice_name else ''

            text = f"""Saytdan xabar:\n
                🆕 Yangi buyurtma
                💈 Barber: {barber.name}
                💼 Xizmat: {service.name}
                {dop_line}
                ⏳ Xizmat davomiyligi: {service_time_minutes} minut
                📅 Sana: {day} - {month_name}
                ⏰ Vaqt: {time_value}
                👤 Buyurtmachi ismi: {customer_name}
                📞 Telefon: {customer_phone}
                {dop_line}

                Summa: {price}

XURMATLI ADMIN, SAYTDA YANGI BUYURTMA MAVJUD!"""

            encoded_text = urllib.parse.quote_plus(text)
            chat_id = barber.telegram_id if barber.telegram_id else ADMIN_CHAT_ID
            url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={chat_id}&text={encoded_text}'
            response = requests.get(url)
            if response.status_code != 200:
                print(f"Error: {response.status_code} - {response.text}")

            return Response({'success': True, 'message': 'Booking created successfully!'}, status=status.HTTP_201_CREATED)

        except ValueError:
            return Response({'success': False, 'message': 'Sana formatini to\'g\'ri kiritmadingiz.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ══════════════════════════════════════════════════════════
#  DASHBOARD API VIEWS
# ══════════════════════════════════════════════════════════

from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .permissions import IsApprovedBarber, IsOwnerBarber
from django.db import transaction


class BarberDashboardProfileView(APIView):
    """Barber o'z profilini ko'rish va tahrirlash"""
    permission_classes = [IsAuthenticated, IsApprovedBarber]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        barber = request.user.barber
        sr = serializers.BarberProfileUpdateSerializer(barber, context={'request': request})
        return Response({'success': True, 'data': sr.data})

    def put(self, request):
        barber = request.user.barber
        sr = serializers.BarberProfileUpdateSerializer(barber, data=request.data, partial=True, context={'request': request})
        if sr.is_valid():
            sr.save()
            return Response({'success': True, 'message': 'Profil yangilandi!', 'data': sr.data})
        return Response({'success': False, 'errors': sr.errors}, status=status.HTTP_400_BAD_REQUEST)


class BarberDashboardServiceView(APIView):
    """Barber o'z xizmatlarini ko'rish va qo'shish"""
    permission_classes = [IsAuthenticated, IsApprovedBarber]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        services = models.Service.objects.filter(barber=request.user.barber)
        sr = serializers.ServiceCreateUpdateSerializer(services, many=True, context={'request': request})
        return Response({'success': True, 'data': sr.data})

    def post(self, request):
        if not getattr(request.user, 'barber', None):
            return Response({'success': False, 'message': 'Barber profile topilmadi.'}, status=status.HTTP_400_BAD_REQUEST)
        sr = serializers.ServiceCreateUpdateSerializer(data=request.data, context={'request': request})
        if sr.is_valid():
            try:
                sr.save(barber=request.user.barber)
                return Response({'success': True, 'message': 'Xizmat qo\'shildi!', 'data': sr.data}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'success': False, 'message': f'Xizmatni saqlashda xatolik: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'success': False, 'errors': sr.errors}, status=status.HTTP_400_BAD_REQUEST)


class BarberDashboardServiceDetailView(APIView):
    """Xizmatni tahrirlash va o'chirish"""
    permission_classes = [IsAuthenticated, IsApprovedBarber]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self, pk, user):
        service = get_object_or_404(models.Service, pk=pk, barber=user.barber)
        return service

    def put(self, request, pk):
        service = self.get_object(pk, request.user)
        sr = serializers.ServiceCreateUpdateSerializer(service, data=request.data, partial=True, context={'request': request})
        if sr.is_valid():
            try:
                sr.save()
                return Response({'success': True, 'message': 'Xizmat yangilandi!', 'data': sr.data})
            except Exception as e:
                return Response({'success': False, 'message': f'Xizmatni yangilashda xatolik: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'success': False, 'errors': sr.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        service = self.get_object(pk, request.user)
        service.delete()
        return Response({'success': True, 'message': 'Xizmat o\'chirildi!'})


class BarberDashboardDopServiceView(APIView):
    """Barber qo'shimcha xizmatlarini ko'rish va qo'shish"""
    permission_classes = [IsAuthenticated, IsApprovedBarber]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        services = models.DopService.objects.filter(barber=request.user.barber)
        sr = serializers.DopServiceCreateUpdateSerializer(services, many=True, context={'request': request})
        return Response({'success': True, 'data': sr.data})

    def post(self, request):
        if not getattr(request.user, 'barber', None):
            return Response({'success': False, 'message': 'Barber profile topilmadi.'}, status=status.HTTP_400_BAD_REQUEST)
        sr = serializers.DopServiceCreateUpdateSerializer(data=request.data, context={'request': request})
        if sr.is_valid():
            try:
                sr.save(barber=request.user.barber)
                return Response({'success': True, 'message': 'Qo\'shimcha xizmat qo\'shildi!', 'data': sr.data}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'success': False, 'message': f'Qo\'shimcha xizmatni saqlashda xatolik: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'success': False, 'errors': sr.errors}, status=status.HTTP_400_BAD_REQUEST)


class BarberDashboardDopServiceDetailView(APIView):
    """Qo'shimcha xizmatni tahrirlash va o'chirish"""
    permission_classes = [IsAuthenticated, IsApprovedBarber]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self, pk, user):
        return get_object_or_404(models.DopService, pk=pk, barber=user.barber)

    def put(self, request, pk):
        service = self.get_object(pk, request.user)
        sr = serializers.DopServiceCreateUpdateSerializer(service, data=request.data, partial=True, context={'request': request})
        if sr.is_valid():
            try:
                sr.save()
                return Response({'success': True, 'message': 'Xizmat yangilandi!', 'data': sr.data})
            except Exception as e:
                return Response({'success': False, 'message': f'Xizmatni yangilashda xatolik: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'success': False, 'errors': sr.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        service = self.get_object(pk, request.user)
        service.delete()
        return Response({'success': True, 'message': 'Xizmat o\'chirildi!'})


class BarberDashboardGalleryView(APIView):
    """Portfolio rasmlarini ko'rish va yuklash"""
    permission_classes = [IsAuthenticated, IsApprovedBarber]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        gallery = models.Gallery.objects.filter(barber=request.user.barber).order_by('-date_upload')
        sr = serializers.GalleryCreateSerializer(gallery, many=True, context={'request': request})
        return Response({'success': True, 'data': sr.data})

    def post(self, request):
        images = request.FILES.getlist('image')
        if not images:
            images = [request.FILES.get('image')]

        created = []
        for img in images:
            if img:
                gallery_item = models.Gallery.objects.create(
                    barber=request.user.barber,
                    image=img,
                )
                created.append(serializers.GalleryCreateSerializer(gallery_item, context={'request': request}).data)

        return Response({
            'success': True,
            'message': f'{len(created)} ta rasm yuklandi!',
            'data': created
        }, status=status.HTTP_201_CREATED)


class BarberDashboardGalleryDeleteView(APIView):
    """Portfolio rasmini o'chirish"""
    permission_classes = [IsAuthenticated, IsApprovedBarber]

    def delete(self, request, pk):
        gallery_item = get_object_or_404(models.Gallery, pk=pk, barber=request.user.barber)
        gallery_item.image.delete(save=False)
        gallery_item.delete()
        return Response({'success': True, 'message': 'Rasm o\'chirildi!'})


class BarberDashboardAvailabilityView(APIView):
    """Barber ish vaqti/tushlik vaqtini boshqarish"""
    permission_classes = [IsAuthenticated, IsApprovedBarber]

    def get(self, request):
        qs = models.Availability.objects.filter(barber=request.user.barber)
        sr = serializers.AvailabilitySerializer(qs, many=True)
        return Response({'success': True, 'data': sr.data})

    @transaction.atomic
    def put(self, request):
        items = request.data
        if not isinstance(items, list):
            return Response({'success': False, 'message': 'Noto\'g\'ri format. List yuboring.'}, status=status.HTTP_400_BAD_REQUEST)

        allowed = {'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'}
        created_or_updated = []

        for item in items:
            if not isinstance(item, dict):
                return Response({'success': False, 'message': 'Har bir element object bo\'lishi kerak.'}, status=status.HTTP_400_BAD_REQUEST)

            day = item.get('day_of_week')
            if day not in allowed:
                return Response({'success': False, 'message': 'day_of_week noto\'g\'ri.'}, status=status.HTTP_400_BAD_REQUEST)

            obj = models.Availability.objects.filter(barber=request.user.barber, day_of_week=day).first()

            if obj is None:
                if not item.get('start_time') or not item.get('end_time'):
                    return Response(
                        {'success': False, 'message': 'Yangi kun uchun start_time va end_time majburiy.'},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                sr = serializers.AvailabilitySerializer(data=item)
                if not sr.is_valid():
                    return Response({'success': False, 'errors': sr.errors}, status=status.HTTP_400_BAD_REQUEST)
                created = sr.save(barber=request.user.barber, day_of_week=day)
                created_or_updated.append(created)
            else:
                sr = serializers.AvailabilitySerializer(obj, data=item, partial=True)
                if not sr.is_valid():
                    return Response({'success': False, 'errors': sr.errors}, status=status.HTTP_400_BAD_REQUEST)
                updated = sr.save(barber=request.user.barber, day_of_week=day)
                created_or_updated.append(updated)

        out = serializers.AvailabilitySerializer(created_or_updated, many=True)
        return Response({'success': True, 'message': 'Ish vaqti saqlandi!', 'data': out.data})


class BarberDetailPublicView(APIView):
    """Sayt foydalanuvchilari uchun bitta barberning to'liq ma'lumoti"""

    def get(self, request, pk):
        barber = get_object_or_404(models.Barber, pk=pk, is_approved=True)
        sr = serializers.BarberDetailPublicSerializer(barber, context={'request': request})
        return Response({'success': True, 'data': sr.data})


class BarberDashboardBookingsView(APIView):
    """Barber dashboard - kutilayotgan buyurtmalar (pending)"""
    permission_classes = [IsAuthenticated, IsApprovedBarber]

    def get(self, request):
        qs = models.Booking.objects.filter(barber=request.user.barber, status='pending').order_by('-date')
        sr = serializers.BookingDetailSerializer(qs, many=True)
        return Response({'success': True, 'data': sr.data})


class BarberDashboardBookingActionView(APIView):
    """Barber dashboard - buyurtmani tasdiqlash/rad etish"""
    permission_classes = [IsAuthenticated, IsApprovedBarber]

    def post(self, request, booking_id):
        action = request.data.get('action')  # 'approve' or 'reject'
        reason = request.data.get('rejection_reason', '')

        if action not in ['approve', 'reject']:
            return Response({'success': False, 'message': 'Noto\'g\'ri action. approve yoki reject bo\'lishi kerak.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            booking = models.Booking.objects.get(id=booking_id, barber=request.user.barber, status='pending')
        except models.Booking.DoesNotExist:
            return Response({'success': False, 'message': 'Buyurtma topilmadi yoki allaqachon ko\'rib chiqilgan.'}, status=status.HTTP_404_NOT_FOUND)

        if action == 'approve':
            booking.status = 'approved'
            booking.rejection_reason = None
            booking.save()
            return Response({'success': True, 'message': 'Buyurtma tasdiqlandi!'})
        else:  # reject
            if not reason:
                return Response({'success': False, 'message': 'Rad etish sababini kiriting.'}, status=status.HTTP_400_BAD_REQUEST)
            booking.status = 'rejected'
            booking.rejection_reason = reason
            booking.save()
            return Response({'success': True, 'message': 'Buyurtma rad etildi.'})


class BarberDashboardArchiveView(APIView):
    """Barber dashboard - arxiv (approved/rejected)"""
    permission_classes = [IsAuthenticated, IsApprovedBarber]

    def get(self, request):
        qs = models.Booking.objects.filter(barber=request.user.barber).exclude(status='pending').order_by('-date')
        sr = serializers.BookingDetailSerializer(qs, many=True)
        return Response({'success': True, 'data': sr.data})
