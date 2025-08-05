from flask import Flask
from .models import db
from flask_restful import Api
from .controllers.user import Register_User, Login_User
from .controllers.books import AddBook, BookList, Get_Specific_User_Books
import logging
import os
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration


def create_app():
    app = Flask(__name__)

    sentry_sdk.init(
        dsn="https://d1c582eb647a15d6ab18ebe6ed6613e2@o4509763108536320.ingest.us.sentry.io/4509763112730624",
        integrations=[FlaskIntegration(
            transaction_style="url",
            http_methods_to_capture=("GET", "POST", "PATCH", "DELETE"),
        )],
        traces_sample_rate=1.0,
        send_default_pii=True,
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bookstore.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["LOG_FILE"] = "logs/bookstore.log"

    if not os.path.exists("logs"):
        os.makedirs("logs")

    logging.basicConfig(
        filename=app.config["LOG_FILE"],
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    logging.info("Starting the Bookstore application")

    db.init_app(app)

    api = Api(app)

    user_prefix = "/api/v1/user"
    book_prefix = "/api/v1/book"

    api.add_resource(Register_User, f"/{user_prefix}/create_user")
    api.add_resource(Login_User, f"/{user_prefix}/login_user")
    api.add_resource(AddBook, f"/{book_prefix}/add_book")
    api.add_resource(BookList, f"/{book_prefix}/all_books")
    api.add_resource(Get_Specific_User_Books,
                     f"/{book_prefix}/user_books/<int:userId>")

    with app.app_context():
        # db.drop_all()
        db.create_all()

    return app   
    
