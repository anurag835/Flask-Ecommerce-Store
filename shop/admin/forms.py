from wtforms import Form, StringField, PasswordField, validators
from wtforms.validators import ValidationError
from shop.admin.models import User


class RegistrationForm(Form):
    name = StringField('Name', [validators.Length(min=4, max=25)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [
        validators.DataRequired(),
        validators.Length(min=6, max=35), validators.Email()])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password', [
        validators.DataRequired()
    ])

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(
                "That email is taken. Please choose a different email."
            )

class LoginForm(Form):
    email = StringField('Email Address', [
        validators.DataRequired(),
        validators.Length(min=6, max=35), validators.Email()])
    password = PasswordField('Enter Password', [validators.DataRequired()])

class ResetRequestForm(Form):
    email = StringField('Email Address', [
        validators.DataRequired(),
        validators.Length(min=6, max=35), validators.Email()])
    
class ChangePasswordForm(Form):
    new_password1 = PasswordField('New password', [validators.DataRequired()])
    new_password2 = PasswordField('New password Confirmation', [validators.DataRequired()])
