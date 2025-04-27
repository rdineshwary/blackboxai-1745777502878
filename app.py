from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)

# Database Models
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=True)
    isbn = db.Column(db.String(20), unique=True, nullable=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

class BorrowRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    borrow_date = db.Column(db.DateTime, default=datetime.utcnow)
    return_date = db.Column(db.DateTime, nullable=True)

    book = db.relationship('Book', backref=db.backref('borrow_records', lazy=True))
    user = db.relationship('User', backref=db.backref('borrow_records', lazy=True))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
@login_required
def index():
    return render_template('index.html')

# Books management routes
@app.route('/books')
def books():
    books = Book.query.all()
    return render_template('books.html', books=books)

@app.route('/books/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        year = request.form.get('year')
        isbn = request.form.get('isbn')
        new_book = Book(title=title, author=author, year=year if year else None, isbn=isbn)
        db.session.add(new_book)
        db.session.commit()
        flash('Book added successfully!', 'success')
        return redirect(url_for('books'))
    return render_template('add_book.html')

@app.route('/books/edit/<int:id>', methods=['GET', 'POST'])
def edit_book(id):
    book = Book.query.get_or_404(id)
    if request.method == 'POST':
        book.title = request.form['title']
        book.author = request.form['author']
        year = request.form.get('year')
        book.year = year if year else None
        book.isbn = request.form.get('isbn')
        db.session.commit()
        flash('Book updated successfully!', 'success')
        return redirect(url_for('books'))
    return render_template('edit_book.html', book=book)

@app.route('/books/delete/<int:id>', methods=['POST'])
def delete_book(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted successfully!', 'success')
    return redirect(url_for('books'))

# Users management routes
@app.route('/users')
def users():
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/users/add', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        new_user = User(name=name, email=email)
        db.session.add(new_user)
        db.session.commit()
        flash('User added successfully!', 'success')
        return redirect(url_for('users'))
    return render_template('add_user.html')

@app.route('/users/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('users'))
    return render_template('edit_user.html', user=user)

@app.route('/users/delete/<int:id>', methods=['POST'])
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('users'))

# Borrow records routes
@app.route('/borrow_records')
def borrow_records():
    records = BorrowRecord.query.all()
    return render_template('borrow_records.html', records=records)

@app.route('/borrow_records/add', methods=['GET', 'POST'])
def add_borrow_record():
    books = Book.query.all()
    users = User.query.all()
    if request.method == 'POST':
        book_id = request.form['book_id']
        user_id = request.form['user_id']
        new_record = BorrowRecord(book_id=book_id, user_id=user_id)
        db.session.add(new_record)
        db.session.commit()
        flash('Borrow record added successfully!', 'success')
        return redirect(url_for('borrow_records'))
    return render_template('add_borrow_record.html', books=books, users=users)

@app.route('/borrow_records/return/<int:id>', methods=['POST'])
def return_book(id):
    record = BorrowRecord.query.get_or_404(id)
    record.return_date = datetime.utcnow()
    db.session.commit()
    flash('Book returned successfully!', 'success')
    return redirect(url_for('borrow_records'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
