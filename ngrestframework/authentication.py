# -*- coding:utf-8 -*-
# create_time: 2018/12/13 14:19
# __author__ = 'brad'

from rest_framework.authentication import SessionAuthentication


class SessionNoCsrftokenAuthentication(SessionAuthentication):
    def authenticate(self, request):
        """
        Returns a `User` if the request session currently has a logged in user.
        Otherwise returns `None`.
        """

        # Get the session-based user from the underlying HttpRequest object
        user = getattr(request._request, 'user', None)

        # Unauthenticated, CSRF validation not required
        if not user or not user.is_active:
            return None

        # CSRF passed with authenticated user
        return (user, None)

