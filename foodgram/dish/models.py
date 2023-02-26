from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from colorfield.fields import ColorField
from users.models import CustomUser


class Ingredient(models.Model):
    name = models.CharField(max_length=255,
                            verbose_name='Название ингредиента')
    measurement = models.CharField(max_length=100,
                                   verbose_name='Единицы измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} ({self.measurement})'


class Tag(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название тега')
    slug = models.SlugField(max_length=100, unique=True)
    color = ColorField(default='#CCCCCC', verbose_name='Цвет')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=254, verbose_name='Название блюда')
    author = models.ForeignKey(CustomUser,
                               on_delete=models.CASCADE,
                               related_name='recipes',
                               verbose_name='Автор рецепта')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации')
    text = models.TextField(verbose_name='Описание рецепта')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(1),
                    MaxValueValidator(5000)]
    )
    image = models.ImageField(upload_to='images/', verbose_name="Фото блюда")
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredientAmount',
                                         related_name='recipes',
                                         verbose_name='Ингредиенты')
    tags = models.ManyToManyField(Tag,
                                  verbose_name='Теги',
                                  related_name='recipes',
                                  )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date', )

    def __str__(self):
        return self.name


class RecipeIngredientAmount(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   verbose_name='Название ингредиента',
                                   related_name='baserecipes')
    amount = models.SmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(1, message='Минимальное значение 1'),
            MaxValueValidator(30000, message='Максимальное значение 30000')
        ]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'ingredient'],
                                    name='recipe_ingredient')
        ]
        verbose_name = 'Ингредиент в количестве'
        verbose_name_plural = 'Количество ингредиентов'

    def __str__(self):
        return f'{self.recipe}, {self.ingredient}, {self.amount}'


class Subscription(models.Model):
    subscriber = models.ForeignKey(CustomUser,
                                   on_delete=models.CASCADE,
                                   related_name='authors',
                                   verbose_name='Подписчик')
    author = models.ForeignKey(CustomUser,
                               on_delete=models.CASCADE,
                               related_name='subscribers',
                               verbose_name='Автор')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['subscriber', 'author'],
                                    name='subscriber_author')
        ]
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'


class Favorite(models.Model):
    user = models.ForeignKey(CustomUser,
                             on_delete=models.CASCADE,
                             related_name='favorite',
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='favorite',
                               verbose_name='Любимый рецепт')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='fav_user_recipe')
        ]
        verbose_name = 'Любимый рецепт'
        verbose_name_plural = 'Любимые рецепты'


class Cart(models.Model):
    user = models.ForeignKey(CustomUser,
                             on_delete=models.CASCADE,
                             related_name='cart',
                             verbose_name='В корзине')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='cart',
                               verbose_name='Находится в корзине')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='cart_user_recipe')
        ]
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
