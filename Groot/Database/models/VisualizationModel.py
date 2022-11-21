from dataclasses import dataclass

from pandas import DataFrame
from sqlalchemy import ForeignKey

from Groot.Database.models.FinancialJargon import FinancialJargon
from Groot.Database.models.ShareClass import ShareClass
from Groot.Extensions.DatabaseExtension import db
from Groot.Services.Consultation.PlotBuilder.CompositeScatterPlot import CompositeScatterPlotStrategy
from Groot.Services.Consultation.PlotBuilder.MultiScatterPlot import MultiScatterPlotStrategy
from Groot.Services.Consultation.PlotBuilder.PlotBuilder import Strategy
from Groot.Services.Consultation.PlotBuilder.ScatterPlot import ScatterPlotStrategy


class PlotFactory:

    x_axis_label: str
    y_axis_label: str
    plot_strategy: Strategy
    plot_data: list = []
    plot_type: str


    def __init__(self, x_axis: str, y_axis: str, plot_type: str, group_label) -> None:
        self.plot_type = plot_type
        self.x_axis_label = x_axis
        self.y_axis_label = y_axis
        if plot_type == 'SCATTERPLOT':
            self.plot_strategy = ScatterPlotStrategy(
                x_axis_label=x_axis, y_axis_label=y_axis)
        if plot_type == 'MULTI_SCATTERPLOT':
            self.plot_strategy = MultiScatterPlotStrategy(
                x_axis_label=x_axis, y_axis_label=y_axis, group_label=group_label)
        if plot_type == 'COMPOSITE_SCATTERPLOT':
            self.plot_strategy = CompositeScatterPlotStrategy(x_axis_label=x_axis, y_axis_label=y_axis, sort=['Date', 'Underlying'], group=group_label)

    def set_data(self, data: DataFrame) -> None:
        self.plot_data.clear()

        for index, row in data.iterrows():
            self.plot_data.append(row.to_dict())
        # self.plot_data = data
        self.plot_strategy.set_data(self.plot_data)

    def get_strategy(self):
        return self.plot_strategy


@dataclass
class Visualization(db.Model):
    vid: int
    visualization_type: str
    data_source_table: str
    data_source_columns: str
    data_source_filter_column: str
    data_source_filter_values: str
    x_axis: str
    y_axis: str
    group_label: str
    viz_query: str
    personalization_source: str
    personalization_target: str
    tid: int
    description: str

    vid = db.Column(db.Integer, primary_key=True)
    visualization_type = db.Column(db.String(15), nullable=False)
    data_source_table = db.Column(db.String(15))
    data_source_columns = db.Column(db.String(30))
    data_source_filter_column = db.Column(db.String(15))
    data_source_filter_values = db.Column(db.String(100))
    x_axis = db.Column(db.String())
    y_axis = db.Column(db.String())
    viz_query = db.Column(db.String())
    group_label = db.Column(db.String)
    personalization_source = db.Column(db.String())
    personalization_target = db.Column(db.String())
    description = db.Column(db.String())
    tid = db.Column(db.Integer(), ForeignKey(FinancialJargon.tid))

    tid_fk = db.relationship(
        'FinancialJargon', foreign_keys='Visualization.tid')

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()

    def update(self) -> None:
        db.session.commit()

    def get_type(self) -> PlotFactory:
        return PlotFactory(x_axis=self.x_axis, y_axis=self.y_axis, plot_type=self.visualization_type, group_label=self.group_label)

    def get_table(self) -> list:
        return self.data_source_table

    def get_columns(self) -> list:
        return self.data_source_columns.split(',')

    def get_filter_column(self) -> list:
        return self.data_source_filter_column

    def get_filter_value(self) -> list:
        return self.data_source_filter_values
    
    def get_share_classes(self):
        return [ShareClass.get_shcl_by_ISIN(x) for x in self.data_source_filter_values.split(',')]
    
    def get_description(self):
        return self.description
    
    def get_query(self):
        return self.viz_query

    @classmethod
    def get_by_tid(cls, tid: int):
        return cls.query.filter_by(tid=tid).first()
