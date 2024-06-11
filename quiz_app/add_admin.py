from werkzeug.security import generate_password_hash
import sqlite3

def add_admin(username, email, password):
    db = sqlite3.connect(
        'instance/quiz_app.sqlite',
        detect_types=sqlite3.PARSE_DECLTYPES
    )
    db.row_factory = sqlite3.Row
    error = None
    user = db.execute(
        'SELECT * FROM Admins WHERE email_id = ?', (email,)
    ).fetchone()
    if user is not None:
        error = 'Admin already exists.'
    else:
        db.execute(
            'INSERT INTO Admins (username, email_id, password) VALUES (?, ?, ?)',
            (username, email, generate_password_hash(password))
        )
        db.commit()
    return error

if __name__ == '__main__':
    username = input('Enter username: ')
    email = input('Enter email: ')
    password = input('Enter password: ')
    error = add_admin(username,email, password)
    if error is not None:
        print(error)
    else:
        print('Admin added successfully.')