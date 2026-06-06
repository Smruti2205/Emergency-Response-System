# Emergency Response System

A Flask-based Emergency Response System that enables users to send emergency alerts, notify emergency contacts via email, visualize active alerts on a map, and monitor incidents through an administrative dashboard.

## Overview

This project provides a centralized platform for reporting and monitoring emergency situations. When an alert is generated, the system stores the information in a MySQL database and sends email notifications to designated contacts. Administrators can monitor alerts, view statistics, and analyze emergency data through dashboards and visualizations.

## Features

* Emergency alert generation
* Email notifications using Gmail SMTP
* Interactive map displaying active alerts
* Alert analytics and daily statistics
* Administrative dashboard
* Scheduled safety check-ins
* MySQL database integration
* Environment-variable based configuration

## Technology Stack

### Backend

* Python
* Flask
* Flask-Mail
* Flask-MySQLdb

### Database

* MySQL

### Data Visualization

* Matplotlib
* Folium

### Scheduling

* APScheduler

### Additional Libraries

* SpeechRecognition
* Geopy
* Python-Dotenv

## Project Structure

```text
Emergency-Response-System/
│
├── app.py
├── checkin_scheduler.py
├── config.py
├── requirements.txt
├── .gitignore
│
├── static/
│   └── styles.css
│
├── templates/
│   ├── index.html
│   ├── alerts.html
│   ├── admin_dashboard.html
│   ├── alerts_per_day.html
│   ├── map.html
│   └── set_checkin.html
│
└── README.md
```

## Installation

### Clone the Repository

```bash
git clone https://github.com/Smruti2205/Emergency-Response-System.git
cd Emergency-Response-System
```

### Create a Virtual Environment

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS**

```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Database Setup

Create a MySQL database:

```sql
CREATE DATABASE emergencydb;
```

Use the database:

```sql
USE emergencydb;
```

Create the required tables:

```sql
CREATE TABLE alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    latitude FLOAT,
    longitude FLOAT,
    status ENUM('Active','Resolved') DEFAULT 'Active',
    address VARCHAR(255)
);
```

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    location VARCHAR(255),
    medical_info TEXT
);
```

```sql
CREATE TABLE contact (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    relationship VARCHAR(100)
);
```

```sql
CREATE TABLE report (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    report_type VARCHAR(50) NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Environment Variables

Create a `.env` file in the project root:

```env
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=emergencydb

MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_gmail_app_password

ADMIN_EMAIL=admin@example.com

SECRET_KEY=your_secret_key
```

## Gmail Configuration

1. Enable Two-Factor Authentication on your Google account.
2. Generate a Gmail App Password.
3. Add the generated password to the `.env` file.

## Running the Application

```bash
python app.py
```

Open the application in your browser:

```text
http://127.0.0.1:5000
```

## Future Improvements

* Real-time GPS tracking
* SMS notifications
* User authentication and authorization
* Mobile application support
* Emergency response escalation workflow
* Real-time monitoring dashboard

## License

This project is licensed under the MIT License. See the LICENSE file for details.
