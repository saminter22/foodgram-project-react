from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User



# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
#     ...
#     list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'role', 'is_superuser', )
#     list_editable = ('role', 'is_staff', 'is_superuser', )
#     # list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
#     # search_fields = ('username', 'first_name', 'last_name', 'email')
#     # ordering = ('username',)
#     # filter_horizontal = ('groups', 'user_permissions',)

admin.site.register(User, UserAdmin)