from datetime import datetime as dt
from flask import Flask, render_template, request
import requests
from send_email import Email


app = Flask(__name__)
today_date = dt.today()
all_posts = requests.get("https://api.npoint.io/b73c5f9f1858f6080703").json()


@app.route('/')
def home():
    return render_template("index.html", year=today_date.year)


@app.route('/about/')
def about():
    return render_template("about.html", year=today_date.year)


@app.route('/blog/')
def blog():
    return render_template("blog.html", year=today_date.year, posts=all_posts)


@app.route('/contact/')
def contact():
    return render_template("contact.html", year=today_date.year)


@app.route('/form-entry', methods=["POST"])
def receive_data():
    name = request.form['name']
    e_mail = request.form['email']
    phone = request.form['phone']
    message = request.form['message']

    if request.method == 'POST':
        new_email = Email()
        new_email.send_email(name, e_mail, phone, message)
        # print(name, e_mail, phone, message)
        return "<h1>Successfully sent your message!</h1>"

        # return render_template("contact.html"), (f"Email Sent! \n\n"
        #                                          f"Name: {name},\n"
        #                                          f"Email: {email},\n"
        #                                          f"Phone: {phone},\n"
        #                                          f"Message: {message}")


@app.route('/blog/post/<int:post_id>')
def post_page(post_id):
    post_info = [x for x in all_posts if x["id"] == post_id][0]
    return render_template("post.html", year=today_date.year, post_info=post_info)


@app.route('/login', methods=["POST"])
def receive_login():
    if request.method == 'POST':
        return render_template("login.html", year=today_date.year,
                               username=request.form['username'], password=request.form['password'])


if __name__ == "__main__":
    app.run(debug=True)
