# import libraries
from dataclasses import dataclass
from random import randint

from Groot.Database.models.Role import Role
# import extensions
from Groot.Extensions.DatabaseExtension import db


# function to create IDs
def generate_4digit_uuid(min=1000, max=9999):
    rand = randint(min, max)

    # check if uuid already exists
    while ClientAdvisor.query.filter_by(uuid=rand).first() is not None:
        rand = randint(min, max)

    return rand


@dataclass
class ClientAdvisor(db.Model):
    __tablename__ = "ClientAdvisor"

    uuid: int
    username: str
    role: str
    accepted: bool


    uuid = db.Column(db.Integer, primary_key=True,
                     default=generate_4digit_uuid)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    accepted = db.Column(db.Boolean, default=False)
    microphone_id = db.Column(db.Integer, db.ForeignKey("Microphone.mic_id"))
    microphone = db.relationship("Microphone", back_populates="advisors")
    sessions = db.relationship('Session', back_populates="client_advisor")


    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()
    
    def get_uuid(self) -> int:
        return self.uuid

    def __repr__(self):
        return (f'Client(uuid: {self.uuid}, username: {self.username}')
    
    def isAdmin(self):
        return self.role == Role.admin.name

    def get_sessions(self):
        return self.sessions

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_uuid(cls, uuid):
        return cls.query.filter_by(uuid=uuid).first()
