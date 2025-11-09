from django.shortcuts import redirect
from django.urls import reverse

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if not request.user.is_authenticated:
            # Allow access to login, logout, admin, and static files
            if not (path.startswith(reverse('login')) or
                    path.startswith('/admin/') or
                    path.startswith('/static/') or
                    path.startswith(reverse('register'))):
                return redirect('login')
        return self.get_response(request)
