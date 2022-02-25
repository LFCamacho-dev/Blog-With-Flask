import main


# CONFIGURE TABLE
class BlogPost(main.db.Model):
    id = main.db.Column(main.db.Integer, primary_key=True)
    title = main.db.Column(main.db.String(250), unique=True, nullable=False)
    subtitle = main.db.Column(main.db.String(250), nullable=False)
    date = main.db.Column(main.db.String(250), nullable=False)
    body = main.db.Column(main.db.Text, nullable=False)
    author = main.db.Column(main.db.String(250), nullable=False)
    img_url = main.db.Column(main.db.String(250), nullable=False)

