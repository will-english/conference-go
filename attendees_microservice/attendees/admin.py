from django.contrib import admin

from .models import AccountVO, Attendee, Badge


@admin.register(Attendee)
class AttendeeAdmin(admin.ModelAdmin):
    pass


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    pass


@admin.register(AccountVO)
class AccountVOAdmin(admin.ModelAdmin):
    pass
