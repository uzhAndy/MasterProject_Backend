from functools import wraps

from flask import jsonify
from flask import request
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity

from Groot.Database.models.ClientModel import Client
from Groot.Database.models.Role import Role
from Groot.Logging.config.LoggingFunctions import log_warning, print_info


def admin_advisor_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims["role"] == Role.admin.name or claims["role"] == Role.advisor.name:
                return fn(*args, **kwargs)
            else:
                log_warning(f'A user which is not an admin or an advisor wanted to access an api and was rejected')
                print_info('A user which is not an admin or an advisor wanted to access an api and was rejected')
                return jsonify(msg="Admins and advisors only!"), 403

        return decorator

    return wrapper


def admin_advisor_temp_client_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            # initialize values
            verify_jwt_in_request()
            claims = get_jwt()
            username = get_jwt_identity()
            client_id = None

            # if the request body is fullfilled a specific client is requested
            # get the client ID
            if 'id' in request.args:
                client_id = request.args['id']

            # if the username is not just numbers do the normal role check
            if not username.isnumeric() and claims["role"] == Role.admin.name or claims["role"] == Role.advisor.name:
                return fn(username, client_id, *args, **kwargs)

            # if only numbers are in the username -> it is in guest view (double check)
            elif username.isnumeric() and claims["role"] == Role.guest.name:
                # get the respective client
                client = Client.query.filter_by(session_id=username).first()

                if client:  # if the client exists
                    username = client.advisor_OTP_username  # set the advisor username to the advisor/admin who created the guest account
                    client_id = client.uuid  # replace the client_id with the UUID of the client
                    return fn(username, client_id, *args, **kwargs)
            else:
                log_warning(f'A user which is not an admin or an advisor wanted to access an api and was rejected')
                print_info('A user which is not an admin or an advisor wanted to access an api and was rejected')
                return jsonify(msg="Admins and advisors only!"), 403

        return decorator

    return wrapper


def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims['role'] == Role.admin.name:
                return fn(*args, **kwargs)
            else:
                log_warning(f'A user which is not an admin wanted to access an api and was rejected')
                print_info('A user which is not an admin wanted to access an api and was rejected')
                return jsonify(msg="Admins and advisors only!"), 403

        return decorator

    return wrapper
