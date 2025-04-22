#Email
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTPResponseException, SMTPException

import os
from dotenv import load_dotenv

def sendMail(html, asunto, para):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = asunto
    msg['From'] = os.getenv("SMTP_BY")
    msg['To'] = para

    msg.attach(MIMEText(html, 'html'))

    try:
        # Corrección: Debes crear un objeto servidor SMTP correcto
        server = smtplib.SMTP(os.getenv("SMTP_SERVER"), os.getenv("SMTP_PORT"))
        server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD"))
        server.sendmail(os.getenv("SMTP_USER"), para, msg.as_string())
        server.quit()
        return None  # Indica éxito
    except Exception as e:
        # En lugar de solo imprimir, lanza la excepción para que active el rollback
        raise Exception(f"Error sending email: {str(e)}")