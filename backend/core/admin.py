from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser
from .models import Client

admin.site.register(Client)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = (
        'email', 'username', 'first_name', 'last_name',
        'phone_number', 'company_name', 'city', 'state', 'zip_code',
        'is_staff', 'is_active'
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'state')

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        (_('Personal info'), {
            'fields': (
                'first_name', 'last_name', 'phone_number',
                'company_name', 'website_url', 'address', 'city',
                'state', 'zip_code',
                'white_label_company_name', 'white_label_support_email',
                'primary_color', 'logo'
            )
        }),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2',
                'first_name', 'last_name', 'phone_number', 'company_name',
                'website_url', 'address', 'city', 'state', 'zip_code',
                'white_label_company_name', 'white_label_support_email',
                'primary_color', 'logo', 'is_staff', 'is_active'
            ),
        }),
    )

    search_fields = ('email', 'username', 'first_name', 'last_name', 'company_name')
    ordering = ('email',)