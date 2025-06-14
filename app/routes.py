from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlparse
from app import db
from app.models import User, Transaction, BankAccount
from app.forms import RegistrationForm, LoginForm, TransferForm, TransactionForm, AccountForm
import random
import string

app = Blueprint('app', __name__)

@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('.dashboard'))
    return render_template('index.html', title='Welcome')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('.dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username already exists
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Username already exists. Please choose a different username.')
            return redirect(url_for('.register'))
            
        # Check if email already exists
        existing_email = User.query.filter_by(email=form.email.data).first()
        if existing_email:
            flash('Email address already registered. Please use a different email.')
            return redirect(url_for('.register'))
            
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('.login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's accounts
    accounts = current_user.accounts.all()
    
    # Get recent transactions
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.timestamp.desc()).limit(10).all()
    
    return render_template('dashboard.html', title='Dashboard', accounts=accounts, transactions=transactions)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('.dashboard')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('.index'))


@app.route('/account/<int:account_id>')
@login_required
def account_details(account_id):
    account = BankAccount.query.get_or_404(account_id)
    if account.user_id != current_user.id:
        flash('You do not have permission to view this account')
        return redirect(url_for('.dashboard'))
    
    transactions = Transaction.query.filter_by(account_id=account_id).order_by(Transaction.timestamp.desc()).limit(20).all()
    
    return render_template('account_details.html', title='Account Details', account=account, transactions=transactions)

@app.route('/account/new', methods=['GET', 'POST'])
@login_required
def create_account():
    form = AccountForm()
    
    if form.validate_on_submit():
        account_type = form.account_type.data
        if account_type not in ['checking', 'savings']:
            flash('Invalid account type')
            return redirect(url_for('.dashboard'))
            
        # Generate a unique account number
        while True:
            account_number = ''.join(random.choices(string.digits, k=10))
            if not BankAccount.query.filter_by(account_number=account_number).first():
                break
                
        account = BankAccount(
            account_number=account_number,
            account_type=account_type,
            user_id=current_user.id
        )
        
        db.session.add(account)
        db.session.commit()
        flash('Account created successfully!')
        return redirect(url_for('.dashboard'))
    
    return render_template('create_account.html', title='Create Account', form=form)

@app.route('/transaction/new', methods=['GET', 'POST'])
@login_required
def new_transaction():
    # Get user's accounts first
    accounts = current_user.accounts.all()
    
    # If no accounts exist, show a message and redirect
    if not accounts:
        flash('You need to create an account first!')
        return redirect(url_for('.dashboard'))
    
    # Initialize form after getting accounts
    form = TransactionForm()
    
    # Populate account choices
    form.account_id.choices = [(acc.id, f'{acc.account_type} - {acc.account_number}') 
                             for acc in accounts]
    
    if form.validate_on_submit():
        account = BankAccount.query.get(form.account_id.data)
        if not account:
            flash('Invalid account selected')
            return redirect(url_for('.new_transaction'))
            
        transaction = Transaction(
            amount=form.amount.data,
            description=form.description.data,
            transaction_type=form.transaction_type.data,
            account_id=form.account_id.data,
            user_id=current_user.id,
            reference_id=''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        )
        
        # Convert decimal amount to float and update account balance
        amount = float(form.amount.data)
        if form.transaction_type.data == 'withdrawal':
            account.balance -= amount
        else:
            account.balance += amount
            
        db.session.add(transaction)
        db.session.commit()
        flash('Transaction completed successfully!')
        return redirect(url_for('.dashboard'))
    
    return render_template('transaction.html', title='New Transaction', form=form)

@app.route('/api/transactions')
@login_required
def get_transactions():
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.timestamp.desc()).limit(10).all()
    
    return jsonify([{
        'id': t.id,
        'amount': float(t.amount),
        'description': t.description,
        'type': t.transaction_type,
        'timestamp': t.timestamp.isoformat()
    } for t in transactions])

@app.route('/transfer', methods=['GET','POST'])
@login_required
def transfer():
    form = TransferForm()
    if form.validate_on_submit():
        # Get the recipient user
        recipient = User.query.filter_by(username=form.recipient.data).first()
        if not recipient:
            flash('Recipient not found')
            return redirect(url_for('.transfer'))

        # Get the sender's account
        sender_account = BankAccount.query.filter_by(user_id=current_user.id).first()
        if not sender_account:
            flash('You don\'t have an account to transfer from')
            return redirect(url_for('.dashboard'))

        # Get the recipient's account
        recipient_account = recipient.accounts.first()
        if not recipient_account:
            flash('Recipient does not have an account')
            return redirect(url_for('.transfer'))

        # Check if sender has enough balance
        if sender_account.balance < form.amount.data:
            flash('Insufficient balance')
            return redirect(url_for('.transfer'))

        # Convert decimal amount to float for balance operations
        transfer_amount = float(form.amount.data)

        # Create transactions for both sender and recipient
        sender_transaction = Transaction(
            amount=-transfer_amount,
            description=f'Transfer to {recipient.username}',
            transaction_type='transfer',
            account_id=sender_account.id,
            user_id=current_user.id,
            reference_id=''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        )

        recipient_transaction = Transaction(
            amount=transfer_amount,
            description=f'Transfer from {current_user.username}',
            transaction_type='transfer',
            account_id=recipient_account.id,
            user_id=recipient.id,
            reference_id=''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        )

        # Update balances
        sender_account.balance -= transfer_amount
        recipient_account.balance += transfer_amount

        db.session.add(sender_transaction)
        db.session.add(recipient_transaction)
        db.session.commit()
        flash('Transfer completed successfully!')
        return redirect(url_for('.dashboard'))

    return render_template('transfer.html', title='Transfer', form=form)
