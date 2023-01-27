#users/views.py
from djoser.views import UserViewSet

from .serializers import CustomUserCreateSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreateViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserCreateSerializer

