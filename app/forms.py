from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, BooleanField, PasswordField, TextAreaField, SubmitField, IntegerField, RadioField, SelectField
from wtforms.validators import ValidationError, InputRequired, DataRequired, Email, EqualTo, Length
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from app.models import User, Client, Teacher

class InquiryForm(FlaskForm):
    first_name = StringField('First name', render_kw={"placeholder": "First name"}, \
        validators=[InputRequired()])
    email = StringField('Email address', render_kw={"placeholder": "Email address"}, \
        validators=[InputRequired(), Email(message="Please enter a valid email address")])
    phone = StringField('Phone number (optional)', render_kw={"placeholder": "Phone number (optional)"})
    subject = StringField('Subject', render_kw={'placeholder': 'Subject'}, default='Message')
    message = TextAreaField('Message', render_kw={"placeholder": "Message"}, \
        validators=[InputRequired()])
    submit = SubmitField('Submit')


class SignupForm(FlaskForm):
    email = StringField('Email address', render_kw={"placeholder": "Email address"}, \
        validators=[InputRequired(), Email(message="Please enter a valid email address")])
    first_name = StringField('First name', render_kw={"placeholder": "First name"}, \
        validators=[InputRequired()])
    last_name = StringField('Last name', render_kw={"placeholder": "Last name"}, \
        validators=[InputRequired()])
    password = PasswordField('Password', render_kw={"placeholder": "Password"}, \
        validators=[InputRequired()])
    password2 = PasswordField('Repeat Password', render_kw={"placeholder": "Repeat Password"}, \
        validators=[InputRequired(), EqualTo('password',message="Passwords do not match.")])
    submit = SubmitField('Join the movement')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('This email address has already been registered.')


class LoginForm(FlaskForm):
    email = StringField('Email address', render_kw={"placeholder": "Email address"}, \
        validators=[InputRequired(), Email(message="Please enter a valid email address")])
    password = PasswordField('Password', render_kw={"placeholder": "Password"}, \
        validators=[InputRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log in')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', render_kw={'placeholder': 'New password'}, \
        validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', render_kw={'placeholder': 'Verify password'}, \
        validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Save password')


class RequestPasswordResetForm(FlaskForm):
    email = StringField('Email address', render_kw={'placeholder': 'Email address'}, \
        validators=[InputRequired(), Email(message='Please enter a valid email address')])
    submit = SubmitField('Request password reset')


def get_teachers():
    return Teacher.query

def teacher_name(Teacher):
    return Teacher.first_name + " " + Teacher.last_name

class ClientForm(FlaskForm):
    first_name = StringField('First name', render_kw={"placeholder": "First name *"}, \
        validators=[InputRequired()])
    last_name = StringField('Last name', render_kw={"placeholder": "Last name"})
    email = StringField('Client Email address', render_kw={"placeholder": "Email address *"}, \
        validators=[InputRequired(), Email(message="Please enter a valid email address")])
    phone = StringField('Phone number', render_kw={'placeholder': 'Phone number'})
    status = SelectField('Status', choices=[('active', 'Active'),('inactive','Inactive')], \
        validate_choice=False)
    notes = TextAreaField('Notes', render_kw={'placeholder': 'Notes', 'rows': '3'})
    submit = SubmitField('Save')


class TeacherForm(FlaskForm):
    first_name = StringField('First name', render_kw={"placeholder": "First name"}, \
        validators=[InputRequired()])
    last_name = StringField('Last name', render_kw={"placeholder": "Last name"}, \
        validators=[InputRequired()])
    email = StringField('Email address', render_kw={"placeholder": "Email address"})
    timezone = IntegerField('Timezone', render_kw={"placeholder": "Timezone"}, \
        validators=[InputRequired()])
    status = SelectField('Status', choices=[('active', 'Active'),('paused','Paused'),('inactive','Inactive')])
    submit = SubmitField('Save')
