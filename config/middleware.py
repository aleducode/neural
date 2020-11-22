"""Middleware to ensure active membership."""

# Django
from django.shortcuts import redirect
from django.urls import reverse


class MembershipMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """Code to be executed for each request before the view is called."""
        if not request.user.is_anonymous:
            if not request.user.is_staff:
                user = request.user
                if not user.is_verified or not user.is_client:
                    trusted_domains = [
                        reverse('users:pending'),
                        reverse('users:logout')
                        ]
                    # Except some urls
                    if request.path not in trusted_domains:
                        return redirect('users:pending')
        response = self.get_response(request)
        return response
