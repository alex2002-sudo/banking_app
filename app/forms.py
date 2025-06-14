from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DecimalField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, NumberRange

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class TransferForm(FlaskForm):
    recipient = StringField('Recipient Username', validators=[DataRequired()])
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    submit = SubmitField('Transfer')

from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class AccountForm(FlaskForm):
    account_type = SelectField('Account Type', 
                             choices=[('checking', 'Checking Account'), ('savings', 'Savings Account')],
                             validators=[DataRequired()])
    submit = SubmitField('Create Account')

from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class TransactionForm(FlaskForm):
    account_id = SelectField('Account', coerce=int, validators=[DataRequired()])
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    description = StringField('Description', validators=[DataRequired()])
    transaction_type = SelectField('Type', choices=[('deposit', 'Deposit'), ('withdrawal', 'Withdrawal')], validators=[DataRequired()])
    submit = SubmitField('Create Transaction')

class TransactionForm(FlaskForm):
    account_id = SelectField('Account', coerce=int, validators=[DataRequired()])
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    description = StringField('Description', validators=[DataRequired()])
    transaction_type = SelectField('Type', choices=[('deposit', 'Deposit'), ('withdrawal', 'Withdrawal')], validators=[DataRequired()])
    submit = SubmitField('Create Transaction')

