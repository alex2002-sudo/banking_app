import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:mydream@localhost:5432/banking_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
