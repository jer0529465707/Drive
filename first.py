from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///drive.db'
    # additional configuration settings

    db.init_app(app)

    with app.app_context():
        db.create_all()

    return app

create_app()
