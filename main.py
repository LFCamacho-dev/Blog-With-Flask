from datetime import datetime as dt
from flask import Flask, render_template
import requests

app = Flask(__name__)
today_date = dt.today()
all_posts = requests.get("https://api.npoint.io/b73c5f9f1858f6080703").json()


@app.route('/')
def home():
    return render_template("index.html", year=today_date.year)


@app.route('/blog/')
def blog():
    return render_template("blog.html", year=today_date.year, posts=all_posts)


@app.route('/blog/post/<int:post_id>')
def post_page(post_id):
    post_info = [x for x in all_posts if x["id"] == post_id][0]
    return render_template("post.html", year=today_date.year, post_info=post_info)


if __name__ == "__main__":
    app.run(debug=True)
