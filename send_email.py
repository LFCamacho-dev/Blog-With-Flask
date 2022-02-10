import os
import smtplib


class Email:

    def __init__(self):
        # region MAIL AUTH
        self.EMAIL = os.environ.get("EMAIL")
        self.PASSWORD = os.environ.get("PASSWORD")
        self.SMTP_SERVER = "smtp.gmail.com"
        self.PORT = 587
        self.SSL_PORT = 465
        # endregion MAIL AUTH

    def send_email(self, name, email, phone, message):
        with smtplib.SMTP_SSL(self.SMTP_SERVER, self.SSL_PORT) as connection:
            connection.login(user=self.EMAIL, password=self.PASSWORD)
            connection.sendmail(
                from_addr=email,
                to_addrs=self.EMAIL,
                msg=f"Subject: Message From Creatos Contact Form!\n\n "
                    f"Name: {name}, Phone Number: {phone}\n"
                    f"Message: {message}"
            )

        print(f"Alert email sent!")
