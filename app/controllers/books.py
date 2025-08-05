from flask_restful import Resource, reqparse
from ..models import User, Book, db
from flask import request
from app.config import *
from cloudinary import uploader
import random
from flask import current_app
import sentry_sdk


class AddBook (Resource):
    def post(self):

        title = request.form.get("title")
        price = request.form.get("price")
        username = request.form.get("username")
        image_file = request.files.get("book_cover")

        if not image_file:
            current_app.logger.error("Book cover image is required")
            sentry_sdk.capture_message(
                "Book cover image is required", level='error')
            return {"message": "Book cover image is required"}, 400

        try:
            upload_result = uploader.upload(image_file)
            book_cover_url = upload_result.get("secure_url")
        except Exception as e:
            current_app.logger.error(f"Image upload failed: {str(e)}")
            sentry_sdk.capture_exception(e)
            return {"message": "Image fail to upload", "error": str(e)}, 500

        user = User.query.filter_by(username=username).first()

        if not user:
            current_app.logger.error(f"User {username} not found")
            sentry_sdk.capture_message(
                f"User {username} not found", level='error')
            return {"message": "User not found"}, 404

        part1 = random.randint(1000, 9999)
        part2 = random.randint(1000, 9999)
        part3 = random.randint(1000, 9999)
        part4 = random.randint(1000, 9999)

        isbn_number = f"{part1}-{part2}-{part3}-{part4}"

        book = Book(title=title, price=price,
                    user_id=user.id, ISBN=isbn_number, book_cover=book_cover_url)
        db.session.add(book)
        db.session.commit()

        current_app.logger.info(f"New book added: {title} by {username}")
        sentry_sdk.capture_message(
            f"New book added: {title} by {username}", level='info')
        return {"message": "New book added success", "data": {
            "title": book.title,
            "price": book.price,
            "ISBN": book.ISBN,
            "book_cover": book.book_cover
        }}, 200


class BookList (Resource):
    def get(self):
        books = Book.query.all()

        current_app.logger.info("Returning all available books")
        sentry_sdk.capture_message(
            "Returning all available books", level='info')

        if not books:
            current_app.logger.info("No books available")
            return {"message": "No books available"}, 404

        current_app.logger.info(f"Found {len(books)} books")
        sentry_sdk.capture_message(
            f"Found {len(books)} books", level='info')
        # sentry_sdk.debug(f"Books: {[book.title for book in books]}")
        return {"message": "All available books returned", "data": [{
            "id": book.id,
            "title": book.title,
            "ISBN": book.ISBN,
            "price": book.price,
            "author": book.user.username
        } for book in books]}, 200


class Get_Specific_User_Books(Resource):

    def get(self, userId):
        user = User.query.get(userId)

        if not user:
            current_app.logger.error(f"User with ID {userId} does not exist")
            return {"message": "User does not exist"}, 404

        books = Book.query.filter_by(user_id=user.id).all()

        if not books:
            sentry_sdk.capture_message(
                f"No books found for user {user.username}", level='error')
            current_app.logger.info(f"No books found for user {user.username}")
            return {"message": "no books found for this user"}, 404

        sentry_sdk.capture_message(
            f"Found {len(books)} books for user {user.username}", level='info')
        current_app.logger.info(
            f"Found {len(books)} books for user {user.username}")
        return {"message": "user books found", "data": [{
                "id": book.id,
                "title": book.title,
                "ISBN": book.ISBN,
                "price": book.price
                } for book in books]}, 200      
    