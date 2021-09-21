import logging
import deta
from deta import app
import os
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from datetime import datetime
from time import time

EMAIL_FROM = 'auto@zealseeker.com'
EMAIL_HOST = 'smtp.ym.163.com'
EMAIL_PORT = 994
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
EMAIL_FROM_NAME = 'admetSAR'

emaildb = deta.Base("emails")

def create_success_email():
    with open('success_email.html') as fp:
        html = fp.read()
    mail = MIMEText(html, 'html', 'utf-8')
    mail['Subject'] = 'admetSAR available now'
    return mail

def create_alert_email():
    with open('alert_email.html') as fp:
        html = fp.read()
    mail = MIMEText(html, 'html', 'utf-8')
    mail['Subject'] = 'admetSAR unavailable now'
    return mail

@app.lib.run()
@app.lib.cron()
def app(event):
    start_time = time()
    mail_list = emaildb.fetch(query={'reason?ne':'subscribe', 'notified': False}, limit=10).items
    n = len(mail_list)
    if n > 0:
        smtp = smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT, timeout=30)
        smtp.login(EMAIL_FROM, EMAIL_PASSWORD)
        for mail_item in mail_list:
            reason = mail_item['reason']
            address = mail_item['email']
            if reason == 'success':
                mail = create_success_email()
            elif reason == 'alert':
                mail = create_alert_email()
            else:
                logging.error("Abnormal reason")
                continue
            mail['From'] = formataddr([EMAIL_FROM_NAME, EMAIL_FROM])
            mail['To'] = formataddr([address.split('@')[0], address])
            smtp.sendmail(EMAIL_FROM, mail['To'], mail.as_string())
            mail_item['notified'] = True
            mail_item['date'] = datetime.isoformat(datetime.utcnow())
            emaildb.put(mail_item)
        smtp.quit()
    used_time = time() - start_time
    return 'Success, send {} emails, used {:.1f}s'.format(n, used_time)
