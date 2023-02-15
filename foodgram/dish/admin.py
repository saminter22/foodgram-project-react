from django.contrib import admin
# from django.db.models import Count

# from .models import CustomUser
from .models import (Ingredient, Tag, Recipe, RecipeIngredientAmount,
                     Subscription, Favorite, Cart)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement',
    )
    ordering = ('name', )
    list_filter = (
        'name',
        'measurement',
    )
    search_fields = ('name', )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
        'color',
    )
    prepopulated_fields = {'slug': ('name', )}
    ordering = ('name', )
    list_editable = ('color', )
    list_filter = ('name', )


class IngredientInLine(admin.TabularInline):
    model = RecipeIngredientAmount
    list_display = ('recipe', 'ingredient', 'amount', 'measurement')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'count_fields',
    )
    readonly_fields = ('count_fields',)

    list_select_related = True
    inlines = [
        IngredientInLine,
    ]
    ordering = ('name', '-pub_date')
    # list_editable = ('name', )
    list_filter = (
        'name',
        'author',
        'tags',
    )
    search_fields = ('name', )

    def count_fields(self, obj):
        return obj.favorite.count()


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'subscriber',
        'author',
    )
    list_filter = (
        'subscriber',
        'author',
    )
    search_fields = (
        'subscriber',
        'author',
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
    list_filter = (
        'user',
        'recipe',
    )
    search_fields = (
        'user',
        'recipe',
    )


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
    list_filter = (
        'user',
        'recipe',
    )
    search_fields = (
        'user',
        'recipe',
    )
