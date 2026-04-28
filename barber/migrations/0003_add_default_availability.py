# Generated migration for existing barbers to have default availability

from django.db import migrations
from datetime import time


def create_default_availability_for_existing_barbers(apps, schema_editor):
    Barber = apps.get_model('barber', 'Barber')
    Availability = apps.get_model('barber', 'Availability')

    default_start = time(8, 0)   # 08:00
    default_end = time(17, 0)   # 17:00
    lunch_start = time(12, 0)   # 12:00
    lunch_end = time(13, 0)     # 13:00

    DAY_CHOICES = [
        ('mon', 'Mon'),
        ('tue', 'Tue'),
        ('wed', 'Wed'),
        ('thu', 'Thu'),
        ('fri', 'Fri'),
        ('sat', 'Sat'),
        ('sun', 'Sun'),
    ]

    for barber in Barber.objects.all():
        for day_key, _ in DAY_CHOICES:
            Availability.objects.get_or_create(
                barber=barber,
                day_of_week=day_key,
                defaults={
                    'start_time': default_start,
                    'end_time': default_end,
                    'lunch_start_time': lunch_start,
                    'lunch_end_time': lunch_end,
                }
            )


class Migration(migrations.Migration):

    dependencies = [
        ('barber', '0002_barber_is_approved_barber_telegram_id_barber_user_and_more'),
    ]

    operations = [
        migrations.RunPython(create_default_availability_for_existing_barbers),
    ]
