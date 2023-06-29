import jwt
from django.conf import settings
from django.http import JsonResponse
import os


class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', '').split('Bearer ')[-1]
        print(token)
        secret_key = os.environ['SECRET_KEY']
        print(secret_key)
        try:
            decoded_token = jwt.decode(
                token, secret_key, algorithms=['HS256'])
            print(decoded_token)
            request.email = decoded_token['email']
            request.token = token
            print(decoded_token)
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token has expired'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Invalid token'}, status=401)

        response = self.get_response(request)
        return response
