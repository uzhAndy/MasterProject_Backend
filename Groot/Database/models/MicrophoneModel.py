# import libraries
from dataclasses import dataclass

# import extensions
from Groot.Extensions.DatabaseExtension import db


def generate_mic_id():
    id = 1
    # check if uuid already exists
    while Microphone.query.filter_by(mic_id=id).first() is not None:
        id = id + 1

    return id


@dataclass
class Microphone(db.Model):
    __tablename__ = "Microphone"

    mic_id: int
    name: str
    ip: str
    port: int

    mic_id = db.Column(db.Integer, primary_key=True, default=generate_mic_id)
    ip = db.Column(db.String(50), unique=False, nullable=False)
    port = db.Column(db.Integer, unique=False, nullable=False)
    name = db.Column(db.String(50), unique=True, nullable=False)
    advisors = db.relationship("ClientAdvisor", back_populates="microphone")

    def serialize(self):
        return {
            'mic_id': self.mic_id,
            'ip': self.ip,
            'port': self.port,
            'name': self.name,
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def get_mic_id(self) -> int:
        return self.mic_id

    # def __repr__(self):
    #     return f'Microphone Mic_id: {self.mic_id}, ip: {self.ip}'

    @classmethod
    def find_by_ip(cls, ip):
        return cls.query.filter_by(ip=ip).first()

    @classmethod
    def find_by_uuid(cls, mic_id):
        return cls.query.filter_by(mic_id=mic_id).first()
