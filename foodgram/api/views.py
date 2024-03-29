import tempfile

from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.db.models import Sum
from django.http import HttpResponse
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from djoser.views import UserViewSet

from django_filters.rest_framework import (
    DjangoFilterBackend,
    FilterSet,
    BooleanFilter,
)
from django_filters import (
    CharFilter,
)

from .mixins import CreateDestroyViewSet
from .permissions import IsAuthorOrReadOnly
from users.models import CustomUser
from dish.models import (
    Tag,
    Ingredient,
    Recipe,
    RecipeIngredientAmount,
    Subscription,
    Favorite,
    Cart
)
from .serializers import (
    CustomUserCreateSerializer,
    CustomUserSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeSerializerWrite,
    FavoriteSerializer,
    SubscribeSerializer,
)


class CustomUserCreateViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserCreateSerializer


class CustomUserViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filterset_fields = ('id', )
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    pagination_class = None

    def get_queryset(self):
        if self.request.GET.get('name'):
            name = self.request.GET.get('name')
            queryset = Ingredient.objects.filter(name__startswith=name)
            return queryset
        return Ingredient.objects.all()


class RecipeFilter(FilterSet):
    tags = CharFilter(method='filter_tags')
    is_favorited = BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = BooleanFilter(method='filter_in_cart')

    class Meta:
        model = Recipe
        fields = ('tags', )

    def filter_tags(self, queryset, name, value):
        if value:
            return queryset.filter(
                tags__slug__in=self.data.getlist('tags')).distinct()
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorite__user=user)
        return queryset

    def filter_in_cart(self, queryset, name, value):
        queryset = Recipe.objects.all()
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(cart__user=user)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    """Контроллер рецептов."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    search_fields = ('ingredients', )
    permission_classes = (IsAuthorOrReadOnly, )

    def get_queryset(self):
        if self.request.GET.get('tags'):
            queryset = Recipe.objects.all()
            tags = self.request.GET.get('tags')
            queryset = queryset.filter(tags__slug=tags)
            return queryset
        return Recipe.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipeSerializerWrite

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated, ),
    )
    def favorite(self, request, **kwargs):
        """Избранное - добавление, удаление."""
        recipe_id = self.kwargs.get('pk')
        user = self.request.user
        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, pk=recipe_id)
            try:
                Favorite.objects.create(user=user, recipe=recipe)
                serializer = FavoriteSerializer(
                    recipe,
                    context={'request': request}
                )
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            except IntegrityError:
                return Response(
                    {'message': 'Уже добавлено в Избранное'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        if request.method == 'DELETE':
            favorite = Favorite.objects.filter(user=user, recipe=recipe_id)
            if not favorite:
                return Response(
                    {'message': 'Рецепт отсутствует в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            favorite.delete()
            return Response(
                {'message': 'Убрано из Избранного'},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated, )
    )
    def shopping_cart(self, request, **kwargs):
        """Корзина - добавление, удаление."""
        recipe_id = self.kwargs.get('pk')
        user = self.request.user
        if request.method == 'POST':
            recipe = Recipe.objects.filter(pk=recipe_id)
            if not recipe:
                return Response(
                    {'message': 'Такого рецепта нет'},
                    status=status.HTTP_404_NOT_FOUND
                )
            recipe = get_object_or_404(Recipe, id=recipe_id)
            try:
                Cart.objects.create(user=user, recipe=recipe)
                serializer = FavoriteSerializer(
                    recipe,
                    context={'request': request}
                )
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response(
                    {'message': 'Уже в корзине'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        if request.method == 'DELETE':
            cart = Cart.objects.filter(user=user, recipe=recipe_id)
        if not cart:
            return Response(
                {'message': 'Рецепт отсутствует в корзине'},
                status=status.HTTP_400_BAD_REQUEST
            )
        cart.delete()
        return Response(
            {'message': 'Удалено из корзины'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=False, permission_classes=(IsAuthenticated, ))
    def download_shopping_cart(self, request):
        """Список покупок в файл."""
        user = request.user
        queryset_ingredient = RecipeIngredientAmount.objects.filter(
            recipe__cart__user=user).values(
                'ingredient__name', 'ingredient__measurement').annotate(
                    amount=Sum('amount'))
        file_name = 'buy_list.txt'
        with tempfile.TemporaryFile() as file:
            file.write('Список покупок FoodGram:\n\n')
            for item in queryset_ingredient:
                file.write(
                    f'{item["ingredient__name"]} '
                    f'({item["ingredient__measurement"]})- {item["amount"]}\n'
                )
            file.write('\nУдачных покупок!\n')
            file.close
        with open(file_name, 'r') as file:
            content_file = file.read()
            response = HttpResponse(content_file, content_type='text/plain')
            response['Content-Disposition'] = (
                r'attachment; filename={file_name}')
            file.close
        return response


class SubscriptionViewSet(viewsets.ModelViewSet):
    """Показываем текущие подписки."""
    serializer_class = SubscribeSerializer

    def get_queryset(self):
        return CustomUser.objects.filter(
            subscribers__subscriber=self.request.user)


class APISubscribe(CreateDestroyViewSet):
    """Подписка, отписка."""
    permission_classes = (IsAuthenticated, )

    def destroy(self, request, user_id):
        subscribe = Subscription.objects.filter(
            subscriber=request.user, author__id=user_id)
        if not subscribe:
            return Response(
                {'message': 'Такой подписки нет'},
                status=status.HTTP_404_NOT_FOUND
            )
        subscribe.delete()
        return Response(
            {'message': 'Отписка произошла'},
            status=status.HTTP_204_NO_CONTENT
        )

    def create(self, request, user_id):
        author = get_object_or_404(CustomUser, pk=user_id)
        user = request.user
        if not author:
            return Response(
                {'message': 'Такого автора нет'},
                status=status.HTTP_404_NOT_FOUND
            )
        if author == user:
            return Response(
                {'message': 'Подписаться на себя нельзя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            Subscription.objects.create(subscriber=request.user, author=author)
            serializer = SubscribeSerializer(
                author, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response(
                {'message': 'Подписка уже оформлена'},
                status=status.HTTP_400_BAD_REQUEST
            )
