import os
import send_email as sm
import UserForms
from datetime import datetime as dt
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_bootstrap import Bootstrap
import requests
from functools import wraps
from flask_ckeditor import CKEditor, CKEditorField
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_gravatar import Gravatar
from sqlalchemy.orm import relationship
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()


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
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))

    # This will act like a List of BlogPost objects attached to each User.
    # The "author" refers to the author property in the BlogPost class.
    posts = relationship("BlogPost", back_populates="author")


class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)

    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # Create reference to the User object, the "posts" refers to the post's property in the User class.
    author = relationship("User", back_populates="posts")

    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)



db.create_all()  # This line only required once, when creating DB.


# all_posts = requests.get("https://api.npoint.io/b73c5f9f1858f6080703").json()


# region BASE ROUTES

@app.route('/')
def home():
    return render_template("pages/index.html", year=today_date.year, logged_in=current_user.is_authenticated)


@app.route('/about/')
def about():
    return render_template("pages/about.html", year=today_date.year, logged_in=current_user.is_authenticated)


@app.route('/contact/')
def contact():
    return render_template("pages/contact.html", year=today_date.year, logged_in=current_user.is_authenticated)


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

# endregion BASE ROUTES


# region BLOG ROUTES


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function


@app.route('/new-post', methods=["GET", "POST"])
@login_required
@admin_only
def new_post():
    form = UserForms.CreatePostForm()
    page_title = "Create New Post"
    if request.method == 'POST':
        new_blog_post = BlogPost()
        new_blog_post.title = request.form.get('title')
        new_blog_post.subtitle = request.form.get('subtitle')
        new_blog_post.date = f"{dt.strftime(today_date,'%B')} {today_date.day}, {today_date.year}"
        new_blog_post.body = request.form.get('body')
        new_blog_post.author = current_user
        new_blog_post.img_url = request.form.get('img_url')

        db.session.add(new_blog_post)
        db.session.commit()

        return redirect(url_for('blog'))

    return render_template('pages/make-post.html', page_title=page_title, form=form, logged_in=current_user.is_authenticated)


@app.route('/blog/')
def blog():
    posts = BlogPost.query.all()
    return render_template("pages/blog.html", year=today_date.year, posts=posts, logged_in=current_user.is_authenticated)


@app.route('/blog/post/<int:post_id>', methods=['GET'])
def post_page(post_id):
    requested_post = BlogPost.query.filter_by(id=post_id).first()
    return render_template("pages/post.html", year=today_date.year, post=requested_post, logged_in=current_user.is_authenticated)


@app.route("/blog/edit-post/<int:post_id>", methods=["GET", "POST"])
@login_required
@admin_only
def edit_post(post_id):
    page_title = "Edit Post"
    post = db.session.query(BlogPost).get(post_id)
    edit_form = UserForms.CreatePostForm()
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        # post.author = edit_form.author.data
        post.img_url = edit_form.img_url.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("post_page", post_id=post.id))
    else:
        edit_form.title.data = post.title
        edit_form.subtitle.data = post.subtitle
        edit_form.img_url.data = post.img_url
        # edit_form.author.data = post.author
        edit_form.body.data = post.body

    return render_template('pages/make-post.html', page_title=page_title, post=post_id, form=edit_form, logged_in=current_user.is_authenticated)


@app.route('/blog/delete/<int:post_id>')
@login_required
@admin_only
def delete_post(post_id):
    db.session.delete(db.session.query(BlogPost).get(post_id))
    db.session.commit()
    return redirect(url_for('blog'))

# endregion BLOG ROUTES


# region ADMIN ROUTES

@app.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated: return redirect(url_for('home'))
    else:

        login_form = UserForms.LoginForm()
        error = None
        if request.method == "POST":
            email = request.form.get('email')
            password = request.form.get('password')
            user = User.query.filter_by(email=email).first()
            if not user:
                error = 'That email does not exist, please try again.'
            else:
                if not check_password_hash(user.password, password):
                    error = 'Password incorrect, please try again.'
                else:
                    login_user(user)
                    return redirect(url_for('home'))

        return render_template("pages/login.html", form=login_form, error=error, logged_in=current_user.is_authenticated)


@app.route('/success-login', methods=["POST"])
def receive_login():
    if request.method == 'POST':
        return render_template("pages/success-login.html", year=today_date.year,
                               username=request.form['username'], password=request.form['password'])


@app.route('/register', methods=["GET", "POST"])
def register():
    if current_user.is_authenticated: return redirect(url_for('home'))
    else:
        register_form = UserForms.RegisterForm()
        error = None
        if request.method == 'POST':
            new_user = User(
                email=request.form.get('email'),
                name=request.form.get('name'),
                password=generate_password_hash(
                    request.form.get('password'),
                    method='pbkdf2:sha256',
                    salt_length=8)
            )
            email_present = User.query.filter_by(email=new_user.email).first()
            if email_present:
                flash("You've already signed up with that email, log in instead!")
                # Redirect to /login route.
                return redirect(url_for('login'))
                # error = "You've already signed up with that email, please login instead."
                # return render_template("pages/login.html", error=error, logged_in=current_user.is_authenticated)
            else:
                db.session.add(new_user)
                db.session.commit()

                login_user(new_user)

                return redirect(url_for("home"))

        return render_template("pages/register.html", form=register_form, logged_in=current_user.is_authenticated)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

# endregion ADMIN ROUTES


if __name__ == "__main__":
    app.run(debug=True)
