import os
from flask import Flask, render_template, flash, Markup, redirect, url_for, request, send_from_directory
from app import app, db
from app.forms import InquiryForm, SignupForm, LoginForm, ClientForm, TeacherForm, \
    RequestPasswordResetForm, ResetPasswordForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Client, Teacher
from werkzeug.urls import url_parse
from datetime import datetime
from app.email import send_contact_email, send_invite_email
from functools import wraps

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_viewed = datetime.utcnow()
        db.session.commit()

def dir_last_updated(folder):
    return str(max(os.path.getmtime(os.path.join(root_path, f))
                   for root_path, dirs, files in os.walk(folder)
                   for f in files))

def admin_required(f):
    @login_required
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.is_admin:
            return f(*args, **kwargs)
        else:
            flash('You must have administrator privileges to access this page.', 'error')
            logout_user()
            return redirect(url_for('login', next_url=request.url))
    return wrap


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    form = InquiryForm()
    if form.validate_on_submit():
        if hcaptcha.verify():
            pass
        else:
            flash('Please verify that you are human.', 'error')
            return render_template('home.html', form=form, last_updated=dir_last_updated('app/static'))
        user = User(first_name=form.first_name.data, email=form.email.data, phone=form.phone.data)
        message = form.message.data
        subject = form.subject.data
        db.session.add(user)
        db.session.commit()
        send_contact_email(user, message)
        print(app.config['ADMINS'])
        flash("Thank you for your message. We will be in touch!")
    return render_template('home.html', form=form, last_updated=dir_last_updated('app/static'))

@app.route('/iam')
def iam():
    return render_template('iam.html')

@app.route('/offerings')
def offerings():
    return render_template('offerings.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already signed in.')
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            if user.is_admin:
                next_page = url_for('clients')
            else:
                next_page = url_for('dashboard')
        return redirect(next_page)
    return render_template('login.html', title="Login", form=form)


@app.route('/request_password_reset/', methods=['GET', 'POST'])
def request_password_reset():
    form = RequestPasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            email = send_invite_email(user)
        flash('Check your inbox at ' + user.email + ' for instructions to reset your password.')
        return redirect(url_for('login'))
    return render_template('request-password-reset.html', title='Reset password', form=form)


@app.route('/set_password/<token>', methods=['GET', 'POST'])
def set_password(token):
    user = User.verify_email_token(token)
    if not user:
        flash('Verification has expired or is invalid. Please request a password reset.')
        return redirect(url_for('request_password_reset'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.status = 'active'
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Your password has been updated.')
        return redirect(url_for('dashboard'))
    return render_template('set-password.html', form=form)


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/clients', methods=['GET', 'POST'])
@admin_required
def clients():
    form = ClientForm()
    clients = User.query.order_by(User.first_name).filter_by(is_admin = False)
    statuses = ['active', 'unverified', 'inactive']
    if form.validate_on_submit():
        user = User(first_name=form.first_name.data, last_name=form.last_name.data, \
            email=form.email.data, phone=form.phone.data, notes=form.notes.data, \
            status='unverified')
        try:
            db.session.add(user)
            db.session.commit()
            email = send_invite_email(user)
            if email.status_code == 200:
                flash('Welcome email sent to ' + user.first_name)
            else:
                flash('Email failed to send with code ' + str(email.status_code) + str(email.reason), 'error')
        except:
            db.session.rollback()
            flash(user.first_name + ' could not be added', 'error')
            return redirect(url_for('clients'))
    return render_template('clients.html', title="Clients", form=form, clients=clients, statuses=statuses)

@app.route('/edit_client/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_client(id):
    form = ClientForm()
    client = User.query.get_or_404(id)
    if form.validate_on_submit():
        if 'save' in request.form:
            client.first_name=form.first_name.data
            client.last_name=form.last_name.data
            client.email=form.email.data
            client.phone=form.phone.data
            client.notes=form.notes.data
            client.status=form.status.data
            try:
                db.session.add(client)
                db.session.commit()
                flash(client.first_name + ' updated')
            except:
                db.session.rollback()
                flash(client.first_name + ' could not be updated', 'error')
                return redirect(url_for('clients'))
            finally:
                db.session.close()
        elif 'delete' in request.form:
            db.session.delete(client)
            db.session.commit()
            flash('Deleted ' + client.first_name)
        else:
            flash('Code error in POST request', 'error')
        return redirect(url_for('clients'))
    elif request.method == "GET":
        form.first_name.data=client.first_name
        form.last_name.data=client.last_name
        form.email.data=client.email
        form.phone.data=client.phone
        form.notes.data=client.notes
        form.status.data=client.status
    return render_template('edit-client.html', title='Edit Client',
                           form=form, client=client)


@app.route('/teachers', methods=['GET', 'POST'])
@admin_required
def teachers():
    form = TutorForm()
    teachers = Teacher.query.order_by(Teacher.first_name).all()
    statuses = Teacher.query.with_entities(Teacher.status).distinct()
    if form.validate_on_submit():
        teacher = Teacher(first_name=form.first_name.data, last_name=form.last_name.data, \
        email=form.email.data, timezone=form.timezone.data)
        try:
            db.session.add(teacher)
            db.session.commit()
        except:
            db.session.rollback()
            flash(teacher.first_name + ' could not be added', 'error')
            return redirect(url_for('teachers'))
        flash(teacher.first_name + ' added')
    return render_template('teachers.html', title="Teachers", form=form, teachers=teachers, statuses=statuses)

@app.route('/edit_teacher/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_teacher(id):
    form = TutorForm()
    teacher = Teacher.query.get_or_404(id)
    if form.validate_on_submit():
        if 'save' in request.form:
            teacher.first_name=form.first_name.data
            teacher.last_name=form.last_name.data
            teacher.email=form.email.data
            teacher.timezone=form.timezone.data
            teacher.status=form.status.data
            try:
                db.session.add(teacher)
                db.session.commit()
                flash(teacher.first_name + ' updated')
            except:
                db.session.rollback()
                flash(teacher.first_name + ' could not be updated', 'error')
                return redirect(url_for('teachers'))
            finally:
                db.session.close()
        elif 'delete' in request.form:
            db.session.delete(teacher)
            db.session.commit()
            flash('Deleted ' + teacher.first_name)
        else:
            flash('Code error in POST request', 'error')
        return redirect(url_for('teachers'))
    elif request.method == "GET":
        form.first_name.data=teacher.first_name
        form.last_name.data=teacher.last_name
        form.email.data=teacher.email
        form.timezone.data=teacher.timezone
        form.status.data=teacher.status
    return render_template('edit-teacher.html', title='Edit Tutor', form=form, teacher=teacher)


@app.route('/signup', methods=['GET', 'POST'])
@admin_required
def signup():
    if current_user.is_authenticated:
        flash('You are already signed in')
        return redirect(url_for('home'))
    form = SignupForm()
    if form.validate_on_submit():
        user_check = User.query.filter_by(email=form.email.data).first()
        if user_check is not None:
            flash('User already exists', 'error')
            return redirect(url_for('signup'))
        user = User(first_name=form.first_name.data, last_name=form.last_name.data, \
        email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("You are now registered. We're glad you're here!")
        return redirect(url_for('home'))
    return render_template('signup.html', title='Sign up', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/robots.txt')
@app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])
