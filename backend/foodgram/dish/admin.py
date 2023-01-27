from django.contrib import admin

# Register your models here.
from .models import (
    Ingredient, 
    Tag, 
    Recipe, 
    RecipeIngredientAmount)


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


# class RecipeIngredientAmountAdmin(admin.ModelAdmin):
#     list_display = (
#         'ingredient',
#         'recipe',
#         'amount',
#     )
#     ordering = ('ingredient', 'recipe')




# admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
# admin.site.register(RecipeIngredientAmount, RecipeIngredientAmountAdmin)
# admin.site.register(RecipeIngredientAmount)

