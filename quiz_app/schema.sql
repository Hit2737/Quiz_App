CREATE TABLE IF NOT EXISTS user(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS admin(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

-- Create the table for quizzes
CREATE TABLE IF NOT EXISTS Quizzes(
    quiz_id TEXT,
    quiz_name TEXT NOT NULL,
    admin_id INTEGER,
    FOREIGN KEY (admin_id) REFERENCES Admin (admin_id) ON DELETE CASCADE
);

-- Create the table for questions with nested options in JSON
CREATE TABLE IF NOT EXISTS Questions(
    question_id INTEGER PRIMARY KEY,
    quiz_id TEXT,
    question_text TEXT NOT NULL,
    options JSON NOT NULL,
    FOREIGN KEY (quiz_id) REFERENCES Quizzes (quiz_id) ON DELETE CASCADE
);
