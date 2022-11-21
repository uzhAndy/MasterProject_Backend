from dataclasses import dataclass
from datetime import date

import numpy
import pandas as pd
from tqdm import tqdm

from Groot.Extensions.DatabaseExtension import db


@dataclass
class ShareClass(db.Model):
    # UDISIN
    ISIN: str
    # OFST020060
    share_class_name: str
    # OFST020540
    currency: str
    # OFST020400
    distribution_policy: str
    # FUNDTYPE
    fund_type: str
    # OFST020560
    launch_date: date
    # OFST020050
    share_class_extension: str
    # OFST024000
    risk_profile: int

    # INVESTOR_TYPE
    client_type: str
    # INITIAL_LAUNCH_PRICE (split value from source file using " " as delimiter and take second element)
    initial_launch_price: float

    ISIN = db.Column(db.String(12), primary_key=True)
    share_class_name = db.Column(db.String(50), nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    distribution_policy = db.Column(db.String(20), nullable=False)
    fund_type = db.Column(db.String(20), nullable=False)
    launch_date = db.Column(db.Date, nullable=False)
    share_class_extension = db.Column(db.String(9), nullable=False)
    risk_profile = db.Column(db.Integer)
    client_type = db.Column(db.String(15), nullable=False)
    initial_launch_price = db.Column(db.Float, nullable=False)

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()

    def update(self) -> None:
        db.session.commit()

    def __repr__(self) -> str:
        return f'ISIN: {self.ISIN}, Share Class: {self.share_class_name}, Risk Factor: {str(self.risk_profile)}'

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_shcl_by_client_type(cls, client_type):
        return cls.query.filter_by(client_type=client_type).all()

    @classmethod
    def get_shcl_by_ISIN(cls, ISIN: str):
        return cls.query.filter_by(ISIN=ISIN).first()

    @classmethod
    def load_csv(cls, fpath: str) -> None:
        df = pd.read_csv(fpath, delimiter=';', parse_dates=['OFST020560'])
        df = df[[
            'UDISIN', 'OFST020060', 'OFST020540', 'OFST020400', 'FUNDTYPE', 'OFST020560', 'OFST020050',
            'OFST024000', 'INVESTOR_TYPE', 'INITIAL_LAUNCH_PRICE'
        ]]
        df['INITIAL_LAUNCH_PRICE'] = df['INITIAL_LAUNCH_PRICE'].str.split(
            ' ').str[1]
        df['INITIAL_LAUNCH_PRICE'] = df['INITIAL_LAUNCH_PRICE'].replace(
            numpy.nan, 0)

        for index, row in tqdm(df.iterrows(), total=df.shape[0]):
            curr_shcl = ShareClass(
                ISIN=row['UDISIN'],
                share_class_name=row['OFST020060'],
                currency=row['OFST020540'],
                distribution_policy=row['OFST020400'],
                fund_type=row['FUNDTYPE'],
                launch_date=row['OFST020560'],
                share_class_extension=row['OFST020050'],
                risk_profile=row['OFST024000'],
                client_type=row['INVESTOR_TYPE'],
                initial_launch_price=row['INITIAL_LAUNCH_PRICE']
            )
            db.session.add(curr_shcl)
        db.session.commit()
