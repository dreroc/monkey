import logging
from http import HTTPStatus

from flask import Response, make_response, request
from flask.typing import ResponseValue
from flask_login import current_user
from flask_security.views import login

from monkey_island.cc.flask_utils import AbstractResource, responses

from ..authentication_facade import AuthenticationFacade
from .utils import (
    add_refresh_token_to_response,
    get_username_password_from_request,
    include_auth_token,
)

logger = logging.getLogger(__name__)


class Login(AbstractResource):
    """
    A resource for user authentication
    """

    urls = ["/api/login"]

    def __init__(self, authentication_facade: AuthenticationFacade):
        self._authentication_facade = authentication_facade

    @include_auth_token
    def post(self):
        """
        Authenticates a user

        Gets a username and password from the request sent from the client, authenticates, and
        returns an access token

        :return: Access token in the response body
        """
        try:
            username, password = get_username_password_from_request(request)
            response: ResponseValue = login()
            refresh_token = self._authentication_facade.generate_refresh_token(current_user)
            response = add_refresh_token_to_response(response, refresh_token)
        except Exception:
            return responses.make_response_to_invalid_request()

        if not isinstance(response, Response):
            return responses.make_response_to_invalid_request()

        if response.status_code == HTTPStatus.OK:
            self._authentication_facade.handle_successful_login(username, password)

        return make_response(response)
