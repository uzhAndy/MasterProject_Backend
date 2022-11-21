from Groot.APIBus.Consultation.ConsultationController import check_login
from Groot.Database.models.Role import Role

from Groot.Extensions.DatabaseExtension import socket_io

from Groot.Services.Consultation.VisualizationService import VisualizationService
from Groot.Services.UserManagementService.UserManagementService import UserManagementService as UMS


@socket_io.on("getVisualization")
@check_login
def get_mock_vizualization_frontend(username, client, sid, data):
    uuid = data['client_id']
    subject = data['subject']
    client_advisor_id = data['advisor_uuid']

    if client_advisor_id == uuid and data['role'] == Role.guest.name:
        client_advisor_id, uuid = UMS.get_advisor_client_from_otp(uuid)

    socket_io.emit('getVisualization_response',
                   VisualizationService.get_mock_vizualization(client_uuid=uuid,
                                                               client_advisor_uuid=client_advisor_id, subject=subject),
                   room=str(client.uuid))
