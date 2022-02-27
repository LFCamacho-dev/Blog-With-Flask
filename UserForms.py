from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Email, DataRequired, Length, URL


class RegisterForm(FlaskForm):
    name = StringField(label='Name', validators=[DataRequired()])
    email = StringField(label='Email', validators=[
        DataRequired(),
        # Length(min=6, message=u"Little short for an email address?"),
        Email(message="Not a valid email address")
    ])
    password = PasswordField(label='Password', validators=[
        DataRequired(),
        Length(min=10, message="Password must be at least 8 characters long...")
    ])
    submit = SubmitField(label="Submit")


class LoginForm(FlaskForm):
    email = StringField(label='Email', validators=[
        DataRequired(),
        Email(message="Not a valid email address")
    ])
    password = PasswordField(label='Password', validators=[
        DataRequired(),
        Length(min=10, message="Password must be at least 10 characters long...")
    ])
    submit = SubmitField(label="Submit")


class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    # author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")
