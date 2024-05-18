-- Create the table for quizzes
CREATE TABLE Quizzes (
    quiz_id INTEGER PRIMARY KEY,
    quiz_name TEXT NOT NULL
);

-- Create the table for questions with nested options in JSON
CREATE TABLE Questions (
    question_id INTEGER PRIMARY KEY,
    quiz_id INTEGER,
    question_text TEXT NOT NULL,
    options JSON NOT NULL,
    FOREIGN KEY (quiz_id) REFERENCES Quizzes (quiz_id) ON DELETE CASCADE
);

-- Insert sample data
-- Insert into quizzes
INSERT INTO Quizzes (quiz_name) VALUES ('Sample Quiz');

-- Insert into questions with options in JSON format
INSERT INTO Questions (quiz_id, question_text, options) VALUES 
(1, 'What is the capital of France?', '[{"option_text": "Paris", "is_correct": true}, {"option_text": "London", "is_correct": false}, {"option_text": "Berlin", "is_correct": false}, {"option_text": "Madrid", "is_correct": false}]');
