from werkzeug.security import generate_password_hash
import sqlite3

def reset_password():
    id = input('Enter the email id of the user whose password you want to reset: ')
    new_password = input('Enter the new password: ')

    db = sqlite3.connect(
        'instance/quiz_app.sqlite',
        detect_types=sqlite3.PARSE_DECLTYPES
    )
    db.row_factory = sqlite3.Row
    
    # Check if the user exists
    user = db.execute('SELECT * FROM Users WHERE email_id = ?', (id,)).fetchone()
    if user is None:
        raise ValueError('User does not exist.')
    else:
        # Update the password
        db.execute(
            'UPDATE Users SET password = ? WHERE email_id = ?',
            (generate_password_hash(new_password), id)
        )
        db.commit()
        print('Password reset successfully.')

if __name__ == '__main__':
    reset_password()
