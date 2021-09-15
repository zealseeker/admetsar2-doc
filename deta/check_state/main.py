from deta import App
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from deta import Deta
from datetime import datetime
import smtplib
import threading
import logging
from email.mime.text import MIMEText
from email.utils import formataddr
import os

deta = Deta()
app = App(FastAPI())
db = deta.Base("admetsar2")
emaildb = deta.Base("emails")
origins = [
    "http://localhost:8000",
    "https://zealseeker.github.io"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Status List: Success, Server Down, Connection Issue, Diagnosing
SUCCESS = 1
SERVER_DOWN = 2
CONNECTION_ISSUE = 3
DIAGNOSING = 4
ERROR = -1

EMAIL_FROM = 'auto@zealseeker.com'
EMAIL_HOST = 'smtp.ym.163.com'
EMAIL_PORT = 994
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
EMAIL_FROM_NAME = 'admetSAR'

@app.get("/")
def http():
    return "Hello Deta, I am running with HTTP"

@app.get('/subscribe')
def subscribe(email=None):
    if email is not None:
        if emaildb.fetch({'email': email, 'reason': 'subscribe',}).items:
            return {'success': False, 'msg': 'You have already subscribed'}
        emaildb.insert({'email': email, 'reason': 'subscribe', 'notified': False})
        return {'success': True}
    else:
        return {}

@app.get("/get_status")
def get_status():
    status = db.get('status')
    last_success = db.get('last_success')
    if last_success:
        date = last_success['date']
    else:
        date = None
    infos = {
        SUCCESS: 'The server is working',
        CONNECTION_ISSUE:'The network has been blocked',
        SERVER_DOWN: 'The server is down, we are fixing the problem',
        DIAGNOSING: 'We are diagnosing the problem'
    }
    if status['status'] in infos:
        info =infos[status['status']]
    else:
        info = None
    r = {'status': status, 'last_success_date': date, 'info': info}
    return r

@app.lib.run()
@app.lib.cron()
def cron_job(event):
    host_ok = False
    server_ok = False
    try:
        r = requests.get("http://lmmd.ecust.edu.cn", timeout=3)
        if r.status_code == 200:
            host_ok = True
    except:
        pass    
    try:
        r = requests.get("http://lmmd.ecust.edu.cn/admetsar2", timeout=3)
        if r.status_code == 200:
            server_ok = True
    except:
        pass
    logging.info("Test logging")
    last_try = db.get('last_try')
    if host_ok and server_ok:
        status = SUCCESS
        if last_try and last_try['status'] != SUCCESS:
            send_success_email()
            notify_subscriptors()
        db.put({'status': SUCCESS}, 'status')
        db.put({'status': SUCCESS, 'times': 0}, 'last_try')
        db.put({'date': datetime.utcnow()}, 'last_success')
        return 'Success'
    elif host_ok and not server_ok:
        status = SERVER_DOWN
    elif not host_ok and not server_ok:
        status = CONNECTION_ISSUE
    else:
        status = ERROR
    if status == DIAGNOSING:
        return 'Success'
    if not last_try:
        last_try = {'status': status, 'times': 1}
    elif last_try['status'] == status:
        if last_try['times'] == 3:
            send_alert()
            logging.error('Sending Email')
        last_try['times'] += 1
        db.put(last_try, 'last_try')
    else:
        last_try['status'] = status
        last_try['times'] = 1
    db.put({'status': status}, 'status')
    last_try['date'] = datetime.isoformat(datetime.utcnow())
    db.put(last_try, 'last_try')

def send_alert():
    emaildb.insert({'email': 'yanyanghong@163.com', 'reason': 'alert', 'notified': False})
    emaildb.insert({'email': '490579089@qq.com', 'reason': 'alert', 'notified': False})

def send_success_email():
    emaildb.insert({'email': 'yanyanghong@163.com', 'reason': 'success', 'notified': False})
    emaildb.insert({'email': '490579089@qq.com', 'reason': 'success', 'notified': False})

def notify_subscriptors():
    for each in emaildb.fetch({'reason': 'subscribe'}):
        each['reason'] = 'success'
        emaildb.put(each)
