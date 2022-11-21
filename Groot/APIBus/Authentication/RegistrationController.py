from flask import Blueprint, request

from Groot.Services.AuthService.AuthAnnotator import admin_required
from Groot.Services.AuthService.AuthenticationService import AuthenticationService

bp = Blueprint('register', __name__, url_prefix='/auth')


@bp.route("/register", methods=["POST"])
def register():
    """
    the body should look the following:
    { "username": "Martin", "password": "strong_password", "role": "guest"}
    the return object looks like this:
    {
        'message': "Created",
        'username': user_from_db.username,
        'role': user_from_db.role,
     }, 201
    """
    user_data = request.get_json()
    return AuthenticationService.register_new_user(user_data)


@bp.route("/accept", methods=["PUT"])
@admin_required()
def accept_user():
    """
    the body should look the following:
    {
        "username": "Martin",
        "password": "strong_password",
        "role": "guest"
    }, the password is not really necessary for this endpoint

    the return object looks like this:
    {
        message': "Created",
        'username': user_from_db.username,
    }, 200
    """

    user_data = request.get_json()
    return AuthenticationService.accept_new_user(user_data)


@bp.route("/engine", methods=["GET"])
@admin_required()
def get_engine():
    """
    the return object looks like this:
    {
        "selected": "Google",
        "selection": [
            "AssemblyAI",
            "Google",
            "Mock_Script"
        ]
    }
    """
    return AuthenticationService.get_engines()


@bp.route("/engine", methods=["PUT"])
@admin_required()
def put_engine():
    """
    the body should look the following:
    {
        "new_engine": "Google"
    }
    """
    user_data = request.get_json()
    new_engine = user_data["new_engine"]

    return AuthenticationService.set_engines(new_engine)
