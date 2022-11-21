from flask import Blueprint
from flask_jwt_extended import get_jwt_identity

from Groot.Database.models.ClientAdvisorModel import ClientAdvisor
from Groot.Services.AuthService.AuthAnnotator import admin_advisor_required
from Groot.Services.StatisticsService.StatisticsService import StatisticService

bp = Blueprint('statistics', __name__)


@bp.route("/statistics", methods=["GET"])
@admin_advisor_required()
def get_statistics():
    """
    the return object looks like this:
    {
    "message": "Retrieving the statistics was successful",
    "stats": [
        {
                "asset": 4500000.0,
                "client_type": "PROFESSIONAL",
                "currency": "CHF",
                "email": "mike@tyson.io",
                "firstname": "Mike",
                "lastname": "Tyson",
                "nr_of_sessions": 2,
                "sessions": [
                    {
                        "advisor": "admin",
                        "date": "Tue, 21 Jun 2022 16:12:09 GMT",
                        "duration": 0.7175566666666667,
                        "sentiment": "POSITIVE",
                        "sentiment_quality": 0.9918572902679443,
                        "session_id": 1,
                        "summary": [
                            {
                                "description": "Stocks are of two types—common and preferred. The difference is while the holder of the former has voting rights that can be exercised in corporate decisions, the later doesn't. However, preferred shareholders are legally entitled to receive a certain level of dividend payments before any dividends can be issued to other shareholders.",
                                "title": "Stock"
                            }
                        ],
                        "transcript": "    Hello, Hello.    Can you show me stocks and ponds.   That's it. "
                    },
                ]
            },
        ]
    }
    """
    username = get_jwt_identity()

    advisor = ClientAdvisor.find_by_username(username)
    return StatisticService.get_statistics(advisor)
