from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from Groot.Services.AuthService.AuthenticationService import AuthenticationService

bp = Blueprint('edit', __name__, url_prefix='/auth')


@bp.route("/edit_user", methods=["PUT"])
@jwt_required()
def save_changes():
    """
    the body should look as follows:
    {
        "username": "Martin", 
        "currentPassword": "strong_password",
        "newPassword": "new_password",
        "newPasswordConfirmation": "new_password".
        "uuid": "uuid"
    }

    the return object looks like this:
    { message': "Updated",
     'username': user_from_db.username,
     }, 200
    """
    new_user_data = request.get_json()
    return AuthenticationService.edit_user(new_user_data)
