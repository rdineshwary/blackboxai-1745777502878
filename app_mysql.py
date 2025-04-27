from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Book, User, BorrowRecord
from datetime import datetime

app = Flask(__name__)
# Replace with your actual MySQL credentials and database name
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/library_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

db.init_app(app)

# Routes
@app.route('/')
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
