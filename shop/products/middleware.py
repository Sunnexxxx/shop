from django.utils.deprecation import MiddlewareMixin
from .models import CustomUser


class CustomContextMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            is_seller = request.user.user_type == CustomUser.SELLER
        else:
            is_seller = False

        request.is_seller = is_seller
