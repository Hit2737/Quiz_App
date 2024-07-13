CREATE TABLE IF NOT EXISTS Admins(
    admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email_id UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Users(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  email_id UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Quizzes(
    quiz_id INTEGER PRIMARY KEY NOT NULL,
    quiz_name TEXT NOT NULL,
    admin_id INTEGER,
    start_time TIMESTAMP,
    appr_num INTEGER,
    FOREIGN KEY (admin_id) REFERENCES Admins (admin_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Questions(
    question_id INTEGER NOT NULL,
    quiz_id INTEGER NOT NULL,
    question_type TEXT NOT NULL,
    question_text TEXT NOT NULL,
    lock BOOLEAN DEFAULT TRUE,
    duration TEXT,
    unlock_time TIMESTAMP,
    PRIMARY KEY (question_id, quiz_id),
    FOREIGN KEY (quiz_id) REFERENCES Quizzes (quiz_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Options(
    option_id INTEGER NOT NULL,
    quiz_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    option_text TEXT NOT NULL,
    correct BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (question_id, quiz_id, option_id),
    FOREIGN KEY (quiz_id) REFERENCES Quizzes (quiz_id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES Questions (question_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS UserResponses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    quiz_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    selected_options JSON NOT NULL,
    time_stamp TIMESTAMP DEFAULT (DATETIME('now','localtime')),
    FOREIGN KEY (user_id) REFERENCES Users (id),
    FOREIGN KEY (quiz_id) REFERENCES Quizzes (quiz_id),
    FOREIGN KEY (question_id) REFERENCES Questions(question_id)
);

CREATE TABLE IF NOT EXISTS Approvals(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    quiz_id INTEGER NOT NULL,
    approval_status BOOLEAN,
    time_stamp TIMESTAMP DEFAULT (DATETIME('now','localtime')),
    FOREIGN KEY (user_id) REFERENCES Users (id),
    FOREIGN KEY (quiz_id) REFERENCES Quizzes (quiz_id)
);

CREATE TABLE IF NOT EXISTS Unfairness(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    quiz_id INTEGER NOT NULL,
    unfairness_status BOOLEAN DEFAULT FALSE,
    time_stamp TIMESTAMP DEFAULT (DATETIME('now','localtime')),
    FOREIGN KEY (user_id) REFERENCES Users (id),
    FOREIGN KEY (quiz_id) REFERENCES Quizzes (quiz_id)
);