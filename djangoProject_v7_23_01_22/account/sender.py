import smtplib
from email.message import EmailMessage
import time
from matplotlib import pyplot as plt
def email_send(subject, body, to):
    msg = EmailMessage()
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = to
    user = 'noreplytrainapp@gmail.com'
    msg['from'] = "TrainingApp"
    password = 'PROJEKTprojekt##11'

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(user, password)
    server.send_message(msg)
    server.quit()

email_send('asd', 'asdasds', 'Tomekstilon@wp.pl')