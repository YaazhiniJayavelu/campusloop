import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'change-this-later'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'campusloop.db')
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024