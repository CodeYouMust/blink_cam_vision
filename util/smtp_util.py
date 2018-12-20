import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


SMTP_HOST = os.environ.get('SMTP_HOST', None) # eg: 'smtp.mailgun.org'
SMTP_PORT = os.environ.get('SMTP_PORT', None) # eg: 587
SMTP_AUTH_USER = os.environ.get('SMTP_AUTH_USER', None) # username for sending
SMTP_AUTH_PASSWORD = os.environ.get('SMTP_AUTH_PASSWORD', None)
# eg: '"Blink XT Cron Job"<cron@domain.com>'
SMTP_FROM_ADDR = os.environ.get('SMTP_FROM_ADDR', None)
# eg: '"Blink XT Viewer"<end-user@domain.com>'
SMTP_TO_ADDR = os.environ.get('SMTP_TO_ADDR', None)


def gen_msg(subj,
            body,
            bodytype='plain',
            from_addr=SMTP_FROM_ADDR,
            to_addrs=SMTP_TO_ADDR):
    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = to_addrs
    msg['Subject'] = subj
    msg.attach(MIMEText(body, bodytype))
    return msg

 
def send_email(msg, fromaddr=SMTP_FROM_ADDR, toaddr=SMTP_TO_ADDR):
    if not SMTP_PORT or not SMTP_PORT:
        raise Exception('SMTP environment variables not set')
    port = int(SMTP_PORT)
    server = smtplib.SMTP(SMTP_HOST, port)
    server.starttls()
    server.login(SMTP_AUTH_USER, SMTP_AUTH_PASSWORD)
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()

def send_job_msg(subject, msg):
    body_template = '''
    <html>
    <head>
    </head>
    <body>{}</body>
    </html>
    '''
    body = body_template.format(msg)
    msg = gen_msg(subject, body, bodytype='html')
    send_email(msg)
    return
