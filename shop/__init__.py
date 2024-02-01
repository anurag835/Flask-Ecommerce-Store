from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_oauthlib.client import OAuth
from flask_mail import Mail
from flask_uploads import IMAGES, UploadSet, configure_uploads, patch_request_class
import os
from flask_migrate import Migrate


basedir = os.path.abspath(os.path.dirname(__file__))
# to run flask need to add: $env:FLASK_APP="run.py"
db = SQLAlchemy()
bcrypt = Bcrypt()
oauth = OAuth()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
photos = UploadSet('photos', IMAGES)


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///myshop.db"
    app.config["SECRET_KEY"] = "e598ca91-eb64-4ac2-a7bc-18a84596c2a1"
    app.config['BCRYPT_LOG_ROUNDS'] = 12
    app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg', 'gif'])
    app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'static/images')
    configure_uploads(app, photos)
    patch_request_class(app)

    # Set the 'secure' flag for session cookies
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'anuragss2311@gmail.com'
    app.config['MAIL_PASSWORD'] = 'dndy rgci menw cgev'

    db.init_app(app)
    bcrypt.init_app(app)
    oauth.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db) 

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except Exception as e:
            app.logger.error(f"Error loading user: {e}")
        return None

    login_manager.login_view = 'admin.login'
    
    from shop.admin.routes import admin
    app.register_blueprint(admin)

    from shop.products.routes import products
    app.register_blueprint(products, url_prefix='/products')

    from shop.admin.models import User
    from shop.products.models import Brand, Category, AddProduct
    # Create the database tables
    with app.app_context():
        for model in [User, Brand, Category, AddProduct]:
            table_name = model.__table__.name
            if table_name not in db.Model.metadata.tables:
                db.create_all(bind=[model])
    
    return app




    