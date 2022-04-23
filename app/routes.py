import os
from flask import Flask, render_template, flash, Markup, redirect, url_for, request, send_from_directory
from app import app, db
from app.forms import InquiryForm, SignupForm, LoginForm, StudentForm, TeacherForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Student, Teacher
from werkzeug.urls import url_parse
from datetime import datetime
from app.email import send_contact_email

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_viewed = datetime.utcnow()
        db.session.commit()

def dir_last_updated(folder):
    return str(max(os.path.getmtime(os.path.join(root_path, f))
                   for root_path, dirs, files in os.walk(folder)
                   for f in files))

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
        return redirect(url_for('home'))
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
        flash('You are already signed in')
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('students')
        return redirect(next_page)
    return render_template('login.html', title="Login", form=form)

@app.route('/students', methods=['GET', 'POST'])
@login_required
def students():
    form = StudentForm()
    students = Student.query.order_by(Student.first_name).all()
    statuses = Student.query.with_entities(Student.status).distinct()
    if form.validate_on_submit():
        student = Student(first_name=form.first_name.data, last_name=form.last_name.data, \
        email=form.email.data, timezone=form.timezone.data, \
        location=form.location.data, status=form.status.data, teacher=form.teacher_id.data)
        try:
            db.session.add(student)
            db.session.commit()
        except:
            db.session.rollback()
            flash(student.first_name + ' could not be added', 'error')
            return redirect(url_for('students'))
        flash(student.first_name + ' added')
        return redirect(url_for('students'))
    return render_template('students.html', title="Students", form=form, students=students, statuses=statuses)

@app.route('/edit_student/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_student(id):
    form = StudentForm()
    student = Student.query.get_or_404(id)
    if form.validate_on_submit():
        if 'save' in request.form:
            student.first_name=form.first_name.data
            student.last_name=form.last_name.data
            student.email=form.email.data
            student.timezone=form.timezone.data
            student.location=form.location.data
            student.status=form.status.data
            student.teacher=form.teacher_id.data
            try:
                db.session.add(student)
                db.session.commit()
                flash(student.first_name + ' updated')
            except:
                db.session.rollback()
                flash(student.first_name + ' could not be updated', 'error')
                return redirect(url_for('students'))
            finally:
                db.session.close()
        elif 'delete' in request.form:
            db.session.delete(student)
            db.session.commit()
            flash('Deleted ' + student.first_name)
        else:
            flash('Code error in POST request', 'error')
        return redirect(url_for('students'))
    elif request.method == "GET":
        form.first_name.data=student.first_name
        form.last_name.data=student.last_name
        form.email.data=student.email
        form.timezone.data=student.timezone
        form.location.data=student.location
        form.status.data=student.status
        form.teacher_id.data=student.teacher
    return render_template('edit-student.html', title='Edit Student',
                           form=form, student=student)


@app.route('/teachers', methods=['GET', 'POST'])
@login_required
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
        return redirect(url_for('teachers'))
    return render_template('teachers.html', title="Teachers", form=form, teachers=teachers, statuses=statuses)

@app.route('/edit_teacher/<int:id>', methods=['GET', 'POST'])
@login_required
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
def signup():
    if current_user.is_authenticated:
        flash('You are already signed in')
        return redirect(url_for('home'))
    form = SignupForm()
    if form.validate_on_submit():
        username_check = User.query.filter_by(username=form.email.data).first()
        if username_check is not None:
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

@app.route('/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('profile.html', user=user, posts=posts)

@app.route('/robots.txt')
@app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])
