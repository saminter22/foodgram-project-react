from django.contrib import admin

# Register your models here.
from .models import (
    Ingredient, 
    Tag, 
    Recipe, 
    RecipeIngredientAmount,
    Subscription,
    Favorite,
    Cart
    )


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


# class TagInLine(admin.TabularInline):
#     model = Tag
#     list_display = (
#         # 'recipe',
#         'name',
#         )


class IngredientInLine(admin.TabularInline):
    model = RecipeIngredientAmount
    list_display = (
        'recipe',
        'ingredient',
        'amount',
        'measurement'
        )

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        # 'text',
        'cooking_time',
        'pub_date',
    )
    list_select_related = True
    inlines = [ 
        IngredientInLine,
        # TagInLine,
    ]
    ordering = ('name', '-pub_date')
    list_editable = ('cooking_time', )
    list_filter = ('name', 'author', 'cooking_time', )
    search_fields = ('name', )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('subscriber', 'author',)
    list_filter = ('subscriber', 'author', )
    search_fields = ('subscriber', 'author', )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', )
    list_filter = ('user', 'recipe', )
    search_fields = ('user', 'recipe', )


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', )
    list_filter = ('user', 'recipe', )
    search_fields = ('user', 'recipe', )



# class RecipeIngredientAmountAdmin(admin.ModelAdmin):
#     list_display = (
#         'ingredient',
#         'recipe',
#         'amount',
#     )
#     ordering = ('ingredient', 'recipe')




# admin.site.register(Ingredient, IngredientAdmin)
# admin.site.register(Tag, TagAdmin)
# admin.site.register(Recipe, RecipeAdmin)
# admin.site.register(RecipeIngredientAmount, RecipeIngredientAmountAdmin)
# admin.site.register(RecipeIngredientAmount)
# admin.site.register(Subscription, SubscriptionAdmin)


