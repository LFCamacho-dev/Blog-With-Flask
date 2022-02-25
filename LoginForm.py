

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
