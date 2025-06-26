from django.urls import path, include
from users.apis import TelegramAuthApi

auth_patterns = [
    path('telegram/', TelegramAuthApi.as_view(), name='telegram-auth'),
]

urlpatterns = [
    path('auth/', include((auth_patterns, 'auth'))),
]