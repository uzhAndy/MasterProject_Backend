# here we import libraries
from dataclasses import dataclass

from Groot.Extensions.DatabaseExtension import db


# here, we import extensions


@dataclass
class Queue(db.Model):

    uuid: int
    client_advisor: str
    terms: list[str]

    uuid = db.Column(db.Integer, primary_key=True)
    client_advisor = db.Column(db.String(50), unique=True, nullable=False)
    _terms = db.Column(db.String, default="")

    @property
    def terms(self):
        return [] if self._terms is None else [str(term) for term in self._terms.split(';')]

    @terms.setter
    def terms(self, value_list):
        if len(value_list) == 0:
            self._terms = None
            return

        max_length = 5
        if self._terms is None:
            self._terms = ""
        else:
            self._terms += ";"

        # if the list is already too long
        if self._terms != "" and len(self.terms) + len(value_list)>= max_length + 2:

            current_terms = [str(term) for term in self._terms.split(';')]
            current_terms = current_terms[:-1]

            for new_term in value_list:
                current_terms.pop(0)
                current_terms.append(new_term.strip().lower())

            self._terms = ";".join([term for term in current_terms])
        else:
            self._terms += ";".join([term.strip().lower() for term in value_list])


    def check_if_exists(self, existing_terms):
        non_redundant_terms = []
        for new_term in self.terms:
            if not new_term in existing_terms:
                non_redundant_terms.append(new_term)
        return non_redundant_terms


    def save(self):
        # test if Queue for this user exists
        if db.session.query(Queue.uuid).filter_by(client_advisor=self.client_advisor).scalar():
            # get existing queue from this advisor/user
            queue_advisor = Queue.query.filter_by(client_advisor=self.client_advisor).first()

            non_redundant_terms = self.check_if_exists(queue_advisor.terms)

            if len(non_redundant_terms) == 0:
                # return the existing queue and the has_been_updated_flag: false
                return queue_advisor, False

            queue_advisor.terms = self.terms
            db.session.commit()
            return queue_advisor, True
        else:
            db.session.add(self)
            db.session.commit()
            return self, True


    def clear_all(self):
        # test if Queue for this user exists
        if db.session.query(Queue.uuid).filter_by(client_advisor=self.client_advisor).scalar():
            queue_advisor = Queue.query.filter_by(client_advisor=self.client_advisor).first()

            queue_advisor.terms = []
            db.session.commit()
            return queue_advisor, True

        return _, False

    def __repr__(self):
        return (f'Currently in queue for {self.client_advisor} is {self.terms}')
