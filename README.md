Velox - Personal Task and Schedule Manager
Velox is a mobile app designed to help users manage personal tasks, schedules, and notifications. It assists users in planning their day, organizing tasks, integrating calendars, and tracking useful statistics.

Key Features
User registration and login with Google OAuth support

Profile personalization (user name)

Set your usual wake-up and bedtime

Main menu with task categories (Work, Personal, Shopping, Health)

Task management with reminders, categories, date, and time selection

Calendar view showing all scheduled events and tasks

Notifications for upcoming tasks

Statistics for completed tasks

Voice input for tasks and commands

Integration with Google Calendar

Interface Screenshots
Welcome and authentication screens

Sign up and login forms

Name personalization and time setup

Main menu with sections

Task categories screen

Notifications panel

Calendar and task creation views

Voice input and task management

Technologies & Dependencies
Python 3.x

Django 5.2

Django REST Framework 3.16.0

Simple JWT for authentication

Djoser for registration and login management

social-auth-app-django for Google OAuth integration

psycopg2 and psycopg for PostgreSQL database connectivity

requests and requests-oauthlib for external API interactions

Full dependency list is provided in requirements.txt:

ini
Копировать
asgiref==3.8.1
certifi==2025.1.31
cffi==1.17.1
charset-normalizer==3.4.1
cryptography==44.0.2
defusedxml==0.7.1
Django==5.2
djangorestframework==3.16.0
djangorestframework_simplejwt==5.5.0
djoser==2.3.1
idna==3.10
oauthlib==3.2.2
psycopg==3.2.6
psycopg2==2.9.10
pycparser==2.22
PyJWT==2.9.0
python3-openid==3.2.0
requests==2.32.3
requests-oauthlib==2.0.0
social-auth-app-django==5.4.3
social-auth-core==4.5.6
sqlparse==0.5.3
typing_extensions==4.13.2
tzdata==2025.2
urllib3==2.4.0
Installation
Clone the repository:

bash
Копировать
git clone <your-repository-url>
cd velox
Create and activate a virtual environment:

bash
Копировать
python -m venv venv
source venv/bin/activate  # On Linux/macOS
venv\Scripts\activate     # On Windows
Install the dependencies:

bash
Копировать
pip install -r requirements.txt
Configure your database settings and OAuth credentials in .env or settings.py.

Apply migrations and run the server:

bash
Копировать
python manage.py migrate
python manage.py runserver
