from flask_restful import Resource, reqparse
from app.models import User, db
from flask import current_app
import sentry_sdk


class Register_User (Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('username', type=str, required=True,
                        help="Username is required")
    parser.add_argument('password', type=str, required=True,
                        help="Password is required")
    parser.add_argument('email', type=str, required=True,
                        help="email is required")

    def post(self):
        data = Register_User.parser.parse_args()

        if User.query.filter_by(username=data['username']).first():
            current_app.logger.info(
                f"User registration failed: {data['username']} already exists")
            sentry_sdk.capture_message(
                f"User registration failed: {data['username']} already exists")
            return {"message": "User already exists"}, 400
        new_user = User(
            username=data["username"], password=data["password"], email=data["email"])
        db.session.add(new_user)
        db.session.commit()

        sentry_sdk.capture_message(
            f"User registered successfully: {data['username']}")
        current_app.logger.info(
            f"User registered successfully: {data['username']}")
        return {"message": "User registerd successfully"}


class Login_User (Resource):
    login_parser = reqparse.RequestParser()

    login_parser.add_argument('password', type=str,
                              required=True, help="Password is required")
    login_parser.add_argument(
        'email', type=str, required=True, help="email is required")

    def post(self):
        data = Login_User.login_parser.parse_args()

        user = User.query.filter_by(
            email=data['email'], password=data["password"]).first()

        if not user:
            sentry_sdk.capture_message(
                f"Login failed: User with email {data['email']} not found")
            current_app.logger.info(
                f"Login failed: User with email {data['email']} not found")
            return {"message": "User not found"}, 400

        sentry_sdk.capture_message(
            f"User logged in successfully: {data['email']}")
        current_app.logger.info(
            f"User logged in successfully: {data['email']}")
        return {"message": "User logged in successfully"}
            
        
        





