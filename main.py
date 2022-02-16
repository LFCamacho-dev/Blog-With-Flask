import os
from datetime import datetime as dt
from flask import Flask, render_template, request
import requests
import send_email as sm
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email


class LoginForm(FlaskForm):
    email = StringField(label='Email', validators=[
        # Length(min=6, message=u"Little short for an email address?"),
        Email(message="Not a valid email address"),
        DataRequired()
    ])
    password = PasswordField(label='Password', validators=[
        DataRequired(),
        Length(min=8, message="Password must be at least 8 characters long...")
    ])
    submit = SubmitField(label="Submit")


app = Flask(__name__)
today_date = dt.today()
all_posts = requests.get("https://api.npoint.io/b73c5f9f1858f6080703").json()

# print(os.urandom(12)) #  this generates a random key, 12 digits
app.secret_key = r"b'Vj<\xf7mP\x854\xad%,E'"


@app.route('/')
def home():
    return render_template("pages/index.html", year=today_date.year)


@app.route('/login', methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        if login_form.email.data == "admin@email.com" and login_form.password.data == "12345678":
            return render_template("pages/secret/success.html")
            # return "Success match!"
        else:
            return render_template("pages/secret/denied.html")
    return render_template('pages/secret/login_secret.html', form=login_form)


@app.route('/about/')
def about():
    return render_template("pages/about.html", year=today_date.year)


@app.route('/blog/')
def blog():
    return render_template("pages/blog.html", year=today_date.year, posts=all_posts)


@app.route('/contact/')
def contact():
    return render_template("pages/contact.html", year=today_date.year)


@app.route('/form-entry', methods=["POST"])
def receive_data():
    name = request.form['name']
    e_mail = request.form['email']
    phone = request.form['phone']
    message = request.form['message']

    if request.method == 'POST':
        new_email = sm.Email()
        new_email.send_email(name, e_mail, phone, message)
        return "<h1>Successfully sent your message!</h1>"


@app.route('/blog/post/<int:post_id>')
def post_page(post_id):
    post_info = [x for x in all_posts if x["id"] == post_id][0]
    return render_template("pages/post.html", year=today_date.year, post_info=post_info)


@app.route('/success-login', methods=["POST"])
def receive_login():
    if request.method == 'POST':
        return render_template("pages/success-login.html", year=today_date.year,
                               username=request.form['username'], password=request.form['password'])




if __name__ == "__main__":
    app.run(debug=True)
