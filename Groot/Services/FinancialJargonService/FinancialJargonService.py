from Groot.Database.models.FinancialJargon import FinancialJargon
from Groot.Services.ResponseService.RequestResponseService import APIObjectsResponse


class FinancialJargonService:
    @staticmethod
    def add_new_term(subject, description, long_desc, synonyms):

        new_term = FinancialJargon(
            subject=subject, description=description, long_description=long_desc, synonyms=synonyms)

        if FinancialJargon.find_by_subject(subject) is None:
            # term has not been added yet => add term and give status update
            new_term.save()
            return APIObjectsResponse.create_generic_response(200, f'Successfully added {new_term} to database.')

        else:
            # return status code 406, 'term already exists, use change term'
            return APIObjectsResponse.create_generic_response(406,
                                                              f'Term already exists in the database. Please, select edit term to update data corresponding to {new_term}.')

    @staticmethod
    def get_terms(request_args):
        terms = []

        if request_args:
            terms = FinancialJargon.get_term_by_id(request_args['id'])
        else:
            terms = FinancialJargon.get_all_terms()

        return APIObjectsResponse.create_generic_data_response(200, 'Successfully requested all terms', 'terms', terms)

    @staticmethod
    def edit_term(subject, description, long_desc, synonyms):
        edit_term = FinancialJargon.find_by_subject(subject)
        if edit_term:
            edit_term.description = description
            edit_term.long_description = long_desc
            edit_term.synonyms = synonyms
            edit_term.save()
            return APIObjectsResponse.create_generic_response(200,
                                                              f'Successfully updated term: {subject} to: {edit_term}.')
        else:
            return APIObjectsResponse.create_generic_response(406,
                                                              f'Could not update term: {subject} as it does not exist.')
