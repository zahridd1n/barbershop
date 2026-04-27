from rest_framework.permissions import BasePermission


class IsApprovedBarber(BasePermission):
    """Faqat tasdiqlangan sartaroshlar uchun ruxsat"""

    message = "Siz tasdiqlangan sartarosh emassiz."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, 'barber')
            and request.user.barber.is_approved
        )


class IsOwnerBarber(BasePermission):
    """Faqat o'z ma'lumotlarini tahrirlashi mumkin"""

    message = "Bu ma'lumot sizga tegishli emas."

    def has_object_permission(self, request, view, obj):
        if not hasattr(request.user, 'barber'):
            return False
        return obj.barber == request.user.barber
