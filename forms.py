from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired


class RegisterForm(FlaskForm):
    """Form for registering a user"""

    name = StringField("Name", validators=[InputRequired()])

    username = StringField("Username", validators=[InputRequired()])

    password = PasswordField("Password", validators=[InputRequired()])


class LoginForm(FlaskForm):
    """Form for logging in a user"""

    username = StringField('Username', validators=[InputRequired()])

    password = PasswordField('Password', validators=[InputRequired()])


class TweetForm(FlaskForm):
    """Form for creating a new tweet"""

    text = TextAreaField("What do you have to say?",
                         validators=[InputRequired()])
