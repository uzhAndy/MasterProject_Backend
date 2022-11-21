from dataclasses import dataclass

import pandas as pd
from tqdm import tqdm

from Groot.Extensions.DatabaseExtension import db


@dataclass
class MarketData(db.Model):
    id: int
    date: str
    rate: float
    monthly_return: float
    underlying: str

    id = db.Column(db.Integer, primary_key=True)
    underlying = db.Column(db.String, nullable=False)
    date = db.Column(db.Date, nullable=False)
    rate = db.Column(db.Float, nullable=False)
    monthly_return = db.Column(db.Float, nullable=False)

    @classmethod
    def load_csv(cls, fpath: str, underlying: str, return_in_percent: bool = False) -> None:
        df = pd.read_csv(fpath, delimiter=',', parse_dates=['Date'])

        prev_price = 0

        for index, row in tqdm(df.iterrows(), total=df.shape[0]):

            return_ = prev_price / row['Value']-1
            if return_in_percent:
                return_ *= 100
            curr_SMI_val = MarketData(
                date=row['Date'],
                underlying=underlying,
                rate=row['Value'],
                monthly_return=return_
            )
            prev_price = row['Value']
            db.session.add(curr_SMI_val)
        db.session.commit()

