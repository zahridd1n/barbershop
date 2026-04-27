from django.urls import path
from .views import telegram_webhook

app_name = 'tgbot'

urlpatterns = [
    path('webhook/', telegram_webhook, name='webhook'),
]
