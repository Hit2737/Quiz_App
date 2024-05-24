CREATE TABLE IF NOT EXISTS user(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  email_id UNIQUE NOT NULL,
  password TEXT NOT NULL
);

-- Create the table for quizzes
CREATE TABLE IF NOT EXISTS Quizzes(
    quiz_id TEXT PRIMARY KEY NOT NULL,
    quiz_name TEXT NOT NULL,
    admin_id INTEGER,
    FOREIGN KEY (admin_id) REFERENCES user (admin_id) ON DELETE CASCADE
);

-- Create the table for questions with nested options in JSON
CREATE TABLE IF NOT EXISTS Questions(
    question_id INTEGER NOT NULL,
    quiz_id TEXT NOT NULL,
    question_text TEXT NOT NULL,
    options JSON NOT NULL,
    correct_options JSON NOT NULL,
    PRIMARY KEY (question_id, quiz_id),
    FOREIGN KEY (quiz_id) REFERENCES Quizzes (quiz_id) ON DELETE CASCADE
);
-- DROP TABLE IF EXISTS UserResponses;

CREATE TABLE IF NOT EXISTS UserResponses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    quiz_id TEXT NOT NULL,
    question_id INTEGER NOT NULL,
    selected_options JSON NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User (id),
    FOREIGN KEY (quiz_id) REFERENCES Quizzes (quiz_id),
    FOREIGN KEY (question_id) REFERENCES Questions(question_id)
);