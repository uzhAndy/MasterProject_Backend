import logging, logging.config, yaml
from datetime import timedelta
from flask_cors import CORS

from datetime import timedelta
from sqlalchemy_utils import database_exists
from Groot.Database.Scripts.init_db import init_db_command, load_shcl_data

# import extensions
from Groot.Extensions.DatabaseExtension import db, jwt, cors, socket_io, app

# all imports regarding other files of the application
from Groot.APIBus.Authentication import LoginController, RegistrationController, EditUserController
from Groot.APIBus.UserManagement import UserManagementController
from Groot.APIBus.Consultation import ConsultationController, ConsultationAdministration
from Groot.APIBus.FinancialJargon import FinancialJargonController
from Groot.APIBus.Consultation import VisualizationController
from Groot.APIBus.Statistics import StatisticsController


# configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Groot-Database.db?check_same_thread=False'
app.config["JWT_SECRET_KEY"] = "Groot"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
CORS(app)

def create_app():

    # This API is to learn/understand/test APIs
    @app.route('/api', methods=['GET'])
    def hello_world_example():
        return {"message": "Displays Hello World Main Server Here man"}, 200

    @socket_io.on('my_event')
    def handle_my_custom_namespace_event(json):
        print("here")
        print('received json: ' + str(json))
        return "working", 2

    # logging
    logging.config.dictConfig(yaml.safe_load(open('Groot/Logging/config/logging.conf')))

    # only log the errors from the werkzeug extension
    # log_werkzeug = logging.getLogger('werkzeug')
    # log_werkzeug.setLevel(logging.ERROR)


    # register all API controllers which are part of the API Bus
    app.register_blueprint(LoginController.bp)
    app.register_blueprint(RegistrationController.bp)
    app.register_blueprint(UserManagementController.bp)
    app.register_blueprint(EditUserController.bp)
    app.register_blueprint(ConsultationController.bp)
    app.register_blueprint(FinancialJargonController.bp)
    app.register_blueprint(ConsultationAdministration.bp)
    app.register_blueprint(StatisticsController.bp)

    # register all extensions
    register_extensions(app)

    # register new command line commands
    app.cli.add_command(init_db_command)
    app.cli.add_command(load_shcl_data)

    return app


def register_extensions(app):
    jwt.init_app(app)
    # cors.init_app(app=app, origins=["http://localhost:3000/*"])
    db.init_app(app)

    socket_io.init_app(app, cors_allowed_origins="*")

    # create database if it does not exist
    if not database_exists('sqlite:///Groot/Groot-Database.db'):
        print(" * Creating Database")
        with app.app_context():
            db.create_all(app=app)


