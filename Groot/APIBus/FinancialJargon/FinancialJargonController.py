from flask import Blueprint, request

from Groot.Services.FinancialJargonService.FinancialJargonService import FinancialJargonService

bp = Blueprint('financialJargon', __name__)


@bp.route('/terms', methods=['POST', 'PUT', 'GET'])
def add_term():
    """
    --- GET ---
    the return object looks like this:
    {
        "message": "Successfully requested all terms",
        "terms": [
            {
                "description": "...",
                "long_description": "...",
                "subject": "Bond",
                "synonyms": [
                    ""
                ]
            },
            {
                "description": "Cryptocurrency is...",
                "long_description": "Cryptocurrency received...",
                "subject": "Crypto Currency",
                "synonyms": [
                    "digital currency",
                    "gold 2.0"
                ]
            }
        ]
    }

    --- POST ---
    the body should look the following:
    {
        "subject": "{{termName}}",
        "description": "{{$randomJobDescriptor}}",
        "long_description": "{{$randomCatchPhraseDescriptor}}",
        "synonyms": ["{{$randomProductName}}"]
    }

    the return object looks like this:
    {
        "message": "Successfully added Financial Term(term id (tid): 20, Full Term: Intelligent Rubber Chair, description: Regional, synonyms: ['handcrafted rubber shoes']) to database."
    }

    --- PUT ---
    the body should look the following:
    {
        "subject": "{{termName}}",
        "description": "{{$randomJobDescriptor}}",
        "long_description": "{{$randomCatchPhraseDescriptor}}",
        "synonyms": ["{{$randomProductName}}"]
    }

    the return object looks like this:
    {
        "message": "Successfully updated term: Intelligent Rubber Chair to: Financial Term(term id (tid): 20, Full Term: Intelligent Rubber Chair, description: International, synonyms: ['handcrafted metal shirt'])."
    }
    """
    args = request.args
    if request.method == 'GET':
        return FinancialJargonService.get_terms(args)
    else:
        new_term = request.get_json()
        subject = new_term['subject']
        description = new_term['description']
        long_description = new_term['long_description']
        synonyms = new_term['synonyms']
        if request.method == 'POST':
            return FinancialJargonService.add_new_term(subject, description, long_description, synonyms)
        elif request.method == 'PUT':
            return FinancialJargonService.edit_term(subject, description, long_description, synonyms)
