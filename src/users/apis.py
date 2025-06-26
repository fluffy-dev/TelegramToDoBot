from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from users.services import get_or_create_user_by_telegram_id


class TelegramAuthApi(APIView):
    """API for authenticating users via Telegram."""
    permission_classes = (AllowAny,)

    class InputSerializer(serializers.Serializer):
        telegram_id = serializers.IntegerField()
        username = serializers.CharField(required=False, allow_blank=True)

    def post(self, request):
        """
        Authenticate a user and return an auth token.

        Creates a new user if one doesn't exist for the given telegram_id.
        """
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        _, token = get_or_create_user_by_telegram_id(**serializer.validated_data)

        return Response({'token': token.key}, status=status.HTTP_200_OK)