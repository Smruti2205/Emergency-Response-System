from flask import Flask, render_template, request, redirect, flash, url_for
from flask_mail import Mail, Message
from flask_mysqldb import MySQL
from markupsafe import Markup
from datetime import datetime
import folium
import json
import matplotlib
import os
from dotenv import load_dotenv

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.start()

import threading
import speech_recognition as sr
import requests
from flask_mysqldb import MySQL

load_dotenv()


# Initialize Flask app
app = Flask(__name__)

# Secret Key
app.secret_key = os.getenv('SECRET_KEY')

# MySQL Configuration
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['MYSQL_CHARSET'] = 'utf8mb4'

mysql = MySQL(app)

# Email Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']

mail = Mail(app)

# Admin Email
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')

# Home Page
@app.route('/')
def index():
    return render_template('index.html')

# Map Page showing Active Alerts
@app.route("/map")
def alert_map():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT latitude, longitude, address, message, timestamp FROM alerts WHERE status='Active'")
    rows = cursor.fetchall()

    m = folium.Map(location=[18.5, 73.8], zoom_start=12)
    for alert in rows:
        latitude, longitude, address, message, timestamp = alert
        popup_info = f"{address}<br>{message}<br>{timestamp}"
        folium.Marker(
            [latitude, longitude],
            popup=folium.Popup(popup_info, max_width=300),
            icon=folium.Icon(color='red', icon='exclamation-sign')
        ).add_to(m)

    cursor.close()
    map_html = m._repr_html_()
    return render_template("map.html", map_html=Markup(map_html))

@app.route("/alerts_per_day")
def alerts_per_day():
    cursor = mysql.connection.cursor()

    # Query alerts grouped by date
    cursor.execute("""
        SELECT DATE(timestamp) as date, COUNT(*) as alert_count
        FROM alerts
        WHERE timestamp IS NOT NULL
        GROUP BY DATE(timestamp)
        ORDER BY DATE(timestamp)
    """)
    alert_data = cursor.fetchall()
    cursor.close()

    print("Fetched alert data:", alert_data)  # Debug: See what's coming in

    if not alert_data:
        return "No data available for alerts per day."

    # Format dates and counts
    dates = [data[0] for data in alert_data]  # datetime.date objects
    alert_counts = [data[1] for data in alert_data]

    # Format dates to YYYY-MM-DD
    formatted_dates = [date.strftime('%Y-%m-%d') for date in dates]

    # Plot the bar chart
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.bar(formatted_dates, alert_counts, color='red', width=0.1)
    
    ax.set_title('Number of Alerts Per Day')
    ax.set_xlabel('Date')
    ax.set_ylabel('Number of Alerts')
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Save chart to BytesIO buffer
    img_stream = BytesIO()
    plt.savefig(img_stream, format='png')
    plt.close()  # Close to free memory
    img_stream.seek(0)

    # Encode chart as base64
    img_b64 = base64.b64encode(img_stream.getvalue()).decode('utf-8')

    return render_template("alerts_per_day.html", img_b64=img_b64)
@app.route('/set_checkin', methods=['POST', 'GET'])
def set_checkin():
    if request.method == 'POST':
        try:
            user_id = request.form['user_id']
            checkin_time = request.form['checkin_time']
            emergency_email = request.form['emergency_email']
        except KeyError as e:
            flash(f"Missing field: {e.args[0]}", "error")
            return render_template("set_checkin.html")
        
        # Optionally store check-in info in db.json
        with open("db.json", "w") as f:
            json.dump({"status": "not_safe", "emergency_email": emergency_email, "user_id": user_id}, f)

        # Schedule check-in without redirecting
        schedule_checkin(user_id, checkin_time, emergency_email)

        flash("Check-in scheduled successfully!", "info")
        return render_template("set_checkin.html", checkin_time=checkin_time, emergency_email=emergency_email)

    return render_template("set_checkin.html")

def schedule_checkin(user_id, checkin_time_str, emergency_email):
    checkin_time = datetime.strptime(checkin_time_str, '%Y-%m-%dT%H:%M')

    def job():
        with open("db.json") as f:
            data = json.load(f)
            if data.get("status") != "safe":
                trigger_alert(user_id, emergency_email)

    scheduler.add_job(job, 'date', run_date=checkin_time)

@app.route('/mark_safe', methods=['POST','GET'])
def mark_safe():
    with open("db.json") as f:
        data = json.load(f)
        user_id = data.get("user_id")
        emergency_email = data.get("emergency_email")
    
    # Send "I'm Safe" email
    send_safe_email(emergency_email)
    
    # Update status in db.json
    with open("db.json", "w") as f:
        json.dump({"status": "safe"}, f)
    
    flash("You are marked as safe!", "info")
    return render_template("set_checkin.html")

def send_safe_email(emergency_email):
    msg = Message("I'm Safe", sender=app.config['MAIL_USERNAME'], recipients=[emergency_email])
    msg.body = "The user has marked themselves as safe."
    mail.send(msg)

def trigger_alert(user_id, emergency_email):
    print(f"🚨 ALERT: User {user_id} missed check-in!")
    with app.app_context():  # ✅ Fixes "outside application context" error
        msg = Message("Emergency Alert: Missed Check-in",
                      sender=app.config['MAIL_USERNAME'],
                      recipients=[emergency_email])
        msg.body = f"The user with ID {user_id} missed their scheduled check-in. Immediate attention is required."
        mail.send(msg)


# Submit Alert and Send Emails
@app.route('/send_alert', methods=['POST'])
def send_alert():
    name = request.form.get('name')
    condition = request.form.get('condition')

    # Temporary default values
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')

    if not latitude:
        latitude = 18.5204

    if not longitude:
        longitude = 73.8567

    # Your form currently has only one contact field
    contact = request.form.get('contact')
    user_contacts = [contact] if contact else []

    # Temporary default user_id
    user_id = request.form.get('user_id', 1)

    address = f"Latitude: {latitude}, Longitude: {longitude}"
    timestamp = datetime.now()

    alert_message = f"""
🚨 EMERGENCY ALERT 🚨

Name: {name}
Medical Info: {condition}
Location: {address} (Lat: {latitude}, Lng: {longitude})
Time: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}

Please respond immediately.
"""

    recipients = user_contacts + [ADMIN_EMAIL]
    msg = Message('🚨 Emergency Alert', sender=app.config['MAIL_USERNAME'], recipients=recipients)
    msg.body = alert_message

    try:
        mail.send(msg)
    except Exception as e:
        print("Email sending error:", e)

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO alerts (user_id, latitude, longitude, address, message, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, float(latitude), float(longitude), address, alert_message, timestamp))
        mysql.connection.commit()
        cursor.close()
        print("Saving to DB...")
        print("Saved successfully!")
    except Exception as e:
        print("DB Error:", e)
    flash('Emergency alert sent and stored successfully!', 'success')
    return redirect('/')

# Admin: View All Alerts
@app.route('/admin/alerts')
def view_alerts():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM alerts")
    alerts = cursor.fetchall()
    cursor.close()
    return render_template('alerts.html', alerts=alerts)

@app.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
