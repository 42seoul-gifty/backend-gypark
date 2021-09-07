from dj_rest_auth.jwt_auth import (
    set_jwt_access_cookie,
    set_jwt_refresh_cookie
)


class CookieAutoRefreshToken:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return self.process_response(request, response)

    def process_response(self, request, response):
        if not hasattr(request.user, 'refreshed_tokens'):
            return response

        tokens = request.user.refreshed_tokens
        set_jwt_access_cookie(response, tokens['access'])

        refresh_token = tokens.get('refresh')
        if refresh_token:
            set_jwt_refresh_cookie(response, refresh_token)
        return response
