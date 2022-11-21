from pandas import DataFrame

from Groot.Database.models.ShareClass import ShareClass
from Groot.Services.Consultation.PlotBuilder.PlotBuilder import Strategy


class MultiScatterPlotStrategy(Strategy):
    PLOT_TYPE = 'MULTI_SCATTERPLOT'
    data: DataFrame
    x_axis_label: str
    y_axis_label: str
    group_label: str

    def __init__(self, x_axis_label, y_axis_label, group_label) -> None:
        self.x_axis_label = x_axis_label
        self.y_axis_label = y_axis_label
        self.group_label = group_label

    def execute(self, client_currency) -> dict:

        plots = []
        df = DataFrame(self.data)

        descriptions = self.description.split(',')

        plot_ids = df[self.group_label].unique()

        for i in range(len(plot_ids)):
            plot_df = df[df[self.group_label] == plot_ids[i]]
            max_y = plot_df[self.y_axis_label].max()
            min_y = plot_df[self.y_axis_label].min()
            return_data = []
            curr_shcl: ShareClass = ShareClass.get_shcl_by_ISIN(i)

            for column, row in plot_df.iterrows():
                return_data.append(
                    row[[self.y_axis_label, self.x_axis_label]].to_dict())
            return_dict = {
                'max': max_y,
                'min': min_y,
                'plot_values': return_data,
                'x_axis_label': self.x_axis_label,
                'y_axis_label': self.y_axis_label,
                'description': f'{descriptions[0]} {descriptions[i + 1]}',
                'client_currency': client_currency
            }

            plots.append(return_dict)
            plot_df = None
        return plots

    def set_data(self, data):
        self.data = data

    def set_description(self, description):
        self.description = description
