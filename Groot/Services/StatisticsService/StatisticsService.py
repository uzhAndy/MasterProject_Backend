from transformers import pipeline

from Groot.Database.models.ClientAdvisorModel import ClientAdvisor
from Groot.Services.ResponseService import RequestResponseService

sentiment_analysis = pipeline("sentiment-analysis", model="siebert/sentiment-roberta-large-english")


class StatisticService():

    @staticmethod
    def get_statistics(advisor: ClientAdvisor):
        sessions = advisor.get_sessions()

        clients = []

        # analysis comes here
        for client in sessions:
            if not StatisticService.check_if_client_in(clients, client):
                client_mapped = {
                    "firstname": client.client.firstname,
                    "lastname": client.client.lastname,
                    "client_type": client.client.client_type,
                    "asset": client.client.AuM,
                    "email": client.client.email,
                    "currency": client.client.currency,
                    "sessions": [StatisticService.create_session_obj(client, 1, sentiment_analysis)],
                    "nr_of_sessions": 1,
                }
                clients.append(client_mapped)
            else:
                index, client_mapped = StatisticService.get_client_from_list(clients, client)
                number_sessions = len(client_mapped['sessions'])
                client_mapped['sessions'].append(
                    StatisticService.create_session_obj(client, number_sessions + 1, sentiment_analysis)
                )
                client_mapped["nr_of_sessions"] = client_mapped["nr_of_sessions"] + 1
                clients[index] = client_mapped

        return RequestResponseService.APIObjectsResponse.create_generic_data_response(
            200,
            "Retrieving the statistics was successful",
            "stats",
            clients
        )

    @staticmethod
    def create_session_obj(client, session_id, sentiment_analysis):
        sentiment = sentiment_analysis(client.transcript[:500])

        return {
            "session_id": session_id,
            "date": client.start_time,
            "advisor": client.client_advisor.username,
            "duration": (client.stop_time - client.start_time).total_seconds() / 60,
            "sentiment": sentiment[0]['label'],
            "sentiment_quality": sentiment[0]['score'],
            # "sentiment": "positive",
            # "sentiment_quality": 0.7898,
            "transcript": client.transcript,
            "summary": [{
                "title": term.subject,
                "description": term.long_description,
            } for term in client.summary
            ]
        }

    @staticmethod
    def check_if_client_in(list, client):
        return any(
            (c['firstname'] == client.client.firstname and c['lastname'] == client.client.lastname) for c in list)

    @staticmethod
    def get_client_from_list(list, client):
        for i, c in enumerate(list):
            if c['firstname'] == client.client.firstname and c['lastname'] == client.client.lastname:
                return i, c
