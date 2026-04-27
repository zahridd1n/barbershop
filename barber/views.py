from decimal import Decimal, InvalidOperation
from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from . import models
from . import serializers
from rest_framework.decorators import api_view, permission_classes, authentication_classes


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
        service_time = request.GET.get('service_time')
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
            availability = models.Availability.objects.filter(barber=barber).first()
            if not availability:
                return Response({
                    "success": False,
                    "message": "Barber uchun ish vaqti topilmadi."
                }, status=status.HTTP_404_NOT_FOUND)
        except models.Barber.DoesNotExist:
            return Response({
                "success": False,
                "message": "Barber topilmadi."
            }, status=status.HTTP_404_NOT_FOUND)

        booked_dates = models.Booking.objects.filter(barber=barber).values_list('date', flat=True)
        booked_dates = [datetime.combine(date.date(), date.time()).replace(tzinfo=None) for date in booked_dates]
        all_possible_dates = self.get_all_possible_dates(requested_date, availability.start_time, availability.end_time)
        available_times = self.get_available_times(requested_date, all_possible_dates, booked_dates, availability)

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

    def get_all_possible_dates(self, start_date, start_time, end_time):
        start_time_str = start_time.isoformat()
        end_time_str = end_time.isoformat()
        start_time = time.fromisoformat(start_time_str)
        end_time = time.fromisoformat(end_time_str)

        interval = timedelta(minutes=60)
        times = {}

        for i in range(5):
            current_date = start_date + timedelta(days=i)
            current_time = start_time
            if current_date not in times:
                times[current_date] = []
            while current_time <= end_time:
                times[current_date].append(current_time)
                current_time = (datetime.combine(current_date, current_time) + interval).time()

        return times

    def get_available_times(self, requested_date, all_possible_dates, booked_dates, availability):
        available_times = []
        times = all_possible_dates.get(requested_date, [])
        uzbekistan_tz = pytz.timezone('Asia/Tashkent')
        lunch_start = datetime.combine(requested_date, availability.lunch_start_time).time()
        lunch_end = datetime.combine(requested_date, availability.lunch_end_time).time()

        booked_times = []
        for b in models.Booking.objects.filter(barber=availability.barber):
            b_date_uzt = b.date.astimezone(uzbekistan_tz)
            booked_time_end = (b_date_uzt + b.service_time).time()
            if b_date_uzt.date() == requested_date:
                booked_times.append((b_date_uzt.time(), booked_time_end))

        for t in times:
            if lunch_start <= t <= lunch_end:
                continue

            is_time_free = True
            for start, end in booked_times:
                if start <= t < end:
                    is_time_free = False
                    break

            if is_time_free:
                available_times.append(t.strftime("%H:%M"))

        print(f"Final available times: {available_times}")
        return available_times


from pytz import timezone

uzbekistan_tz = timezone('Asia/Tashkent')
from config.settings import BOT_TOKEN, ADMIN_CHAT_ID
import requests
import urllib.parse
import locale

locale.setlocale(locale.LC_TIME, 'uz_UZ.UTF-8')


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
            utc_datetime = local_datetime.astimezone(pytz.utc)
            service_time = timedelta(minutes=int(service_time_minutes))

            barber = get_object_or_404(models.Barber, id=barber_id)
            service = get_object_or_404(models.Service, id=service_id)

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
