from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from shop.admin.forms import RegistrationForm, LoginForm
from shop import db, bcrypt
from shop.admin.models import User
from flask_login import login_required, current_user, login_user, logout_user


admin = Blueprint("admin", __name__)

@admin.route('/')
@login_required
def home():
    return render_template('admin/index.html', title="Admin Page")

@admin.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, username=form.username.data, email=form.email.data,
                    password=hash_password)
        try:
            db.session.add(user)
            db.session.commit()
            flash(f' Welcome {form.name.data} Thanks for registering', 'success')
            return redirect(url_for('admin.login'))
        except Exception as e:
            flash(f'Error registering user: {str(e)}', 'danger')
    return render_template('admin/register.html', form=form, title="Registration Page")

@admin.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.home'))
    
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session['email'] = form.email.data
            login_user(user)
            flash(f'Welcome, {form.email.data}! You have successfully logged in.', 'success')
            return redirect(request.args.get('next') or url_for('admin.home'))
        else:
            flash("Login failed. Please check your email and password.", 'danger')
    return render_template('admin/login.html', form=form, title="Login Page")

@admin.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('admin.login'))