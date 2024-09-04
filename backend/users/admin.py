from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Subscription


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = (
        'email', 'username', 'first_name',
        'last_name', 'is_staff', 'is_active'
    )
    list_filter = (
        'email', 'username', 'is_staff', 'is_active'
    )
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'username', 'first_name',
                'last_name', 'password1', 'password2',
                'is_staff', 'is_active'
            )
        }),
    )
    search_fields = ('email', 'username')
    ordering = ('email',)


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscribed_to')
    search_fields = ('user',)


admin.site.register(User, CustomUserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
