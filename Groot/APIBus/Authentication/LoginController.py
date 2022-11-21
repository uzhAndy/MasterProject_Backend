from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

from Groot.Services.AuthService.AuthenticationService import AuthenticationService

bp = Blueprint('login', __name__, url_prefix='/auth')


@bp.route('/login', methods=['POST'])
def login():
    """
    the body should look the following:
    {
        "username": "{{admin_username}}",
        "password": "{{admin_pw}}",
        "role": "{{admin_role}}"
    }

    the return object looks like this:
    {
        "message": "Login successful.",
        "user": {
            "accepted": true,
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY1NTgyMjMwMCwianRpIjoiNmQ0OGRkYTgtMTgxMS00MThhLTllN2EtYjE2NjVjZDM5YWM0IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IkhhbnMgWmltbWVybWFubiIsIm5iZiI6MTY1NTgyMjMwMCwiZXhwIjoxNjU1ODI5NTAwLCJyb2xlIjoiYWRtaW4ifQ.RdRSPpJmUt39GS_zmRBk0HUInXlw4O8XG44MIT2AMf8",
            "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY1NTgyMjMwMCwianRpIjoiZjQzZDkyZTAtYWVjMi00YTAxLWJmODUtMmE4ZDU4YzNjNWM1IiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiJIYW5zIFppbW1lcm1hbm4iLCJuYmYiOjE2NTU4MjIzMDAsImV4cCI6MTY1ODQxNDMwMCwicm9sZSI6ImFkbWluIn0.pShIkoilLfcwKfaXOrpF3HlBqjzlkB60g_JlybDUdTQ",
            "role": "admin",
            "username": "Hans Zimmermann",
            "uuid": 8050
        }
    }, 200
    """
    user_data = request.get_json()
    return AuthenticationService.login(user_data)


@bp.route('/check_login', methods=['GET'])
@jwt_required()
def check_login():
    """
    the return object looks like this:
    {
        "message": "Check positive"
    }, 200
    """
    return {"message": "Check positive"}, 200


@bp.route('/check_role', methods=['GET'])
@jwt_required()
def get_role():
    """
    the return object looks like this:
    {
        "message": "Successfully checked the role.",
        "user": {
            "role": "admin",
            "username": "Hans Zimmermann"
        }
    }, 200
    """
    username = get_jwt_identity()
    return AuthenticationService.find_role(username)


@bp.route('logout', methods=['DELETE'])
@jwt_required()
def logout():
    """
    the return object looks like this:
    {
        "message": "Successfully logged out."
    }, 200
    """
    jwt = get_jwt()["jti"]
    return AuthenticationService.logout(jwt)
