import asyncio
from django.core.management.base import BaseCommand
from django.conf import settings
from aiogram import Bot

class Command(BaseCommand):
    help = 'Sets the Telegram Webhook using SITE_URL from settings'

    def handle(self, *args, **options):
        if not settings.SITE_URL:
            self.stdout.write(self.style.ERROR('SITE_URL is not set in config/settings.py. It must be an HTTPS URL (e.g., https://yourdomain.com)'))
            return
        
        # Olib tashlash oxiridagi sleshni (slash) agar bo'lsa
        site_url = settings.SITE_URL.rstrip('/')
        webhook_url = f"{site_url}/bot/webhook/"
        
        self.stdout.write(f"Setting webhook to: {webhook_url}")
        
        async def _set_webhook():
            async with Bot(token=settings.BOT_TOKEN) as bot:
                result = await bot.set_webhook(url=webhook_url)
                me = await bot.get_me()
                return result, me

        try:
            result, me = asyncio.run(_set_webhook())
            if result:
                self.stdout.write(self.style.SUCCESS(f'Successfully set webhook for bot @{me.username}'))
            else:
                self.stdout.write(self.style.ERROR('Failed to set webhook.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error setting webhook: {e}'))
