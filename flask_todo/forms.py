from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, PasswordField
from wtforms.validators import Email, DataRequired, Length, EqualTo


class LoginForm(FlaskForm):
    email = StringField('email: ', validators=[Email()])
    password = PasswordField('password: ', validators=[DataRequired(), Length(min=4, max=30)])
    remember = BooleanField('remember: ', default=False)
    submit = SubmitField('Enter')


class RegisterForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    email = StringField('email: ', validators=[Email()])
    password = PasswordField('password: ', validators=[DataRequired(), Length(min=4, max=30)])
    password2 = PasswordField(
        'confirm password: ', validators=[DataRequired(), EqualTo(
            'password', message='password  and password  confirm must be the same')])
    submit = SubmitField('register')
