from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(512))
    account_number = db.Column(db.String(20), unique=True)
    balance = db.Column(db.Float, default=0.0)
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic')
    accounts = db.relationship('BankAccount', backref='owner', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class BankAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(20), unique=True)
    account_type = db.Column(db.String(50))  # e.g., 'checking', 'savings'
    balance = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(3), default='USD')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    transactions = db.relationship('Transaction', backref='account', lazy='dynamic')

    def __repr__(self):
        return f'<Account {self.account_number}>'

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)
    description = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    transaction_type = db.Column(db.String(20))  # e.g., 'deposit', 'withdrawal', 'transfer'
    status = db.Column(db.String(20), default='completed')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    account_id = db.Column(db.Integer, db.ForeignKey('bank_account.id'))
    reference_id = db.Column(db.String(50), unique=True)

    def __repr__(self):
        return f'<Transaction {self.description} {self.amount}>'

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
