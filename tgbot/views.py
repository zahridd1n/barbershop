import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from aiogram.types import Update
from aiogram import Bot
from django.conf import settings
from .bot import dp

@csrf_exempt
async def telegram_webhook(request):
    if request.method == "POST":
        try:
            # Parse the incoming JSON update from Telegram
            update_data = json.loads(request.body.decode('utf-8'))
            print(">>> KELGAN XABAR TELEGRAMDAN:", update_data)
            update = Update(**update_data)
            
            # Har bir so'rov uchun yangi Bot instansiyasini (yangi sessiya bilan) yaratamiz
            # Bu Django WSGI da "Session is attached to different loop" xatosini oldini oladi
            async with Bot(token=settings.BOT_TOKEN) as bot:
                # Feed the update into the aiogram dispatcher
                await dp.feed_update(bot=bot, update=update)
            
            return JsonResponse({"status": "ok"})
        except Exception as e:
            print(f"Error processing update: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    
    return JsonResponse({"status": "invalid request"}, status=405)
