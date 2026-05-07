# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import json
import requests

scheduler = BackgroundScheduler()
scheduler.start()

def trigger_alert(user_id):
    print(f"🚨 ALERT: User {user_id} missed check-in!")
    requests.post("http://localhost:5000/send_alert", data={
        "name": "Scheduled User",
        "condition": "Missed Check-in",
        "latitude": "0.0",
        "longitude": "0.0",
        "contacts": "anushka.gavit@cumminscollege.in",  # or fetch from DB
        "user_id": user_id
    })

def schedule_checkin(user_id, checkin_time_str):
    checkin_time = datetime.strptime(checkin_time_str, '%Y-%m-%dT%H:%M')

    def job():
        with open("db.json") as f:
            data = json.load(f)
            if data.get("status") != "safe":
                trigger_alert(user_id)

    scheduler.add_job(job, 'date', run_date=checkin_time)
