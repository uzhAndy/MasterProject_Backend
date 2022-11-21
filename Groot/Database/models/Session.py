# import libraries
from dataclasses import dataclass
from datetime import datetime
from random import randint

from Groot.Database.models.ClientAdvisorModel import ClientAdvisor
from Groot.Database.models.ClientModel import Client
# import extensions
from Groot.Extensions.DatabaseExtension import db
from Groot.Logging.config.LoggingFunctions import print_info


# function to create IDs
def generate_4digit_uuid(min=1000, max=9999):
    rand = randint(min, max)

    # check if uuid already exists
    while Session.query.filter_by(uuid=rand).first() is not None:
        rand = randint(min, max)

    return rand


association_table = db.Table(
    "association",
    db.Column("left_id", db.ForeignKey("Session.uuid")),
    db.Column("right_id", db.ForeignKey("FinancialJargon.tid")),
)


@dataclass
class Session(db.Model):
    __tablename__ = "Session"

    client_advisor_id: int
    transcript: str
    start_time: datetime
    stop_time: datetime
    client: Client
    client_advisor: ClientAdvisor
    completed: bool

    uuid = db.Column(db.Integer, primary_key=True,
                     default=generate_4digit_uuid)
    client_advisor_id = db.Column(db.Integer, db.ForeignKey("ClientAdvisor.uuid"))
    client_advisor = db.relationship("ClientAdvisor", back_populates="sessions")
    client_id = db.Column(db.Integer, db.ForeignKey("Client.uuid"))
    client = db.relationship("Client", back_populates="sessions_clients")
    transcript = db.Column(db.Text)
    sentiment = db.Column(db.String(50))
    start_time = db.Column(db.DateTime)
    stop_time = db.Column(db.DateTime)
    completed = db.Column(db.Boolean, default=False)
    summary = db.relationship("FinancialJargon", secondary=association_table)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def get_uuid(self) -> int:
        return self.uuid

    @classmethod
    def find_by_uuid(cls, uuid):
        return Session.query.filter_by(uuid=uuid).first()
    
    @classmethod
    def find_first_active_sessions_by_client_and_advisor(cls, client, client_advisor):
        """
        Finds the first active session by client and advisor.

        If more than one session is active, then the newest one is returned, and the others are marked as completed. However, if the newest one is older than 4h then it is also marked as completed.
        """

        # get all active sessions of the client and advisor
        sessions = Session.query.filter_by(client_id=client.uuid, client_advisor_id=client_advisor.uuid, completed=False).all()

        # set all sessions to completed except the last one if its start date is today - 4h
        if len(sessions) > 1:
            # sort sessions by start time
            sessions.sort(key=lambda x: x.start_time)

            # set all sessions except the last one to completed
            for s in sessions[:-1]:
                print(s.start_time)
                s.completed = True
                s.update()
            
            # if the last (i.e. newest) session is older than 4h (14400 seconds), set it to completed
            if (datetime.now() - sessions[-1].start_time).total_seconds() > 14400:
                sessions[-1].completed = True
                sessions[-1].update()
                return None
            else:
                return sessions[-1]

        elif len(sessions) == 1:
            return sessions[0]
        else:
            print_info(f"No active sessions found of client {client.uuid} and advisor {client_advisor.uuid}")

            return None
