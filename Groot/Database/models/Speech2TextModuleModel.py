from dataclasses import dataclass

from Groot.Extensions.DatabaseExtension import db


def generate_mic_id():
    id = 1
    # check if uuid already exists
    while Speech2TextModuleModel.query.filter_by(engine_id=id).first() is not None:
        id = id + 1

    return id

@dataclass
class Speech2TextModuleModel(db.Model):
    __tablename__ = "Speech2TextModule"

    engine_id: int
    name: str
    selected: bool

    engine_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    selected = db.Column(db.Boolean, nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def __repr__(self) -> str:
        return f"Speech2TextModule: {self.name}"

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_all_names(cls) -> list[str]:
        return [e.name for e in cls.query.all()]

    @classmethod
    def get_selected(cls):
        return [engine.name for engine in cls.query.all() if engine.selected][0]