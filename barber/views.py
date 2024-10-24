from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from . import models
from . import serializers
from rest_framework.decorators import api_view, permission_classes, authentication_classes



class ServiceView(APIView):
    def get(self, request, id=None):
        # Agar ID berilgan bo'lsa, faqat o'sha ID ga mos xizmatni olish
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

        # ID berilmagan bo'lsa, barcha xizmatlarni olish
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
        # Agar ID berilgan bo'lsa, faqat o'sha ID ga mos xizmatni olish
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

        # ID berilmagan bo'lsa, barcha xizmatlarni olish
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
        # Ma'lumotlarni olish
        banners = models.Banner.objects.all()
        reviews = models.Review.objects.filter(status=True)
        about = models.About.objects.all()
        gallery_asc = models.Gallery.objects.all().order_by('date_upload')
        gallery_desc = models.Gallery.objects.all().order_by('-date_upload')
        socials = models.Socials.objects.all()
        contact = models.Contacts.objects.all()
        video = models.Video.objects.all()
        maqola = models.Richtext.objects.order_by('-created_at').first() #Faqat oxirgi yozilgan maqolani chiqaradi

        # Serializatsiya qilish
        banners_sr = serializers.BannerSerializer(banners, many=True, context={'request': request})
        reviews_sr = serializers.ReviewSerializer(reviews, many=True, context={'request': request})
        about_sr = serializers.AboutSerializer(about, many=True, context={'request': request})
        gallery_1 = serializers.GallerySerializer(gallery_asc, many=True, context={'request': request})
        gallery_2 = serializers.GallerySerializer(gallery_desc, many=True, context={'request': request})
        contacts_sr = serializers.ContactsSerializer(contact, many=True, context={'request': request})
        socials_sr = serializers.SocialSerializer(socials, many=True, context={'request': request})
        video_sr = serializers.VideoSerializer(video, many=True,context={'request': request})
        maqola_sr = serializers.RichtextSerializer(maqola, context={'request': request})
        # Hammasini data ichiga joylash
        data = {
            'banners': banners_sr.data,
            'reviews': reviews_sr.data,
            'about': about_sr.data,
            'gallery_asc': gallery_1.data,
            'gallery_desc': gallery_2.data,
            'contact': contacts_sr.data,  # .data dan foydalanildi
            'socials': socials_sr.data,  # .data dan foydalanildi
            'video': video_sr.data, # .data dan foydalanild
            'maqola': maqola_sr.data, # .data dan foydalanildi
        }

        return Response({
            'success': True,
            'message': 'success',
            'data': data
        })

    def post(self, request):
        serializer = serializers.ReviewSerializer(data=request.data)
        if serializer.is_valid():
            # Izohni saqlash
            review = serializer.save()

            # Xabar matnini tayyorlash
            text = f"""Saytdan xabar:\n
                🆕 Yangi izoh qoldirildi
                ⭐️ Yulduzlar soni: {review.stars}  
                📝 Izoh: {review.comment}  
                👤 Foydalanuvchi: {review.name}  

XURMATLI ADMIN, SAYTDA YANGI IZOH MAVJUD!"""

            encoded_text = urllib.parse.quote_plus(text)

            # Xabarni Telegram guruhiga yuborish
            url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={GROUP_CHAT_ID}&text={encoded_text}'
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
        # Ma'lumotlarni olish
        banners = models.Barber.objects.all()
       
        # Serializatsiya qilish
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


from datetime import timedelta, time,datetime
from django.utils import timezone

class AvailableTimes(APIView):  # AvailableTimes klassi, APIView dan meros oladi.
    def get(self, request):  # GET so'rovini qaytaruvchi metod.
        barber_id = request.GET.get('barber_id')  # So'rovdan barber_id ni olish.
        service_time = request.GET.get('service_time')  # So'rovdan xizmat vaqtini olish (masalan, 30 minut).
        date_param = request.GET.get('date')  # So'rovdan sanani olish.
        uzbekistan_tz = pytz.timezone('Asia/Tashkent')  # O'zbekiston vaqti uchun timezone.

        # Hozirgi vaqtni O'zbekiston vaqti bilan olish.
        today = datetime.now(uzbekistan_tz).date()  # Lokal vaqtni olish.

        # Sanani o'qish yoki bugungi sanani olish.
        if date_param:  # Agar sana parametri berilgan bo'lsa.
            try:
                requested_date = datetime.strptime(date_param, "%d-%m-%Y").date()  # Sana formatini o'qish.
            except ValueError:
                requested_date = today  # Agar format noto'g'ri bo'lsa, bugungi sanani olish.
        else:
            requested_date = today  # Sana berilmagan bo'lsa, bugungi sanani olish.

        # Barber va ish vaqtini olish.
        try:
            barber = models.Barber.objects.get(id=barber_id)  # Barberni bazadan olish.
            availability = models.Availability.objects.filter(barber=barber).first()  # Barberning ish vaqtini olish.
            if not availability:  # Agar ish vaqti topilmasa.
                return Response({
                    "success": False,
                    "message": "Barber uchun ish vaqti topilmadi."  # Xato xabari qaytarish.
                }, status=status.HTTP_404_NOT_FOUND)  # 404 status kodi.
        except models.Barber.DoesNotExist:  # Barber topilmasa.
            return Response({
                "success": False,
                "message": "Barber topilmadi."  # Xato xabari qaytarish.
            }, status=status.HTTP_404_NOT_FOUND)  # 404 status kodi.

        # Band qilingan sanalarni olish.
        booked_dates = models.Booking.objects.filter(barber=barber).values_list('date', flat=True)  # Band qilingan sanalarni olish.
        booked_dates = [datetime.combine(date.date(), date.time()).replace(tzinfo=None) for date in booked_dates]  # Band sanalarini datetime formatiga o'tkazish.

        # Vaqtni olish.
        all_possible_dates = self.get_all_possible_dates(requested_date, availability.start_time, availability.end_time)  # Mavjud vaqtlarni olish.

        # Funksiya bo'sh vaqtlarni olish.
        available_times = self.get_available_times(requested_date, all_possible_dates, booked_dates, availability)  # Bo'sh vaqtlarni olish.

        # Ma'lumotlarni tayyorlash.
        data = {
            "date": requested_date.strftime("%Y-%m-%d"),  # So'rovdagi sanani YYYY-MM-DD formatida saqlash.
            "times": available_times,  # Mavjud vaqtlar.
            "dates": [(
                (requested_date + timedelta(days=i)).strftime("%d-%m-%Y")  # Keyingi 7 kunlarni olish.
            ) for i in range(7)]
        }

        # Agar bo'sh vaqtlar mavjud bo'lmasa, xabar berish.
        if not available_times:  # Agar bo'sh vaqtlar mavjud bo'lmasa.
            data["message"] = "Bu sana uchun mavjud vaqtlar mavjud emas"  # Xabar qo'shish.

        # Success javobini qaytarish.
        response_data = {
            "success": True,  # Javob muvaffaqiyatli.
            "message": "Success",  # Muvaffaqiyat xabari.
            "data": data  # Ma'lumotlar.
        }

        return Response(response_data)  # Javobni qaytarish.

    def get_all_possible_dates(self, start_date, start_time, end_time):  # Mavjud sanalarni olish.
        # `start_time` va `end_time` vaqtlarini str formatiga o'tkazish.
        start_time_str = start_time.isoformat()  # `str` formatida.
        end_time_str = end_time.isoformat()  # `str` formatida.

        # `fromisoformat` dan foydalanish.
        start_time = time.fromisoformat(start_time_str)  # Ish vaqtini vaqt formatiga o'tkazish.
        end_time = time.fromisoformat(end_time_str)  # Ish tugash vaqtini vaqt formatiga o'tkazish.

        interval = timedelta(minutes=60)  # 15 daqiqalik interval.
        times = {}  # Mavjud vaqtlar uchun lug'at.

        for i in range(5):  # Bugun va keyingi 4 kun.
            current_date = start_date + timedelta(days=i)  # Joriy sanani hisoblash.
            current_time = start_time  # Joriy vaqtni boshlash.
            if current_date not in times:  # Agar sana lug'atda bo'lmasa.
                times[current_date] = []  # Yangi sana uchun ro'yxat yaratish.
            while current_time <= end_time:  # Ish vaqti davomida.
                times[current_date].append(current_time)  # Joriy vaqti qo'shish.
                current_time = (datetime.combine(current_date, current_time) + interval).time()  # Keyingi vaqti hisoblash.

        return times  # Mavjud vaqtlarni qaytarish.

    def get_available_times(self, requested_date, all_possible_dates, booked_dates, availability):
        available_times = []
        times = all_possible_dates.get(requested_date, [])

        uzbekistan_tz = pytz.timezone('Asia/Tashkent')

        # Lunch vaqti olish
        lunch_start = datetime.combine(requested_date, availability.lunch_start_time).time()
        lunch_end = datetime.combine(requested_date, availability.lunch_end_time).time()

        booked_times = []
        for b in models.Booking.objects.filter(barber=availability.barber):
            b_date_uzt = b.date.astimezone(uzbekistan_tz)
            booked_time_end = (b_date_uzt + b.service_time).time()
            if b_date_uzt.date() == requested_date:
                booked_times.append((b_date_uzt.time(), booked_time_end))

        # Mavjud vaqtlarni tekshirish
        for t in times:
            combined_datetime = datetime.combine(requested_date, t)

            # Agar hozirgi vaqt tushadigan lunch vaqtida bo'lsa, o'tkazib yuborish
            if lunch_start <= t <= lunch_end:
                continue

            # Band vaqtlarni tekshirish
            is_time_free = True

            for start, end in booked_times:
                # Agar hozirgi vaqt band vaqt orasida bo'lsa
                if start <= t < end:
                    is_time_free = False
                    break

            # Agar vaqt bo'sh bo'lsa, uni qo'shish
            if is_time_free:
                available_times.append(t.strftime("%H:%M"))

        print(f"Final available times: {available_times}")
        return available_times


from pytz import timezone

uzbekistan_tz = timezone('Asia/Tashkent')
# local_datetime = uzbekistan_tz.localize(datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S"))


from config.settings import BOT_TOKEN,GROUP_CHAT_ID
import requests
import urllib.parse
import locale

locale.setlocale(locale.LC_TIME, 'uz_UZ.UTF-8')  # O'zbek tiliga o'tish

class BookingView(APIView):
    def post(self, request):
        # Ma'lumotlarni olish
        barber_id = request.data.get('barber_id')
        service_id = request.data.get('service_id')
        date_str = request.data.get('date')  # YYYY-MM-DDTHH:MM:SS formatida
        customer_name = request.data.get('customer_name')
        customer_phone = request.data.get('customer_phone')
        service_time_minutes = request.data.get('service_time')  # Masalan, 45 minut
        dopservice_id = request.data.get('dopservice_id') 
        price = request.data.get('price')  # Dopservis ID
         # Dopservis ID

        # Vaqtni O'zbekiston vaqti bilan olish
        uzbekistan_tz = pytz.timezone('Asia/Tashkent')

        try:
            # Vaqtni O'zbekiston vaqti sifatida oling
            local_datetime = uzbekistan_tz.localize(datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S"))

            # UTC ga o'tkazing
            utc_datetime = local_datetime.astimezone(pytz.utc)

            # Service vaqtini 'timedelta' ga aylantiring
            service_time = timedelta(minutes=int(service_time_minutes)) 

            # Barber va xizmat nomlarini olish
            barber = get_object_or_404(models.Barber, id=barber_id)
            service = get_object_or_404(models.Service, id=service_id)

            # Dopservisni olish (agar tanlangan bo'lsa)
            dopservice_name = None
            if dopservice_id:
                dopservice = get_object_or_404(models.DopService, id=dopservice_id)
                dopservice_name = dopservice.name

            # Yangi buyurtma yaratish
            booking = models.Booking(
                barber_id=barber.id,
                service_id=service.id,
                dopservice_id=dopservice.id if dopservice_id else None,  # Dopservis ID si qo'shiladi
                date=utc_datetime,  # UTC vaqtini saqlaymiz
                customer_name=customer_name,
                customer_phone=customer_phone,
                service_time=service_time,
            )
            booking.save()

            # Oyning nomini olish
            month_name = local_datetime.strftime('%B')  # Oyning to'liq nomi (o'zbek tilida)
            day = local_datetime.strftime('%d')  # Kun
            time = local_datetime.strftime('%H:%M')  # Vaqt

            # Xabar matni
            text = f"""Saytdan xabar:\n
                🆕 Yangi buyurtma
                💈 Barber: {barber.name} 
                💼 Xizmat: {service.name}
                {'➕ Qo\'shimcha xizmat: ' + dopservice_name if dopservice_name else ''}
                ⏳ Xizmat davomiyligi: {service_time_minutes} minut
                📅 Sana: {day} - {month_name}
                ⏰ Vaqt: {time}
                👤 Buyurtmachi ismi: {customer_name}
                📞 Telefon: {customer_phone}
                {'➕ Qo\'shimcha xizmat: ' + dopservice_name if dopservice_name else ''}

                Summa: {price}

XURMATLI ADMIN, SAYTDA YANGI BUYURTMA MAVJUD!"""

            # Matnni URLga mos tarzda kodlash
            encoded_text = urllib.parse.quote_plus(text)

            # Xabarni Telegram guruhiga yuborish
            url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={GROUP_CHAT_ID}&text={encoded_text}'
            response = requests.get(url)
            if response.status_code != 200:
                print(f"Error: {response.status_code} - {response.text}")

            return Response({'success': True, 'message': 'Booking created successfully!'}, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({'success': False, 'message': 'Sana formatini to\'g\'ri kiritmadingiz.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        