from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity

from Groot.Services.AuthService.AuthAnnotator import admin_advisor_required
from Groot.Services.SessionService.SessionAdministration import SessionAdministration

bp = Blueprint('consultation_admin', __name__, url_prefix='/consultation_admin')


@bp.route('/save_id', methods=['POST'])
@admin_advisor_required()
def generate_one_time_password():
    """
    the body should look the following:
    {
        "session_id": "{{session_id}}",
        "uuid": "2976",
        "password_client": "strong_password",
        "valid_until": 2
    }

    the return object looks like this:
    {
        "message": "Session ID saved",
        "session": {
            "session_id": "9272",
            "uuid": "2976",
            "valid_until": "Tue, 21 Jun 2022 21:23:49 GMT"
        }
    }, 202
    """

    user_data = request.get_json()
    username = get_jwt_identity()

    return SessionAdministration.save_one_time_login(username, user_data)


@bp.route('/generate_id', methods=['GET'])
@admin_advisor_required()
def generate_one_time_id():
    """
    the return object looks like this:
    {
        "message": "Session ID created",
        "session_id": 8829
    }
    """

    return SessionAdministration.generate_4digit_session_id()
