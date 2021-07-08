from main import database as db
from datetime import datetime
import smtplib
import ssl

while True:
    datess = db.dates()
    # print(datess)
    for i in range(len(datess)):
        value = datess[i][1]
        time = str(value).split(',')[0]
        date = str(value).split(',')[-1]
        hour = int(time.split(':')[0])
        min = int(time.split(':')[-1])
        year = int(date.split('-')[0])
        month = int(date.split('-')[1])
        day = int(date.split('-')[2])
        date = datetime(year, month, day, hour, min, 1)
        date_now = datetime.now()
        now = date_now.strftime('%Y-%m-%d %X')

        if str(date) == str(now):
            print("Send")

            smtp_server = "SERVER_DOMAIN"
            port = 587  # For starttls
            sender_email = "SENDER_MAIL"
            password = "PASSWORD_Sender"
            receiver_email = "MAIL_TO"
            message = f"""\


            Name: {str(datess[i][2])}

            {str(datess[i][3])}

            {str(datess[i][1])}"""

            context = ssl.create_default_context()
            with smtplib.SMTP(smtp_server, port) as server:
                server.ehlo()  # Can be omitted
                server.starttls(context=context)
                server.ehlo()  # Can be omitted
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message)
