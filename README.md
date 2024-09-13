# Quiz App

This repo provides the code for the quiz app that I with my friends ([Hitesh Kumar](https://github.com/hit2737/), [Bhavik Patel](https://github.com/bp0609/), [Gaurav Budhwani](https://github.com/gaurav-budhwani)) under the guidance of [Prof. Balagopal Komarath](https://github.com/balu).

## Features

- The app contains all the basic features like login, signup, create quiz, show result, forget password etc.
- The app can be used as attendance taking device in the classroom as it has some security features like random number varification, and...(no, no, no that can not be disclosed here although you can find it in the code :wink:).
- The app is built using flask and sqlite3.
- The app can be safely hosted on any machine which has python installed (i.e. the app is lightweight).

## How to run as an admin

First of all, you need to have to register yourself as an admin. For that, you need to run the add_admin.py file. The command to run the file is as follows: (Before running the command, make sure that you are in the root directory of the project)

```bash
python add_admin.py
```
Now, you can add/delete an admin. After adding an admin, you can run the app using the following command:

```bash
flask --app quiz_app run --host=0.0.0.0
```
If you want to run the app on debug mode then you can use --debug flag as follows:

```bash
flask --app quiz_app --debug run --host=0.0.0.0
```

Now, you can see the web address where the app is running. You can open the web address in your browser and login as an admin.

> **_NOTE:_**  You will get two address, one of which will be localhost and the other will be the IP address of the machine where the app is running. If your users/students are giving the quiz from different machines then you should use the IP address to access the app.

### Creating a quiz

After login as admin you will see an interface like below.

![Admin Interface](images_for_readme/admin_interface.png)

You can create a quiz by clicking on the "Create Quiz" button. Now, you have to select an id and title for the quiz(quiz id should be unique but you can put same quiz name multiple times). Now, after creating the quiz you can add questions, options and can mark answers on the interface. 

Here, if you want to add a new question then you can click on the "Add Question" button. You can also delete a question by clicking on the "Delete Question" button. You can also add options to the question by clicking on the "Add Option" button. You can also delete an option by clicking on the "Remove" button. You can mark the answer by clicking on the check box which is located at the left side of "Remove" button, and in case of text type answers you can select question type as "text" and then you can write the answer in the text box provided (the answer will be case sensitive in case of text type answers).

After adding all questions and answers the interface will look like below:

![Admin Interface](images_for_readme/create_quiz.png)

![Admin Interface](images_for_readme/create_quiz_2.png)

Now, after adding all questions and answers you can click on the "Done" button to save the quiz.

>**_NOTE:_** Here, if you want you can put the time limit for every question but you can leave it as it is to put manual lock unlock option.

Now, you will be redirected to a page like below:-

# Insert the image here which shows the last page of create quiz manual start time wala page start time wala jo ki done button click karne k baad milta h 

