from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from flask import Flask
from flask_login import LoginManager, UserMixin

app = Flask(__name__, template_folder='../templates')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config.update(dict(SECRET_KEY="powerful secretkey",
                       WTF_CSRF_SECRET_KEY="a csrf secret key"))
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


class BaseModel(db.Model):
    __abstract__ = True

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Todo(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    traffic = db.Column(db.Integer)
    status = db.Column(db.String(30))
    task = db.Column(db.String(500))
    date_created = db.Column(db.DateTime, default=datetime.now)
    done = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=True)
    user = relationship(
            'User', foreign_keys='Todo.user_id', backref='todo')


class User(UserMixin, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500))
    email = db.Column(db.String(50))
    password = db.Column(db.String)
    date_created_user = db.Column(db.DateTime, default=datetime.now)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


db.init_app(app)
db.create_all()
