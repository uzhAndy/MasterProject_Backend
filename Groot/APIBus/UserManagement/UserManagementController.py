from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity

from Groot.Services.AuthService.AuthAnnotator import admin_advisor_required, admin_advisor_temp_client_required
from Groot.Services.AuthService.AuthenticationService import AuthenticationService
from Groot.Services.UserManagementService.UserManagementService import UserManagementService as UMS

bp = Blueprint('user', __name__)


@bp.route("/users", methods=["GET"])
def get_all_users():
    """
    the return object looks like this:
    {
        "message": "Successfully requested for all clients",
        "users": [
            {
                "accepted": true,
                "role": "guest",
                "username": "Daisha_Schmeler45",
                "uuid": 1059
            },
        ]
    }
    """
    return UMS.get_users()


@bp.route('/clients', methods=['GET'])
@admin_advisor_temp_client_required()
def get_all_clients(username, client_id):
    """
    optional parameter 'id':
    {{protocol}}://{{api-backend}}/clients?id=8835
    Results in only returning one client:
    {
        "clients": {

            },
        "message": "Client Request successful."

    }

    if no parameter is specified the return object looks like this:
    {
        "clients": [
            {
                "AuM": 1000.0,
                "address": {
                    "city": "Zurich",
                    "country": "CH",
                    "street": "Moosstrasse",
                    "street_nr": 67,
                    "zip_code": 8038
                },
                "birthdate": "Sun, 22 Nov 1998 00:00:00 GMT",
                "client_advisor_uuid": 6051,
                "client_type": "RETAIL",
                "currency": "CHF",
                "email": "andy@aidoo.io",
                "firstname": "Andy",
                "lastname": "Aidoo",
                "nr_of_counseling": 1,
                "portfolio": "",
                "session_id": 4841,
                "uuid": 2976
            }
        ],
        "message": "Client Request successful."
    }
    """
    user = AuthenticationService.get_user_from_username(username)
    return UMS.get_clients(client_id, user)


@bp.route('/clients', methods=['POST'])
@admin_advisor_required()
def add_new_client():
    """
    the body should look the following:
    {
        "AuM": 1000.0,
        "nrOfCounselings": 5,
        "firstname": "{{$randomFirstName}}",
        "lastname": "{{$randomLastName}}",
        "address1":"testaddress",
        "address2":"testaddress2",
        "zipCode":"8057",
        "city":"Zürich",
        "country":"Switzerland",
        "email": "testemail123@dsjafkl.ch",
        "clientType": "Professional",
        "birthdate": "2022-06-26",
        "currency":"CHF"
    }
    the return object looks like this:
    {
        "message": "Successfully create client."
    }
    """
    user = AuthenticationService.get_user_from_username(get_jwt_identity())
    req = request.get_json()
    return UMS.add_client(req, user)


@bp.route('/clients', methods=['PUT'])
def update_client():
    """
    expected body:
    {
        "AuM": 1000.0,
        "nrOfCounselings": "5",
        "firstname": "test",
        "lastname": "test",
        "address1":"testaddress",
        "address2":"testaddress2",
        "zipCode":"testzip",
        "city":"testcity",
        "country":"switzerland",
        "email": "test",
        "clientType": "test",
        "birthdate": "2022-06-26",
        "uuid": 8835
    }

    the return object looks like this:
    {
        "message": "Successfully updated new client."
    }
    """
    req = request.get_json()
    return UMS.update_client(req)
