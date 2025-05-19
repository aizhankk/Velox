# Velox

**Velox** is a mobile task and schedule management app designed to help users organize their day, manage tasks, and stay on top of their routines with ease.

---

## Features

- User authentication with email/password and Google OAuth  
- User profile personalization (name input)  
- Set wake-up and sleep times to optimize daily routines  
- Task categorization (Work, Personal, Shopping, Health)  
- Create, edit, and delete tasks with reminders and location notes  
- Interactive calendar to view and manage scheduled events  
- Push notifications for upcoming tasks  
- Task statistics and progress tracking  
- Voice input for quick task creation  
- Google Calendar integration  

---

## Screenshots

![Welcome and Auth](./screenshots/welcome-auth.png)  
![Name Personalization & Time Setup](./screenshots/onboarding-time-setup.png)  
![Main Menu & Categories](./screenshots/main-menu-categories.png)  
![Notifications](./screenshots/notifications.png)  
![Calendar & Task Creation](./screenshots/calendar-task.png)  
![Voice Input](./screenshots/voice-input.png)

---

## Tech Stack

- Python 3.x  
- Django 5.2  
- Django REST Framework 3.16.0  
- Simple JWT  
- Djoser  
- social-auth-app-django (Google OAuth)  
- PostgreSQL (psycopg2 / psycopg)  
- Requests & Requests-OAuthlib  

---

## Installation

```bash
git clone <repo-url>
cd velox
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
pip install -r requirements.txt
