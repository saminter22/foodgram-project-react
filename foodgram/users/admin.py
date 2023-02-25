from django.contrib import admin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'is_staff',
        'count_fields'
    )
    readonly_fields = ('count_fields',)
    ordering = ('username', )
    list_filter = (
        'username',
        'email',
    )
    search_fields = ('username', 'email', )

    def count_fields(self, obj):
        return obj.favorite.count()
