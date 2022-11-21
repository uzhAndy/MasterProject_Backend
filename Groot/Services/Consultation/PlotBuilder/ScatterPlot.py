from Groot.Services.Consultation.PlotBuilder.PlotBuilder import Strategy


class ScatterPlotStrategy(Strategy):
    PLOT_TYPE = 'SCATTERPLOT'

    max: float
    min: float
    x_axis_label: str
    y_axis_label: str
    data: list
    description: str

    def __init__(self, x_axis_label, y_axis_label) -> None:
        self.x_axis_label = x_axis_label
        self.y_axis_label = y_axis_label

    def execute(self, client_currency) -> dict:
        self.max = max(x[self.y_axis_label] for x in self.data)
        self.min = min(x[self.y_axis_label] for x in self.data)

        return_dict = {
            'max': self.max,
            'min': self.min,
            'plot_values': self.data,
            'x_axis_label': self.x_axis_label,
            'y_axis_label': self.y_axis_label,
            'description': self.description,
            'plot_type': self.PLOT_TYPE,
            'client_currency': client_currency
        }

        return return_dict

    def set_data(self, data):
        self.data = data

    def set_description(self, description):
        self.description = description
