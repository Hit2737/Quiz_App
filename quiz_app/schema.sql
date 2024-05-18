-- Create the table for quizzes
CREATE TABLE IF NOT EXISTS Quizzes (
    quiz_id INTEGER PRIMARY KEY,
    quiz_name TEXT NOT NULL
);

-- Create the table for questions with nested options in JSON
CREATE TABLE IF NOT EXISTS Questions (
    question_id INTEGER PRIMARY KEY,
    quiz_id INTEGER,
    question_text TEXT NOT NULL,
    options JSON NOT NULL,
    FOREIGN KEY (quiz_id) REFERENCES Quizzes (quiz_id) ON DELETE CASCADE
);

-- Insert sample data
-- Insert into quizzes (although this will be used in the main code)
-- INSERT INTO Quizzes (quiz_name) VALUES ('Sample Quiz');

-- -- Insert into questions with options in JSON format
-- INSERT INTO Questions (quiz_id, question_text, options) VALUES 
-- (1, 'What is the capital of France?', '[{"option_text": "Paris", "is_correct": true}, {"option_text": "London", "is_correct": false}, {"option_text": "Berlin", "is_correct": false}, {"option_text": "Madrid", "is_correct": false}]');


-- Querying the data (although this will be used in the main code)
SELECT 
    q.quiz_name,
    ques.question_id,
    ques.question_text,
    json_each.value ->> '$.option_text' AS option_text,
    json_each.value ->> '$.is_correct' AS is_correct,
    json_each.value ->> '$.answer' AS answer,
    json_each.value ->> '$.case_sensitive' AS case_sensitive
FROM 
    Quizzes q
JOIN 
    Questions ques ON q.quiz_id = ques.quiz_id,
    json_each(ques.options)
WHERE 
    q.quiz_id = 2 AND json_each.value ->> '$.answer' IS NOT NULL;
