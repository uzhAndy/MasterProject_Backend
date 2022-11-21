import pandas as pd

from Groot.Database.models.ClientAdvisorModel import ClientAdvisor
from Groot.Database.models.ClientModel import Client
from Groot.Database.models.FinancialJargon import FinancialJargon
from Groot.Database.models.Session import Session
from Groot.Database.models.VisualizationModel import Visualization
from Groot.Extensions.DatabaseExtension import db
from Groot.Services.Consultation.PlotBuilder.PlotBuilder import TermVisualization
from Groot.Services.ResponseService.RequestResponseService import \
    APIObjectsResponse


class VisualizationService:

    @staticmethod
    def get_mock_vizualization(client_uuid, client_advisor_uuid, subject):
        if client_uuid:
            client = Client.find_by_uuid(client_uuid)
        if subject:
            financial_term = FinancialJargon.find_by_subject(subject=subject)

        result_object = VisualizationService.get_visualization(
            client, financial_term)

        # store subject and description in session
        client_advisor = ClientAdvisor.find_by_uuid(client_advisor_uuid)
        current_session = Session.find_first_active_sessions_by_client_and_advisor(client, client_advisor)

        if len(current_session.summary) == 0:
            current_session.summary = [financial_term]
        else:
            current_session.summary.append(financial_term)

        current_session.save()

        return APIObjectsResponse.create_generic_data_dict_response_socket(
            result_object['message'],
            result_object['field_name'],
            result_object['data']
        )

    @staticmethod
    def get_visualization(client: Client, financial_term: FinancialJargon):

        term_calculation = None
        plot_data = None
        visualization = Visualization.get_by_tid(financial_term.tid)

        if visualization:
            # there is a visualization for the requested term

            # creates a canvas for the visualization f. i. SCATTERPLOT
            v_type = visualization.get_type()

            # gets the columns which are used for the visualization
            v_columns = visualization.get_columns()

            # filtered = visualization.get_share_classes()

            # returns the raw data queried
            plot_raw_data = VisualizationService.get_plot_data(
                column_names=v_columns, query=visualization.get_query())

            # transform data according the the personalization criteria
            if visualization.personalization_source != '' and visualization.personalization_target != '':
                personalized_data = VisualizationService.personalize(
                    client, plot_raw_data,
                    visualization.personalization_source,
                    visualization.personalization_target,
                    visualization.group_label)

                # set data for the visualization
                v_type.set_data(personalized_data)
            else:
                v_type.set_data(plot_raw_data)

            term_visualization = TermVisualization(
                term=financial_term, strategy=v_type.get_strategy())
            term_visualization.set_description(visualization.get_description())

            # execute visualization according the the defined strategy
            plot_data = term_visualization.executeStratey(client.currency)
            term_calculation = VisualizationService._calulate_max_draw_down(
                data=v_type.plot_data, y_axis_label=visualization.y_axis, x_axis_label=visualization.x_axis)

            # if visualization.personalization_source != '' and visualization.personalization_target != '':

            #     # personalize the y axis label to the client currency
            #     visualization.y_axis = client.currency
            #     print("\n personalized data: ")
            #     print(personalized_data)

        else:
            v_type = None

        # print("\nplot data")
        # print(plot_data)
        # # set y_axis_label to the currency of the client
        # plot_data["y_axis_label"] = client.currency

        return_dict = {
            'term': {
                'subject': financial_term.subject,
                'description': financial_term.description,
                'long_description': financial_term.long_description,
                'synonyms': financial_term.synonyms,
                'plot_type': v_type.plot_type if v_type else None,
            },
            financial_term.calculations_necessary[0]: term_calculation,
            'plot_data': plot_data
        }

        return {"status": 200, "message": f'Successfully requested for {financial_term.subject}',
                "field_name": 'TermVisualization', "data": return_dict}

    @staticmethod
    def get_plot_data(column_names: list, query: str):

        raw_data = db.engine.execute(query)

        formatted_data = [x for x in raw_data]

        return pd.DataFrame(formatted_data, columns=column_names)

    @staticmethod
    def personalize(client: Client, data: pd.DataFrame, pers_source: str, pers_target: str, group: str) -> list:

        frames = []

        if group != '':
            buckets = data[group].unique()
            for x in buckets:
                df = data[data[group] == x]
                personalization_factor = client.get_attribute(
                    pers_source) / df[pers_target].iloc[0]
                df[pers_target] = df[pers_target] * personalization_factor
                frames.append(df)
        else:
            personalization_factor = client.get_attribute(
                pers_source) / data[pers_target].iloc[0]

            data[pers_target] = data[pers_target] * personalization_factor
            frames.append(data)

        return pd.concat(frames, sort=False)

    @staticmethod
    def _calulate_max_draw_down(data, y_axis_label, x_axis_label, window=252):

        df = pd.DataFrame(data, columns=[x_axis_label, y_axis_label])

        roll_max = df[y_axis_label].rolling(window=window, min_periods=1).max()
        daily_draw_down = df[y_axis_label] / roll_max - 1
        return min(daily_draw_down.rolling(window=window, min_periods=1).min())
