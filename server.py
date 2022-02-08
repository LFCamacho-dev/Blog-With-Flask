from datetime import datetime as dt
from flask import Flask, render_template
import requests


app = Flask(__name__)
today_date = dt.today()


@app.route('/')
def home():
    return render_template("index.html", year=today_date.year)


@app.route('/guess/<n>')
def guess_the_name(n):
    age_response = requests.get(f"https://api.agify.io?name={n}").json()
    guess_name = age_response["name"].title()
    guess_age = age_response["age"]
    gender_response = requests.get(f"https://api.genderize.io?name={n}").json()
    guess_gender = gender_response["gender"]
    return render_template("guess_name.html", name_=guess_name, age_=guess_age, gender_=guess_gender)


if __name__ == "__main__":
    app.run(debug=True)


