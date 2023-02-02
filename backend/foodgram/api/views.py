#api/views.py
from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from djoser.views import UserViewSet


from dish.models import (
    Tag, 
    Ingredient, 
    Recipe, 
    RecipeIngredientAmount,
    # Subscription,
    # Favorite
    )
from .serializers import (
    CustomUserCreateSerializer,
    CustomUserSerializer,
    TagSerializer, 
    IngredientSerializer, 
    RecipeSerializer,
    # SubscriptionSerializer, 
    # SubscribeSerializer,
    # FavoriteSerializer
)

User = get_user_model()

class CustomUserCreateViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserCreateSerializer


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly, )

    # @action(method=['GET'], detail=False,)
    # def 


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )

    @action(detail=False, )
    def download_shopping_cart(self, request):
        user = request.user
        cartingredients=RecipeIngredientAmount.objects.filter(
            recipe__cart__user=user).order_by('-ingredient', '-amount').select_related(
                'ingredient','recipe').annotate(Sum('amount'))
        with open('list_of_buy.txt', 'w') as file:
            file.write('Список покупок FoodGram:\n\n')
            for item in cartingredients:
                file.write(
                    f'{item.ingredient} - {item.amount}\n'
                )
            file.write('\nУдачных покупок!\n')
        return Response (
                {'message': 'Список покупок сформирован'},
                status=status.HTTP_200_OK
                )