import os
from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from shop.admin.forms import RegistrationForm, LoginForm, ResetRequestForm, ChangePasswordForm
from shop import db, bcrypt, oauth, mail
from shop.admin.models import User
from shop.products.models import AddProduct, Brand, Category
from flask_login import login_required, current_user, login_user, logout_user
from flask_oauthlib.client import OAuthException
from flask_mail import Message
import mimetypes
from email.utils import make_msgid


admin = Blueprint("admin", __name__)


google = oauth.remote_app(
    'google',
    consumer_key='1059616331280-o192fo386aq3dpcac5lv51qjjkt0lvov.apps.googleusercontent.com',
    consumer_secret='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', 
    request_token_params={
        'scope': 'email',
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
)

@admin.route('/')
@login_required
def home():
    if 'email' not in session:
        flash("Please login first", 'danger')
        return redirect(url_for('admin.login'))
    products = AddProduct.query.all()
    return render_template('admin/index.html', title="Home Page", products=products)

@admin.route('/brands')
def brands():
    if 'email' not in session:
        flash("Please login first", 'danger')
        return redirect(url_for('admin.login'))
    brands = Brand.query.order_by(Brand.id.desc()).all()
    return render_template('admin/brand_category.html', title="Brand Page", brands=brands)

@admin.route('/category')
def category():
    if 'email' not in session:
        flash("Please login first", 'danger')
        return redirect(url_for('admin.login'))
    categories = Category.query.order_by(Category.id.desc()).all()
    return render_template('admin/brand_category.html', title="Category Page", categories=categories)

@admin.route('/login/google')
def login_google():
    return google.authorize(callback=url_for('admin.authorized_google', _external=True))

@admin.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        # If no existing user, proceed to create a new user
        hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, username=form.username.data, email=form.email.data,
                    password=hash_password)
        try:
            db.session.add(user)
            db.session.commit()
            flash(f' Welcome {form.name.data} Thanks for registering', 'success')
            return redirect(url_for('admin.login'))
        except Exception as e:
            flash(f'User registration failed: {str(e)}', 'danger')
            return render_template('admin/register.html', form=form, title="Registration Page")

    return render_template('admin/register.html', form=form, title="Registration Page")

@admin.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.home'))
    
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                session['email'] = form.email.data
                login_user(user)
                flash(f'Welcome, {form.email.data}! You have successfully logged in.', 'success')
                return redirect(request.args.get('next') or url_for('admin.home'))
            else:
                flash(" User does not exist.", 'danger')
                return render_template('admin/login.html', form=form, title="Login Page")
        except Exception as e:
            flash(f'User login failed: {str(e)}', 'danger')

    return render_template('admin/login.html', form=form, title="Login Page")

@admin.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('admin.login'))

@admin.route('/login/authorized_google')
def authorized_google():
    try:
        response = google.authorized_response()
        access_token = response.get('access_token')
        if response is None or access_token is None:
            print("Yes")
            flash('Access denied: reason={} error={}'.format(
                request.args['error_reason'],
                request.args['error_description']
            ), 'danger')
            return redirect(url_for('admin.login'))
    except OAuthException as e:
        print(f'OAuthException: {e}')

    session['google_token'] = (response['access_token'], '')
    user_info = google.get('userinfo', token=access_token)
    print("user_info", user_info)
    user = User.query.filter_by(email=user_info.data['email']).first()

    if user is None:
        # You might want to create a new user here if it doesn't exist
        flash('User not registered. Please register.', 'warning')
        return redirect(url_for('admin.register'))

    login_user(user)
    flash(f'Welcome, {user.email}! You have successfully logged in.', 'success')
    return redirect(request.args.get('next') or url_for('admin.home'))

def send_mail(user):
    token = user.get_token()
    reset_link = url_for('admin.reset_token', token=token, _external=True)

    subject = 'Password Reset Request'
    recipients = [user.email]
    sender = 'anurag.iitian07@gmail.com'

    # Create a MIMEMultipart message
    msg = Message(subject, recipients=recipients, sender=sender)
    html_body = f'''
        <p>To reset your password, please follow the link below:</p>
        <p><a href="{reset_link}">{reset_link}</a></p>
        <p>If you didn't send a password reset request, please ignore this message.</p>
    '''

    # Attach the image as an inline attachment
    img_path = 'D:\E-Shopper\Flask-Ecommerce-Store\shop\static\images\home\logo.png'
    mime_type, _ = mimetypes.guess_type(img_path)
    if mime_type:
        with open(img_path, 'rb') as img_file:
            try:
                msg.attach(filename='logo.png', data=img_file.read(), content_type=mime_type)
                # Set the Content-ID for the inline image
                img_cid = make_msgid(domain='example.com')[1:-1]
                html_body = html_body.replace('src="cid:logo"', f'src="cid:{img_cid}"')
            except AttributeError:
                # Handle the case where content_type is None or doesn't have split method
                pass

    msg.html = html_body
    mail.send(msg)

@admin.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    form = ResetRequestForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_mail(user)
            flash(f'Reset link has been sent. Check your email', 'success')
            return redirect(url_for('admin.login'))
    return render_template('admin/reset_password.html', title='Reset Password Page', form=form)

@admin.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    user = User.verify_token(token)
    if user is None:
        flash('That is invalid token. Please try again', 'warning')
        return redirect(url_for('admin.reset_password'))
    
    form = ChangePasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        hash_password = bcrypt.generate_password_hash(form.new_password1.data).decode('utf-8')
        user.password = hash_password
        db.session.commit()
        flash('Password changed successfully. Please Login', 'success')
        return redirect(url_for('admin.login'))
    return render_template('admin/change_password.html', title='Set Password Form', form=form)