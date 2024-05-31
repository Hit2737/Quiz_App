CREATE TABLE IF NOT EXISTS user(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  email_id UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Quizzes(
    quiz_id TEXT PRIMARY KEY NOT NULL,
    quiz_name TEXT NOT NULL,
    admin_id INTEGER,
    start_time TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES user (admin_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Questions(
    question_id INTEGER NOT NULL,
    quiz_id TEXT NOT NULL,
    question_text TEXT NOT NULL,
    options JSON NOT NULL,
    correct_options JSON NOT NULL,
    lock BOOLEAN DEFAULT TRUE,
    duration TEXT,
    PRIMARY KEY (question_id, quiz_id),
    FOREIGN KEY (quiz_id) REFERENCES Quizzes (quiz_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS UserResponses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    quiz_id TEXT NOT NULL,
    question_id INTEGER NOT NULL,
    selected_options JSON NOT NULL,
    time_stamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User (id),
    FOREIGN KEY (quiz_id) REFERENCES Quizzes (quiz_id),
    FOREIGN KEY (question_id) REFERENCES Questions(question_id)
);