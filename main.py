import os
from datetime import datetime as dt
from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
import requests
import BlogPost as Blog
import send_email as sm
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, URL
from flask_ckeditor import CKEditor, CKEditorField
from flask_sqlalchemy import SQLAlchemy


class LoginForm(FlaskForm):
    email = StringField(label='Email', validators=[
        Email(message="Not a valid email address"),
        DataRequired()
    ])
    password = PasswordField(label='Password', validators=[
        DataRequired(),
        Length(min=8, message="Password must be at least 8 characters long...")
    ])
    submit = SubmitField(label="Submit")


class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


app = Flask(__name__)
today_date = dt.today()
# print(os.urandom(12)) #  this generates a random key, 12 digits
app.secret_key = r"b'Vj<\xf7mP\x854\xad%,E'"
ckeditor = CKEditor(app)
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CKEDITOR_PKG_TYPE'] = 'standard-all'
db = SQLAlchemy(app)


# all_posts = requests.get("https://api.npoint.io/b73c5f9f1858f6080703").json()


@app.route('/')
def home():
    return render_template("pages/index.html", year=today_date.year)


@app.route('/login', methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        if login_form.email.data == "admin@email.com" and login_form.password.data == "12345678":
            return render_template("pages/secret/success.html")
        return render_template("pages/secret/denied.html")
    return render_template('pages/secret/login_secret.html', form=login_form)


@app.route('/about/')
def about():
    return render_template("pages/about.html", year=today_date.year)


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


@app.route('/new-post', methods=["GET", "POST"])
def new_post():
    form = CreatePostForm()
    page_title = "Create New Post"
    if request.method == 'POST':
        new_blog_post = Blog.BlogPost(
            title=request.form.get('title'),
            subtitle=request.form.get('subtitle'),
            date=f"{dt.strftime(today_date,'%B')} {today_date.day}, {today_date.year}",
            body=request.form.get('body'),
            author=request.form.get('author'),
            img_url=request.form.get('img_url'),
        )
        db.session.add(new_blog_post)
        db.session.commit()

        return redirect(url_for('blog'))

    return render_template('pages/make-post.html', page_title=page_title, form=form)


@app.route('/blog/')
def blog():
    posts = Blog.BlogPost.query.all()
    return render_template("pages/blog.html", year=today_date.year, posts=posts)


@app.route('/blog/post/<int:post_id>', methods=['GET'])
def post_page(post_id):
    requested_post = Blog.BlogPost.query.filter_by(id=post_id).first()
    return render_template("pages/post.html", year=today_date.year, post=requested_post)


@app.route("/blog/edit-post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    page_title = "Edit Post"
    post = db.session.query(Blog.BlogPost).get(post_id)
    edit_form = CreatePostForm()
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.author = edit_form.author.data
        post.img_url = edit_form.img_url.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("post_page", post_id=post.id))
    else:
        edit_form.title.data = post.title
        edit_form.subtitle.data = post.subtitle
        edit_form.img_url.data = post.img_url
        edit_form.author.data = post.author
        edit_form.body.data = post.body

    return render_template('pages/make-post.html', page_title=page_title, post=post_id, form=edit_form)


@app.route('/blog/delete/<int:post_id>')
def delete_post(post_id):
    db.session.delete(db.session.query(Blog.BlogPost).get(post_id))
    db.session.commit()
    return redirect(url_for('blog'))


@app.route('/success-login', methods=["POST"])
def receive_login():
    if request.method == 'POST':
        return render_template("pages/success-login.html", year=today_date.year,
                               username=request.form['username'], password=request.form['password'])


if __name__ == "__main__":
    app.run(debug=True)
