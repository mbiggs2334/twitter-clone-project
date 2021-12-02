from re import S
from flask.app import Flask
from flask_wtf import FlaskForm
from models import User
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length



class MessageForm(FlaskForm):
    """Form for adding/editing messages."""

    text = TextAreaField('text', validators=[DataRequired()])


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Profile image URL')


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class EditProfileForm(FlaskForm):
    """Form to edit profile."""
    
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired()])
    image_url = StringField('(Optional) Profile image URL')
    header_image_url = StringField('(Optional) Header image URL')
    bio = TextAreaField('Bio', )
    password = PasswordField('Password')
