from pandas import DataFrame

from Groot.Services.Consultation.PlotBuilder.PlotBuilder import Strategy


class CompositeScatterPlotStrategy(Strategy):
    PLOT_TYPE = 'COMPOSITE_SCATTERPLOT'
    data: DataFrame
    x_axis_label: str
    y_axis_label: str
    group: str
    sort: list

    def __init__(self, x_axis_label, y_axis_label, sort, group) -> None:
        self.x_axis_label = x_axis_label
        self.y_axis_label = y_axis_label
        self.sort = sort
        self.group = group

    def execute(self, client_currency) -> dict:

        plot = []
        df = DataFrame(self.data).sort_values(self.sort)

        data_keys = [x for x in df[self.group].unique()]
        curr_date = df['Date'][0]
        curr_dict = {}

        for index, row in df.iterrows():
            if row['Date'] != curr_date:
                curr_date = row['Date']
                # using dict() to create a copy so that the dictionary in the plot does not get cleared, when the original
                # dictionary is reset
                plot.append(dict(curr_dict))
                curr_dict.clear()
            curr_dict['Date'] = curr_date
            curr_dict[row['Underlying']] = row['Return']

        max_y = df[self.y_axis_label].max()
        min_y = df[self.y_axis_label].min()

        return_dict = {
            'max': max_y,
            'min': min_y,
            'plot_values': plot,
            'x_axis_label': self.x_axis_label,
            'y_axis_label': self.y_axis_label,
            'data_keys': data_keys,
            'description': self.description,
            'plot_type': self.PLOT_TYPE,
            'client_currency': client_currency
        }

        #     plots.append(return_dict)
        #     plot_df = None
        return return_dict

    def set_data(self, data):
        self.data = data

    def set_description(self, description):
        self.description = description
