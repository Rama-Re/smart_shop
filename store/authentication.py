from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import User


class UsernameAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # Get the username from the request (e.g., from headers or request data)
        username = request.data.get('username')

        if not username:
            return None  # No username provided

        try:
            user = User.objects.get(username=username)
            return (user, None)  # Authenticate user, no password needed
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found')

        return None

