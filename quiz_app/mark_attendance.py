from werkzeug.security import generate_password_hash,check_password_hash
import sqlite3

def allow_student():
    quiz_id = int(input('Enter the quiz id: '))
    print('Enter the username of the users. Enter 1 to stop. And after every username press Enter.')
    users = []
    username = input()
    while(username!="1"):
        users.append(username)
        username = input()

    db = sqlite3.connect(
        'instance/quiz_app.sqlite',
        detect_types=sqlite3.PARSE_DECLTYPES
    )
    db.row_factory = sqlite3.Row
    not_allowed = []

    for username in users:
        try:
            user = db.execute(
                'SELECT * FROM Users WHERE username = ?', (username,)
            ).fetchone()

            usr = db.execute(
                'SELECT * FROM Approvals WHERE user_id = ? AND quiz_id = ?', (user["id"], quiz_id)
            ).fetchone()

            if usr is None:
                db.execute(
                    'INSERT INTO Approvals (user_id, quiz_id, approval_status) VALUES (?, ?, ?)', (user["id"], quiz_id, 1)
                )
            else:
                db.execute(
                    'UPDATE Approvals SET approval_status = 1 WHERE user_id = ? AND quiz_id = ?', (user["id"], quiz_id)
                )

            db.execute(
                'DELETE FROM Unfairness WHERE user_id = ? AND quiz_id = ?', (user["id"], quiz_id)
            )
            db.commit()
        except:
            not_allowed.append(username)
    print('Users marked attendance successfully.')
    if (len(not_allowed) > 0):
        print('Following users were not allowed to mark attendance:')
        for username in not_allowed:
            print(username)

if __name__ == '__main__':

    allow_student()