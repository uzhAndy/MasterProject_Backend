# import libraries
import datetime
import enum
from dataclasses import dataclass
from datetime import date
from enum import Enum
from random import randint

from Groot.Database.models.ClientAdvisorModel import ClientAdvisor
from Groot.Extensions.DatabaseExtension import db


# import extensions

# function to create IDs
def generate_4digit_uuid(min=1000, max=9999):
    rand = randint(min, max)

    # check if uuid already exists
    while Client.query.filter_by(uuid=rand).first() is not None:
        rand = randint(min, max)

    return rand


class ClientType(Enum):
    RETAIL = "Retail"
    PROFESSIONAL = "Professional"
    INSTITUTIONAL = "Institutional"

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_ or value in cls._member_names_


@dataclass
class Client(db.Model):
    __tablename__ = "Client"

    uuid: int
    firstname: str
    lastname: str
    email: str
    address: dict
    birthdate: date
    nr_of_counseling: int
    AuM: float
    currency: str
    client_advisor_uuid: int
    client_type: enum
    portfolio: str
    session_id: int

    uuid = db.Column(db.Integer, primary_key=True,
                     default=generate_4digit_uuid)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    address = db.Column(db.JSON, nullable=False)
    birthdate = db.Column(db.Date)
    nr_of_counseling = db.Column(db.Integer)
    AuM = db.Column(db.Float)
    currency = db.Column(db.String(3))
    client_advisor_uuid = db.Column(db.Integer, db.ForeignKey(ClientAdvisor.uuid))
    client_type = db.Column(db.String(15), nullable=False)
    portfolio = db.Column(db.String(10), default='')
    client_advisor = db.relationship('ClientAdvisor', foreign_keys=client_advisor_uuid)
    session_id = db.Column(db.Integer, nullable=True, unique=True)
    session_password = db.Column(db.String(50), nullable=True)
    valid_until = db.Column(db.DateTime, nullable=True)
    sessions_clients = db.relationship('Session', back_populates="client")
    advisor_OTP_username = db.Column(db.String(20), nullable=True)

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()

    def update(self) -> None:
        db.session.commit()

    def __repr__(self) -> str:
        return (f'Client(uuid: {self.uuid}, firstname: {self.firstname}, lastname: {self.lastname})')
    
    def get_uuid(self) -> int:
        return self.uuid
    
    def get_attribute(self, column_name) -> None:
        return db.engine.execute(f'SELECT {column_name} from client WHERE client.uuid = {self.uuid}').first()[0]

    @classmethod
    def find_by_uuid(cls, uuid:int):
        client = cls.query.filter_by(uuid=uuid).first()
        if client:
            client.nr_of_counseling = len(client.sessions_clients)
        return client

    @classmethod
    def get_all_clients(cls):
        clients = cls.query.all()
        result = []

        for c in clients:
            c.nr_of_counseling = len(c.sessions_clients)
            result.append(c)

        return result

    @classmethod
    def get_clients_of_user(cls, uuid):
        return cls.query.filter_by(client_advisor_uuid=uuid).all()

    def get_sessions(self):
        return self.sessions_clients

    def temp_login_valid(self):
        return self.valid_until > datetime.datetime.now()
