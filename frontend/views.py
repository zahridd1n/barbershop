import datetime as dt

from django.db import OperationalError
from django.http import Http404
from django.utils import timezone
from django.views.generic import TemplateView

from barber import models


class SiteDataMixin:
    def safe_query(self, callback, default=None):
        try:
            return callback()
        except OperationalError:
            return default

    def get_site_context(self):
        contact = self.safe_query(lambda: models.Contacts.objects.first())
        socials = self.safe_query(lambda: list(models.Socials.objects.all()), [])
        return {
            "contact": contact,
            "socials": socials,
        }


class HomeView(SiteDataMixin, TemplateView):
    template_name = "frontend/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_site_context())
        primary_banner = self.safe_query(lambda: models.Banner.objects.first())
        context.update(
            {
                "primary_banner": primary_banner,
                "services": self.safe_query(lambda: list(models.Service.objects.prefetch_related("features").all()[:6]), []),
                "dopservices": self.safe_query(lambda: list(models.DopService.objects.all()[:6]), []),
                "barbers": self.safe_query(lambda: list(models.Barber.objects.all()[:4]), []),
                "reviews": self.safe_query(lambda: list(models.Review.objects.filter(status=True)[:6]), []),
                "gallery": self.safe_query(lambda: list(models.Gallery.objects.order_by("-date_upload")[:8]), []),
                "about": self.safe_query(lambda: models.About.objects.first()),
                "video": self.safe_query(lambda: models.Video.objects.order_by("-created_at").first()),
                "article": self.safe_query(lambda: models.Richtext.objects.order_by("-created_at").first()),
            }
        )
        return context


class ServicesView(SiteDataMixin, TemplateView):
    template_name = "frontend/services.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_site_context())
        context.update(
            {
                "services": self.safe_query(lambda: list(models.Service.objects.prefetch_related("features").all()), []),
                "dopservices": self.safe_query(lambda: list(models.DopService.objects.all()), []),
            }
        )
        return context


class BarbersView(SiteDataMixin, TemplateView):
    template_name = "frontend/barbers.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_site_context())
        context["barbers"] = self.safe_query(lambda: list(models.Barber.objects.all()), [])
        return context


class GalleryView(SiteDataMixin, TemplateView):
    template_name = "frontend/gallery.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_site_context())
        context["gallery"] = self.safe_query(lambda: list(models.Gallery.objects.order_by("-date_upload")), [])
        return context


class BookingView(SiteDataMixin, TemplateView):
    template_name = "frontend/booking.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_site_context())
        context.update(
            {
                "barbers": self.safe_query(lambda: list(models.Barber.objects.all()), []),
                "services": self.safe_query(lambda: list(models.Service.objects.all()), []),
                "dopservices": self.safe_query(lambda: list(models.DopService.objects.all()), []),
            }
        )
        return context


class BarberBookingsView(SiteDataMixin, TemplateView):
    template_name = "frontend/barber_bookings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_site_context())

        barber_id = self.kwargs["barber_id"]
        barber = self.safe_query(lambda: models.Barber.objects.filter(id=barber_id).first())
        if not barber:
            raise Http404("Barber topilmadi.")

        today = timezone.localdate()
        today_start = timezone.make_aware(dt.datetime.combine(today, dt.time.min))
        bookings = self.safe_query(
            lambda: list(
                models.Booking.objects.select_related("service", "dopservice", "barber")
                .filter(barber=barber, date__gte=today_start)
                .order_by("date")
            ),
            [],
        )

        grouped_bookings = []
        today_bookings_count = 0
        estimated_revenue = 0

        for booking in bookings:
            local_dt = timezone.localtime(booking.date)
            booking.local_dt = local_dt
            booking.end_dt = local_dt + booking.service_time
            booking.total_price = booking.service.price + (booking.dopservice.price if booking.dopservice else 0)
            estimated_revenue += booking.total_price

            if local_dt.date() == today:
                today_bookings_count += 1

            if not grouped_bookings or grouped_bookings[-1]["date"] != local_dt.date():
                grouped_bookings.append(
                    {
                        "date": local_dt.date(),
                        "label": local_dt.strftime("%d %B, %A"),
                        "items": [booking],
                    }
                )
            else:
                grouped_bookings[-1]["items"].append(booking)

        context.update(
            {
                "selected_barber": barber,
                "booking_groups": grouped_bookings,
                "today_bookings_count": today_bookings_count,
                "upcoming_total": len(bookings),
                "estimated_revenue": estimated_revenue,
            }
        )
        return context
