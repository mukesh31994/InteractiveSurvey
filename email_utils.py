import smtplib
from email.message import EmailMessage
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def send_email_util(email_list):
    EMAIL_ADDRESS = 'mukeshsharma31994@gmail.com'
    EMAIL_PASSWORD = 'wmvtzxjzmehsaptk'

    for email, message in email_list:

        msg = EmailMessage()
        msg['Subject'] = 'Dublin Business School Survey Form !!!'

        msg['From'] = EMAIL_ADDRESS
        msg['To'] = email

        msg.set_content(message)
        # msg.add_alternative("""\
        # <!DOCTYPE html>
        # <html>
        #     <body>
        #         <h1 style="color:SlateGray;"> message </h1>
        #     </body>
        # </html>
        # """, subtype='html')
        msg.add_alternative('<!DOCTYPE html> <html> <body>Your participation in the survey is voluntary. However, you can help us a lot by taking time to share your experiences of higher education.<br>If you experience any technical issues, please contact  Student Services – student.services@dbs.ie <br> Further information is available at www.studentsurvey.ie <br> If you wish to complete the survey, click on the below link: <br> <h3 style="color:SlateGray;"> ' + message + '</h3> <br> <br> Yours sincerely,</body> </html>', subtype='html')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)

        logger.info(f"Sent message to : {email}")
