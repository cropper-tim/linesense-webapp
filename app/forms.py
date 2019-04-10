from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import InputRequired, Email, EqualTo, ValidationError
from app.models import Customer


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign in")


class CreateAccount(FlaskForm):
    f_name = StringField("First Name", validators=[InputRequired()])
    l_name = StringField("Last Name", validators=[InputRequired()])
    username = StringField("Username", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField('Password', [InputRequired(), EqualTo(
        'confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm Password')
    submit = SubmitField("Create Account")

    def validate_username(self, username):
        user = Customer.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("That username is already taken.")
    
    def validate_email(self, email):
        user = Customer.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("That email is already registered to a user.")