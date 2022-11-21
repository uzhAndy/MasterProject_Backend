from flask import jsonify


class APIObjectsResponse():

    @staticmethod
    def create_get_user_response(message, users):
        return jsonify({"message": message, "users": users})

    @staticmethod
    def create_generic_response(status: int, message: str):
        return jsonify({'message': message}), status

    @staticmethod
    def create_generic_data_response(status: int, message: str, data_name: str, data: any):
        return jsonify({
            'message': message,
            data_name: data
        }), status

    @staticmethod
    def create_generic_data_dict_response(status: int, message: str, data_name: str, data: dict):
        return jsonify({
            'message': message,
            data_name: data
        }), status

    @staticmethod
    def create_generic_data_dict_response_socket(message: str, data_name: str, data: dict):
        return {
            'message': message,
            data_name: data
        }
