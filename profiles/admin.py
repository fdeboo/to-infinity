from django.contrib import admin
from .models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'first_name',
        'last_name',
        'default_phone_num',
        'default_passport_num',
    )


admin.site.register(UserProfile, UserProfileAdmin)
