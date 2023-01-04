import re
import json
import requests
import smtplib
import logging
from src.nlp.chatbot import ChatbotModel
from flask import (Flask, render_template,
                   redirect, request, url_for,
                   jsonify, make_response)
from email_utils import send_email_util

from src.db import StudentDatabase, UserDatabase, QuestionDatabase
# setting up the databases
user_db_obj = UserDatabase("./databases/database.db", "user")
question_db_obj = QuestionDatabase("./databases/database.db", "question_table")
student_db_obj = StudentDatabase(
    "./databases/database.db", "student_table")

email_validation_pattern = re.compile('[.a-zA-Z]+[0-9]*@gmail.com')
bot = ChatbotModel()
query_count = -1
questions = {}
responses = {}
form_completed = False
mode = "FEEDBACK"
app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route("/")
def home():
    return render_template('index.html')


@app.route("/home")
def index():
    return render_template('index.html')

@app.route("/dashboard")
def dashboard():
    name = request.args.get("name")
    type = request.args.get("type")
    students = student_db_obj.getAllFeedback(col=name)
    # form_types = list(set(question_db_obj.check_database(col="type")))
    return render_template('home.html', students=students,email=name)
    # return render_template('home.html')    


def get_valid_json_response(request):
    global responses
    response = {}
    logger.info(request)
    for k in request.keys():
        response[k.replace("_", " ")] = request[k]
    for k in responses:
        response[k.replace("_", " ")] = responses[k]
    responses = {}
    response.pop("submit")
    name = response.pop("name")
    type = response.pop("type")
    response = json.dumps(response)
    return name, type, response


@app.route("/feedback", methods=["POST", "GET"])
def feedback():
    global user_info, questions, query_count, form_completed

    if request.method == "POST":
        # request.json if request.json is not None else request.form
        query_request = request.form
        email, feed_type, response = get_valid_json_response(query_request)
        if user_db_obj.update_entry(username=email, feed_type=feed_type, response=response):
            student_db_obj.update_entry(
                status=2, name=None, email=email, type=feed_type)
            form_completed = False
            return redirect(url_for("user", content="form submission succesful", loc=""))
        else:
            return redirect(url_for("user", content="form submission failed, please try again...", loc=""))
    else:

        # TODO: always redirect to login page if not logged in user : DONE
        name = request.args.get("name")
        type = request.args.get("type")

        if name is None and type != '':
            return redirect(url_for("login", type=type))

        if student_db_obj.validate(name=name, type=type):
            result_from_qdb = question_db_obj.check_database(type=type)
            questions = {}
            query_count = -1
            for idx, ques in enumerate(result_from_qdb):
                questions[f"Q{idx}"] = (ques, ques.replace(" ", "_"))

            response = make_response(
                render_template('feedback.html', name=name, questions=questions, type=type))
            res = requests.post(
                'https://interactive-survey.herokuapp.com/predict?type='+type)
            print("Hit predict for first timer", res.content)
            return response
        else:
            return redirect(url_for("user", content="Feedback Already Submitted!!!", loc=""))


def is_invalid_email(email):
    return not len(re.findall(pattern=email_validation_pattern, string=email))


@app.route("/login", methods=["POST", "GET"])
def login():
    global user_info
    if request.method == "POST":
        email = request.form["text"]
        password = request.form["pass"]
        feed_type = None
        status = 2
        feed_type = None
        if "type" in request.form.keys():
            feed_type = request.form["type"]
        if feed_type == 'None' or feed_type is None or feed_type == "":
            results = student_db_obj.fetch(email, to_fetch="type")
            for (t, s) in results:
                if s == '1':
                    feed_type = t
                    status = int(s)
                    break

        if (feed_type is None or feed_type == "None") and status == 2:
            # return render_template("login.html", content="Form already filled...", type='')
            loc = "dashboard?name=" + email + "&type=" + feed_type
            return redirect(url_for("user", content="Taking you to form...", loc=loc))

        if feed_type is None or feed_type == "None":
            return render_template("login.html", content="Form not assigned yet...", type='')
        valid, _ = user_db_obj.validate(username=email, password=password)

        user_db_obj.update_entry(
            username=email, feed_type=feed_type, response='')
        userObj = user_db_obj.getUser(email)
        if userObj == "admin":
            return redirect(url_for("user", content="Taking you to form...", loc="admin"))    
        if valid:
            if status == 1:
                loc = "dashboard?name=" + email + "&type=" + feed_type
                return redirect(url_for("user", content="Taking you to form...", loc=loc))
            else:
                loc = "dashboard?name=" + email + "&type=" + feed_type
                return redirect(url_for("user", content="Taking you to form...", loc=loc))
                # return render_template("login.html", content="Form already filled", type='')
        else:
            return render_template("login.html", content="Invalid Username or Password", type='')
    else:
        feed_type = request.args.get("type")
        print(feed_type, "in login")
        return render_template('login.html', content="", type=feed_type)


@app.route("/signup", methods=["POST", "GET"])
def signup():
    """Registering user after format validation

    Returns
    -------
    html object
    """
    if request.method == "POST":
        password = request.form["pass"]
        conf_password = request.form["confpass"]
        email = request.form['email']
        name = request.form['text']
        correct = False
        if is_invalid_email(email):
            return render_template('signup.html', content="Invalid E-mail")
        else:
            correct = True
        if password == conf_password and correct:
            response = user_db_obj.insert_entry(
                username=email, password=password)
            if response:
                student_db_obj.insert_entry(name, email, '', '0')
                return redirect(url_for("user", content="Registration successful, please login again", loc="login"))
            else:
                return redirect(url_for("user", content="Entry already exists, please try again", loc="signup"))
        else:
            return render_template('signup.html', content="password and confirm password didn't matched", loc="login")
    else:
        return render_template('signup.html', content='')


@app.route("/predict", methods=["POST"])
def predict():
    """ Recieves query from user and sends corresponding response from pre-trained bot

    Returns
    -------
    json object
        response from pre-trained bot in json format
    """
    global query_count, questions, mode, responses, form_completed
    type = request.args.get("type")
    question_list = list(questions.values())
    print(query_count)
    if query_count == -9999:
        form_completed = True
        query_count = -2

    if query_count == -2:
        query_count += 1
        return jsonify({'answer': ["Feedback already completed."]})
    if query_count == -1:
        query_count = 0
        return jsonify({'answer': "Hi there, Type or Say YES if you want to give feedback else NO " + type})

    query_text = request.get_json().get("message")
    if query_text.lower() == "feedback":
        query_text = "yes"
        query_count = 0

    # print(query_text, query_count)
    if form_completed and query_count == 0:
        mode = "CONVERSATION"
        query_count = 1
        return jsonify({'answer': ["Form is already completed, if you want we can have generic conversation, else you can submit the form."]})

    if query_text.lower() == "yes" and query_count == 0:
        query_count = 1
        mode = "FEEDBACK"
        return jsonify({'answer': ["Sure, lets start with feedback."]})
    elif query_text.lower() != "yes" and query_count == 0:
        mode = "CONVERSATION"
        query_count = 1
        return jsonify({'answer': ["Sure, lets have generic conversation."]})

    if mode == "FEEDBACK":
        ques_num = query_count - 1
        if ques_num >= 1:
            responses[f"Q{ques_num}: " +
                      question_list[ques_num-1][0]] = query_text

        if ques_num >= len(question_list):
            query_count = -9999
            print(responses)
            return jsonify({'answer': ["Thank you for your feedback. Please press SUBMIT to complete the feedback."]})

        ques = question_list[query_count-1][0]
        query_count += 1
        return jsonify({'answer': [f"Ques {ques_num+1}/{len(question_list)}: {ques}"]})
    else:
        # TODO: text validation
        response_from_bot = bot.get_response(query_text)
        response = {"answer": response_from_bot}
        query_count += 1
        return jsonify(response)


@app.route("/user")
def user():
    # TODO: better redirection : DONE
    content = request.args.get("content")
    loc = request.args.get("loc")
    return render_template('redirecter.html', content=content, loc=loc)


def email_preprocess(form_types, student_mails,
                     base_url=f"https://interactive-survey.herokuapp.com/feedback?"):

    email_list = []
    for each_student in student_mails:
        # pulling email from combo string
        each_student = each_student.split("_")[1]
        message = ""
        for each_type in form_types:
            url = base_url + f"name={each_student}&type={each_type}"
            message += f"{each_type}: {url}\n"
        email_list.append((each_student, message))

    return email_list


@app.route("/admin", methods=["POST", "GET"])
def admin():
    if request.method == "POST":
        student_mails = request.form.getlist("dropdown_for_students")
        formtypes = request.form.getlist("formtype_dropdown")
        logger.info(student_mails)
        logger.info(formtypes)
        """
        TODO: BLOCKER : gmail service has stopped this feature
        1. send feedback mail for each form type to each student: SMTP :ONHOLD
        """
        # email_list = send_link_over_mail(formtypes, student_mails)
        email_list = email_preprocess(formtypes, student_mails)
        logger.info(email_list)
        send_email_util(email_list)
        logger.info("Email sent")

        for each_student in student_mails:
            name, email = each_student.split("_")
            for each_type in formtypes:
                print(student_db_obj.query(email, type=''))
                if student_db_obj.query(email, type=''):
                    student_db_obj.update_entry(
                        name, email, each_type, '1')
                else:
                    student_db_obj.insert_entry(
                        name, email, each_type, '1')

        return redirect(url_for("user", content="request succesfull", loc=""))
    else:
        students = student_db_obj.check_database()
        form_types = list(set(question_db_obj.check_database(col="type")))
        return render_template('admin.html', students=students, form_types=form_types)


if __name__ == '__main__':
    app.run(debug=True)
