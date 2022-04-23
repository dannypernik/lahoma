from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, BooleanField, PasswordField, TextAreaField, SubmitField, IntegerField, RadioField, SelectField
from wtforms.validators import ValidationError, InputRequired, DataRequired, Email, EqualTo, Length
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from app.models import User, Student, Teacher

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


def get_tutors():
    return Tutor.query

def tutor_name(Tutor):
    return Tutor.first_name + " " + Tutor.last_name

class StudentForm(FlaskForm):
    first_name = StringField('First name', render_kw={"placeholder": "First name"}, \
        validators=[InputRequired()])
    last_name = StringField('Last name', render_kw={"placeholder": "Last name (optional)"})
    email = StringField('Student Email address', render_kw={"placeholder": "Student Email address"}, \
        validators=[InputRequired(), Email(message="Please enter a valid email address")])
    timezone = IntegerField('Timezone', render_kw={"placeholder": "Timezone"}, \
        validators=[InputRequired()])
    location = StringField('Location', render_kw={"placeholder": "Location"}, \
        validators=[InputRequired()])
    status = SelectField('Status', choices=[('active', 'Active'),('paused','Paused'),('inactive','Inactive')])
    teacher_id = QuerySelectField('Tutor', default=1, query_factory=get_tutors, get_label=tutor_name, \
        validators=[InputRequired()])
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
