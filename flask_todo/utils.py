from flask_todo.models import Todo, User
from sqlalchemy import or_
from werkzeug.security import check_password_hash


class MyException(Exception):
    def __init__(self, message='ParentException'):
        super().__init__(message)


class NoUserPassword(MyException):
    def __init__(self, message='NoUserPassword'):
        super().__init__(message)


class Nodata(MyException):
    def __init__(self, message='NoData'):
        super().__init__(message)


def get_user(user_id):
    data = Todo.query.filter_by(user_id=user_id). \
        order_by(Todo.traffic).all()
    return data


def get_user_filter(user_id, status):
    data = Todo.query.filter_by(user_id=user_id). \
        filter_by(status=status).all()
    return data


def find_next_traffic() -> int:
    data = Todo.query.order_by(Todo.id.desc()).first()
    traffic = (data.id + 1) if data else 1
    return traffic


def get_data(display):
    return Todo.query.filter_by(traffic=display).first()


def get_move_in_front_data(data, current_user):
    if data:
        data_next = Todo.query.filter(Todo.user == current_user).\
            filter(Todo.traffic < data.traffic).\
            order_by(Todo.traffic.desc()).first()
    else:
        data_next = Todo.query.filter(Todo.user == current_user).\
            filter(Todo.traffic < data.traffic).\
            order_by(Todo.traffic.desc()).first()
    if data_next:
        return data_next
    raise Nodata


def get_move_back_data(data, current_user):
    if data:
        data_next = Todo.query.filter(Todo.user == current_user). \
            filter(Todo.traffic > data.traffic). \
            order_by(Todo.traffic).first()
    else:
        data_next = Todo.query.filter(Todo.user == current_user). \
            filter(Todo.traffic > data.traffic). \
            order_by(Todo.traffic).first()
    if data_next:
        return data_next
    raise Nodata


def get_user_email_password(email, password) -> User:
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        return user
    raise NoUserPassword


def check_user_name_email(name, email) -> bool:
    return bool(User.query.filter(or_(User.name == name, User.email == email)).first())

