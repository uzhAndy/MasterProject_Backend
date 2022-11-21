from flask import jsonify


class APIObjectsUser():

    @staticmethod
    def create_get_user_response(message, users):
        return jsonify({"message": message, "users": users})
