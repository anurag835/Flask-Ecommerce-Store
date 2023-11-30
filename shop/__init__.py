from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

db = SQLAlchemy()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///myshop.db"
    app.config["SECRET_KEY"] = "jajskwenlkkhefi23"
    app.config['BCRYPT_LOG_ROUNDS'] = 12
    
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager = LoginManager(app)

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
    # Create the database tables
    with app.app_context():
        from shop.admin.models import User
        db.create_all()
    
    return app

    




    