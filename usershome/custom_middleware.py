# custom_middleware.py
from django.contrib.auth import logout


class BlockUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        user = request.user
        if user.is_authenticated and user.is_active == False:
            logout(request)

        return response
