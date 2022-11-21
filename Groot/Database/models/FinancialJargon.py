# used libraries are imported here
from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import func

# used extensions are imported here
from Groot.Extensions.DatabaseExtension import db


@dataclass
class FinancialJargon(db.Model):
    __tablename__ = "FinancialJargon"

    tid = db.Column(db.Integer, primary_key=True)
    tid: int
    subject: str
    synonyms: list[str]
    description: str
    long_description: str
    calculations_necessary = list[str]

    _subject = db.Column(db.String(50), unique=True, nullable=False)
    _synonyms = db.Column(db.String, default="")
    _description = db.Column(db.String(300), nullable=False)
    _long_description = db.Column(db.String(1000), nullable=False)
    # probably removable
    _calculations_necessary = db.Column(db.String, default="")

    # vid_fk = db.relationship('Visualization', foreign_keys=vid)

    @property
    def synonyms(self):
        if self._synonyms:
            return [str(syn) for syn in self._synonyms.split(';')]
        else:
            return ['']

    @synonyms.setter
    def synonyms(self, value_list):
        self._synonyms = ''
        self._synonyms += ";".join([syn.lower() for syn in value_list])

    @property
    def subject(self):
        return self._subject

    @subject.setter
    def subject(self, value):
        self._subject = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def long_description(self):
        return self._long_description

    @long_description.setter
    def long_description(self, value):
        self._long_description = value

    @property
    def calculations_necessary(self):
        return [str(cal) for cal in self._calculations_necessary.split(';')]

    @calculations_necessary.setter
    def calculations_necessary(self, value_list):
        self._calculations_necessary = ';'.join(value_list)
    
    @property
    def vid(self):
        return self._vid
    
    @vid.setter
    def vid(self, value):
        self._vid = value

    def save(self):
        db.session.add(self)
        self = FinancialJargon.__remove_special_characters(self)
        db.session.commit()

    def update(self):
        self = FinancialJargon.__remove_special_characters(self)
        db.session.commit()

    def __repr__(self):
        return (f'Financial Term(term id (tid): {self.tid}, Full Term: {self.subject}, description: {self.description}, synonyms: {self.synonyms})')

    @classmethod
    def find_by_subject(cls, subject) -> FinancialJargon:
        term = cls.query.filter(func.lower(cls._subject) == func.lower(subject)).first()
        if term:
            return FinancialJargon.__remove_special_characters(term, True)
        else:
            return term
    
    @classmethod
    def get_all_terms(cls) -> list[FinancialJargon]:
        terms = cls.query.all()
        return [FinancialJargon.__remove_special_characters(t, True) for t in terms]
    
    @classmethod
    def get_term_by_id(cls, id) -> FinancialJargon:
        term = cls.query.filter_by(tid=id).first()
        return FinancialJargon.__remove_special_characters(term, True)


    # helper function
    @staticmethod
    def __remove_special_characters(term, update_in_db=False):
        """
        replaces special_chars (as defined in the function) by " ", and replaces "&" by "and". this helps the speech to text module identify the words better, by cleaning them of special characters.
        """
        # replace "&" by "and"

        # defining a set of characters that will be removed from the subject names and the synonyms, before saving to db
        special_chars = ["-", "_", "\"", "'", "(", ")", ".", ":", ";", "/", "#", "*"]

        # remove from subject
        for i in special_chars:
            term.subject = term.subject.replace(i, " ")
        term.subject = term.subject.replace("&", "and")

        # remove from all synonyms
        for k, syn in enumerate(term.synonyms):
            for i in special_chars:
                term.synonyms[k] = term.synonyms[k].replace(i, " ")
            term.synonyms[k] = term.synonyms[k].replace("&", "and")

        if update_in_db:
            term.update()

        return term
