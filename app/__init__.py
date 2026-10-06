from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    login_manager.init_app(app)

    from app.auth.routes import auth
    app.register_blueprint(auth)

    from app.lostfound.routes import lostfound
    app.register_blueprint(lostfound)

    from app import models
    with app.app_context():
        db.create_all()

    @app.route('/')
    def home():
        return render_template('index.html')

    return app