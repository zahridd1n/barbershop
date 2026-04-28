import datetime as dt

from django.contrib.auth import authenticate, login, logout
from django.db import OperationalError
from django.http import Http404
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

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
                "barbers": self.safe_query(lambda: list(models.Barber.objects.filter(is_approved=True)[:4]), []),
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
        context["barbers"] = self.safe_query(lambda: list(models.Barber.objects.filter(is_approved=True)), [])
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
                "barbers": self.safe_query(lambda: list(models.Barber.objects.filter(is_approved=True)), []),
                "services": [],
                "dopservices": [],
                "preselected_barber_id": self.request.GET.get("barber_id", ""),
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


# ══════════════════════════════════════════════════════════
#  BARBER DETAIL PAGE (PUBLIC)
# ══════════════════════════════════════════════════════════

class BarberDetailView(SiteDataMixin, TemplateView):
    template_name = "frontend/barber_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_site_context())

        barber_id = self.kwargs["barber_id"]
        barber = self.safe_query(
            lambda: models.Barber.objects.filter(id=barber_id, is_approved=True).first()
        )
        if not barber:
            raise Http404("Sartarosh topilmadi.")

        services = self.safe_query(
            lambda: list(models.Service.objects.filter(barber=barber)), []
        )
        dopservices = self.safe_query(
            lambda: list(models.DopService.objects.filter(barber=barber)), []
        )
        gallery = self.safe_query(
            lambda: list(models.Gallery.objects.filter(barber=barber).order_by("-date_upload")), []
        )

        context.update({
            "barber": barber,
            "services": services,
            "dopservices": dopservices,
            "gallery": gallery,
        })
        return context


# ══════════════════════════════════════════════════════════
#  BARBER DASHBOARD (Frontend Views)
# ══════════════════════════════════════════════════════════

class DashboardLoginView(SiteDataMixin, View):
    """Dashboard login sahifasi"""

    def get(self, request):
        if request.user.is_authenticated and hasattr(request.user, 'barber'):
            return redirect('frontend:dashboard')
        context = self.get_site_context()
        return render(request, 'frontend/dashboard_login.html', context)

    def post(self, request):
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        context = self.get_site_context()

        if user is not None:
            if hasattr(user, 'barber') and user.barber.is_approved:
                login(request, user)
                return redirect('frontend:dashboard')
            else:
                context['error'] = 'Sizning profilingiz hali tasdiqlanmagan.'
        else:
            context['error'] = 'Login yoki parol noto\'g\'ri.'

        context['username'] = username
        return render(request, 'frontend/dashboard_login.html', context)


class DashboardLogoutView(View):
    """Dashboard logout"""

    def get(self, request):
        logout(request)
        return redirect('frontend:dashboard-login')

    def post(self, request):
        logout(request)
        return redirect('frontend:dashboard-login')


class BarberDashboardMixin(LoginRequiredMixin, SiteDataMixin):
    """Dashboard uchun umumiy mixin — login talab qiladi va barber ekanligini tekshiradi"""
    login_url = '/dashboard/login/'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not hasattr(request.user, 'barber'):
            return redirect('frontend:dashboard-login')
        return super().dispatch(request, *args, **kwargs)


class DashboardView(BarberDashboardMixin, TemplateView):
    """Asosiy dashboard — profil tahrirlash"""
    template_name = "frontend/dashboard_profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_site_context())
        context['barber'] = self.request.user.barber
        return context


class DashboardServicesView(BarberDashboardMixin, TemplateView):
    """Xizmatlar boshqaruvi"""
    template_name = "frontend/dashboard_services.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_site_context())
        context['barber'] = self.request.user.barber
        return context


class DashboardGalleryView(BarberDashboardMixin, TemplateView):
    """Portfolio boshqaruvi"""
    template_name = "frontend/dashboard_gallery.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_site_context())
        context['barber'] = self.request.user.barber
        return context


class DashboardBookingsView(BarberDashboardMixin, TemplateView):
    """Buyurtmalar tarixi"""
    template_name = "frontend/dashboard_bookings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_site_context())
        barber = self.request.user.barber
        context['barber'] = barber

        today = timezone.localdate()
        today_start = timezone.make_aware(dt.datetime.combine(today, dt.time.min))
        bookings = list(
            models.Booking.objects.select_related("service", "dopservice")
            .filter(barber=barber, date__gte=today_start)
            .order_by("date")
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
                grouped_bookings.append({
                    "date": local_dt.date(),
                    "label": local_dt.strftime("%d %B, %A"),
                    "items": [booking],
                })
            else:
                grouped_bookings[-1]["items"].append(booking)

        context.update({
            "booking_groups": grouped_bookings,
            "today_bookings_count": today_bookings_count,
            "upcoming_total": len(bookings),
            "estimated_revenue": estimated_revenue,
        })
        return context


class DashboardAvailabilityView(BarberDashboardMixin, TemplateView):
    """Ish vaqti va tushlik vaqtini sozlash"""
    template_name = "frontend/dashboard_availability.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_site_context())
        context['barber'] = self.request.user.barber
        return context
