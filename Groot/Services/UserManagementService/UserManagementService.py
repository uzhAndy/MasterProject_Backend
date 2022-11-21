from datetime import datetime

from Groot.Database.models.ClientAdvisorModel import ClientAdvisor
from Groot.Database.models.ClientModel import Client, ClientType
from Groot.Database.models.MicrophoneModel import Microphone
from Groot.Database.models.Role import Role
from Groot.Services.ResponseService.RequestResponseService import APIObjectsResponse


class UserManagementService():

    @staticmethod
    def get_users():
        list_ca = ClientAdvisor.query.all()
        return APIObjectsResponse.create_generic_data_response(200, 'Successfully requested for all clients', 'users',
                                                               list_ca)

    @staticmethod
    def get_clients(client_id, user: ClientAdvisor):
        http_response_code = 200
        message = 'Client Request successful.'
        if client_id:
            list_clients = Client.find_by_uuid(client_id)
            # ensure that the requested client is a client of the advisor

            if not Client.find_by_uuid(client_id).client_advisor_uuid == user.uuid and user.role != Role.admin.name:
                list_clients = []
                http_response_code = 403
                message = 'Access not allowed.'
                print("here")
        else:
            # return all clients if the user is an admin
            if user.isAdmin():
                list_clients = Client.get_all_clients()

            else:
                list_clients = Client.get_clients_of_user(user.uuid)

        return APIObjectsResponse.create_generic_data_response(http_response_code, message, 'clients', list_clients)

    @staticmethod
    def add_client(client_data: dict, user: ClientAdvisor):

        if ClientType.has_value(client_data['clientType']):
            new_client = Client(
                firstname=client_data['firstname'],
                lastname=client_data['lastname'],
                address={
                    'street': client_data['address1'],
                    'street_nr': client_data['address2'],
                    'zip_code': client_data['zipCode'],
                    'city': client_data['city'],
                    'country': client_data['country']
                },
                email=client_data['email'],
                client_type=client_data['clientType'],
                birthdate=datetime.strptime(client_data['birthdate'], '%Y-%m-%d'),
                AuM=client_data['AuM'],
                currency=client_data['currency'],
                client_advisor_uuid=user.get_uuid(),
                nr_of_counseling=client_data['nrOfCounselings']
            )
        else:
            return APIObjectsResponse.create_generic_response(406, 'Could not create new client client.')

        existing_client = Client.query.filter_by(firstname=new_client.firstname, lastname=new_client.lastname,
                                                 address=new_client.address).first()
        if existing_client:
            return APIObjectsResponse.create_generic_response(409, 'Could not create client as it already exisist.')

        new_client.save()
        return APIObjectsResponse.create_generic_response(200, 'Successfully create client.')

    @staticmethod
    def update_client(client_data: dict):

        client = Client.find_by_uuid(client_data['uuid'])
        if client:
            client.firstname = client_data['firstname']
            client.lastname = client_data['lastname']
            client.address = {
                'street': client_data['address1'],
                'street_nr': client_data['address2'],
                'zip_code': client_data['zipCode'],
                'city': client_data['city'],
                'country': client_data['country']
            }
            client.email = client_data['email']
            client.client_type = client_data['clientType']
            client.birthdate = datetime.strptime(client_data['birthdate'], '%Y-%m-%d')
            client.AuM = client_data['AuM']
            client.nr_of_counseling = client_data['nrOfCounselings']
            client.save()
            return APIObjectsResponse.create_generic_response(200, 'Successfully updated new client.')
        else:
            return APIObjectsResponse.create_generic_response(406, 'Could not update client.')

    @staticmethod
    def update_microphone(username, mic_id, mic_name):

        mic = Microphone.find_by_uuid(mic_id)
        user = ClientAdvisor.find_by_username(username)

        if user:
            user.microphone = mic
            user.save()
            return {'message': 'Successfully updated mic for ClientAdvisor',
                    "success": True, "mic": {"mic_id": mic_id, "name": mic_name}}

        else:
            return {'message': 'Could not update microphone for ClientAdvisor.', "success": False}

    @staticmethod
    def get_advisor_client_from_otp(otp_client_id):
        client = Client.query.filter_by(session_id=otp_client_id).first()

        return client.client_advisor.uuid, client.uuid
