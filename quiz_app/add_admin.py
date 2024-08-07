from werkzeug.security import generate_password_hash,check_password_hash
import sqlite3

def add_admin():
    username = input('Enter username of admin you want to add: ')
    email = input('Enter the email of the admin you want to add: ')
    if email.endswith('@iitgn.ac.in') == False:
        raise ValueError('Please enter a valid IITGN email id. Exiting...')
    password = input('Enter the password of the admin you want to add: ')

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
        print('Admin already exists.')
    else:
        db.execute(
            'INSERT INTO Admins (username, email_id, password) VALUES (?, ?, ?)',
            (username, email, generate_password_hash(password))
        )
        db.commit()
        print('Admin added successfully.')

def del_admin():
    email = input('Enter the email of the admin you want to delete: ')
    db = sqlite3.connect(
        'instance/quiz_app.sqlite',
        detect_types=sqlite3.PARSE_DECLTYPES
    )
    db.row_factory = sqlite3.Row
    admin = db.execute('SELECT * FROM Admins WHERE email_id = ?', (email,)).fetchone()
    if admin is None:
        raise ValueError('Admin does not exist.')
    else:
        db.execute('DELETE FROM Admins WHERE email_id = ?', (email,))
        db.commit()
        print('Admin deleted successfully.')

if __name__ == '__main__':
    oper = input('Enter 1 to add admin, 2 to delete admin: ')
    if oper == '1':
        add_admin()
    elif oper == '2':
        del_admin()
    else:
        print('Invalid input. Please try again.')