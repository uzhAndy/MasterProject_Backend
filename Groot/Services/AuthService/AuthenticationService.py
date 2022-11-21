from datetime import datetime, timezone

from flask_jwt_extended import (
    create_access_token, create_refresh_token, get_jwt_identity)

from Groot.Database.models.ClientAdvisorModel import ClientAdvisor
from Groot.Database.models.ClientModel import Client
from Groot.Database.models.JWT_tokens import TokenBlocklist
from Groot.Database.models.Role import Role
from Groot.Database.models.Speech2TextModuleModel import Speech2TextModuleModel
from Groot.Extensions.DatabaseExtension import jwt, db
from Groot.Services.ResponseService.RequestResponseService import APIObjectsResponse


class AuthenticationService:

    @staticmethod
    def login(user_data):
        # check if it is only numbers
        if str(user_data["username"]).isdigit():
            return_obj = AuthenticationService.__login_without_password(
                user_data)
        else:
            return_obj = AuthenticationService.__login_with_password(user_data)

        return return_obj

    @staticmethod
    def __generate_login_response(uuid, username, role, accepted):

        access_token = create_access_token(
            identity=username, additional_claims={"role": role})
        refresh_token = create_refresh_token(
            identity=username, additional_claims={"role": role})
        accepted = accepted
        uuid = uuid
        return_data = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'accepted': accepted,
            'uuid': uuid,
            'role': role,
            'username': username
        }
        return APIObjectsResponse.create_generic_data_response(200, 'Login successful.', 'user', return_data)

    @staticmethod
    def __login_without_password(user_data):
        session_id = user_data['username']
        session_password = user_data['password']

        # check if session_id exists
        client = Client.query.filter_by(session_id=session_id).first()

        if not client:
            return APIObjectsResponse.create_generic_response(406, 'Login unsuccessful.')

        now = datetime.now()

        # check if password is correct and if the login is still valid
        if now > client.valid_until or client.session_password != session_password:
            return APIObjectsResponse.create_generic_response(406, 'Login unsuccessful.')

        return AuthenticationService.__generate_login_response(session_id, session_id,
                                                               Role.guest.name, True)

    @staticmethod
    def __login_with_password(user_data):
        # create a temporary Client Advisor
        temp_user = ClientAdvisor(
            username=user_data["username"], password=user_data["password"])

        user_from_db = ClientAdvisor.find_by_username(temp_user.username)

        # if no user exists
        if not user_from_db or not user_from_db.accepted:
            return APIObjectsResponse.create_generic_response(406, 'User has not been accepted yet')

        if user_from_db.password == temp_user.password:
            return AuthenticationService.__generate_login_response(user_from_db.uuid, user_from_db.username,
                                                                   user_from_db.role, user_from_db.accepted)
        else:
            return APIObjectsResponse.create_generic_response(406, 'Login unsuccessful.')

    @staticmethod
    def register_new_user(user_data):
        # check if the username consists of only digits
        if str(user_data['username']).isdigit():
            APIObjectsResponse.create_generic_response(406, 'Invalid Username')

        new_user = ClientAdvisor(
            username=user_data['username'], password=user_data['password'], role=user_data['role'])

        # check if the username is still available
        if ClientAdvisor.find_by_username(new_user.username):
            return APIObjectsResponse.create_generic_response(406, 'Username already taken.')

        # check if the role is valid
        try:
            Role(new_user.role)
        except ValueError:
            print("Error in AuthenticationService.py line 101")
            return APIObjectsResponse.create_generic_response(406, 'Invalid role selected.')

        new_user.save()
        return APIObjectsResponse.create_generic_data_response(201, 'User successfully created', 'user', new_user)

    @staticmethod
    def accept_new_user(user_data):
        username = get_jwt_identity()

        user_admin = ClientAdvisor.find_by_username(username)
        user_to_accept = ClientAdvisor.find_by_username(user_data["username"])

        # if no user was found
        if not user_admin or not user_to_accept:
            return APIObjectsResponse.create_generic_response(406,
                                                              'Could not accept new user, as it was not found in the database.')

        if user_admin.role != Role.admin.name:
            return APIObjectsResponse.create_generic_response(403, 'User does not have permission to accept new users.')

        # negate permission
        new_permission = not user_to_accept.accepted
        user_to_accept.accepted = new_permission

        user_to_accept.update()

        return APIObjectsResponse.create_generic_response(200, 'Successfully given privileges to user.')

    @staticmethod
    def edit_user(new_user_data):
        username = get_jwt_identity()

        access_token = ""
        refresh_token = ""
        uuid = new_user_data["uuid"]

        # changing a username once works, but changing it again breaks, as find_by_username returns None (line 110)
        user = ClientAdvisor.find_by_username(username)  # user that edits
        # user in the database that is being edited
        user_to_edit = ClientAdvisor.find_by_uuid(uuid)

        # make sure the user exists
        if not user or not user_to_edit:
            return APIObjectsResponse.create_generic_response(406,
                                                              'Could not accept new user, as it was not found in the database.')

        # if the user is not the account that is being edited, don't allow it
        if user.username != user_to_edit.username:
            return APIObjectsResponse.create_generic_response(401, 'User does not have permisson to edit another user.')

        # check if new username is available (i.e. unique)
        if user and not (user_to_edit.username == username):
            return APIObjectsResponse.create_generic_response(406, 'Username already taken.')

        # check if the current password is correct
        if user_to_edit.password != new_user_data["currentPassword"]:
            return APIObjectsResponse.create_generic_response(403, 'Incorrect current password provided.')

        # ===== apply changes (this part is only reached if all checks above are valid) =====

        # if some value is unchanged, i.e. an empty string, then change nothing in the database
        if new_user_data["username"] != "":
            user_to_edit.username = new_user_data["username"]
        if new_user_data["newPassword"] != "":
            user_to_edit.password = new_user_data["newPassword"]

        user_to_edit.update()

        # create new tokens (because username may have changed; even if only the password changed the token gets renewed)
        access_token = create_access_token(identity=user_to_edit.username)
        refresh_token = create_refresh_token(identity=user_to_edit.username)

        return_data = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'uuid': uuid,
            'username': user_to_edit.username
        }

        return APIObjectsResponse.create_generic_data_response(200, 'Successfully updated personal data.', 'user',
                                                               return_data)

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()
        return token is not None

    @staticmethod
    def find_role(username):
        role = ClientAdvisor.query.filter_by(username=username).first().role
        return_data = {
            'username': username,
            'role': role
        }
        return APIObjectsResponse.create_generic_data_response(200, 'Successfully checked the role.', 'user',
                                                               return_data)

    @staticmethod
    def logout(jwt):
        now = datetime.now(timezone.utc)
        TokenBlocklist(jti=jwt, created_at=now).save()

        return APIObjectsResponse.create_generic_response(200, 'Successfully logged out.')

    @staticmethod
    def get_user_from_username(username):
        return ClientAdvisor.query.filter_by(username=username).first()

    @staticmethod
    def get_engines():
        all_engines = Speech2TextModuleModel.get_all_names()
        currently_selected = Speech2TextModuleModel.get_selected()
        return {"selection": all_engines, "selected": currently_selected}

    @staticmethod
    def set_engines(new_engine):
        all_engines = Speech2TextModuleModel.get_all()

        for engine in all_engines:
            if engine.selected:
                engine.selected = False

            if engine.name == new_engine:
                engine.selected = True

            engine.update()

        return {"message": "successfully updated", "current_engine": new_engine}
