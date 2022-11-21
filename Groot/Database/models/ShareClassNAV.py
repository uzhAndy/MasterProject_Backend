from dataclasses import dataclass
from datetime import date

import pandas as pd
from tqdm import tqdm

from Groot.Database.models.ShareClass import ShareClass
from Groot.Extensions.DatabaseExtension import db


@dataclass
class ShareClassNAV(db.Model):
    ISIN:str
    currency: str
    NAVDate: date
    NAV: float

    ISIN = db.Column(db.String(12), db.ForeignKey(ShareClass.ISIN), nullable=False, primary_key=True)
    NAVDate = db.Column(db.Date, primary_key=True)
    currency = db.Column(db.String(3), nullable=False)
    NAV = db.Column(db.Float, nullable=False)

    share_class = db.relationship('ShareClass', foreign_keys=ISIN)

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()
    
    def add(self)-> None:
        db.session.add(self)
    
    def safe_bulk(self)-> None:
        db.session.commit()

    def update(self) -> None:
        db.session.commit()

    def __repr__(self) -> str:
        return f'ISIN: {self.ISIN}, Date: {self.NAVDate}, NAV: {self.NAV}'

    @classmethod
    def load_csv(cls, fpath:str) -> None:
        df = pd.read_csv(fpath, delimiter=';', parse_dates=['NAVDate'])

        for index, row in tqdm(df.iterrows(), total=df.shape[0]):
            curr_NAV = ShareClassNAV(
                ISIN=row['ISIN'],
                currency=row['Currency'],
                NAVDate=row['NAVDate'],
                NAV=row['NAV']
            )
            curr_NAV.add()
        db.session.commit()
    
    @classmethod
    def get_nr(cls):
        return len(cls.query.all())

    @classmethod
    def get_NAVs_By_ISIN(cls, ISIN):
        return cls.query.order_by(cls.NAVDate.asc()).filter_by(ISIN=ISIN).all()