import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

try:
    from aiogram.types import Update
    from aiogram import Bot
    AIOGRAM_AVAILABLE = True
except ImportError:
    AIOGRAM_AVAILABLE = False
    Update = None
    Bot = None

from django.conf import settings

@csrf_exempt
def telegram_webhook(request):
    if not AIOGRAM_AVAILABLE:
        return JsonResponse({"status": "error", "message": "Aiogram not installed"}, status=500)
    
    if request.method == "POST":
        try:
            # Parse the incoming JSON update from Telegram
            update_data = json.loads(request.body.decode('utf-8'))
            print(">>> KELGAN XABAR TELEGRAMDAN:", update_data)
            update = Update(**update_data)
            
            from .bot import dp
            # Har bir so'rov uchun yangi Bot instansiyasini (yangi sessiya bilan) yaratamiz
            # Bu Django WSGI da "Session is attached to different loop" xatosini oldini oladi
            import asyncio
            
            async def process():
                async with Bot(token=settings.BOT_TOKEN) as bot:
                    await dp.feed_update(bot=bot, update=update)
            
            asyncio.run(process())
            
            return JsonResponse({"status": "ok"})
        except Exception as e:
            print(f"Error processing update: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    
    return JsonResponse({"status": "invalid request"}, status=405)
