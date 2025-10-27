# Live Location Tracker

A full-stack, real-time GPS tracking web application built with Django, Django Channels, and Google Maps API. This application allows users to track their devices in real-time, view historical location data, and set up geofences for alerts.

**Live Demo:** [https://rishi-locations-tracker.onrender.com/](https://rishi-locations-tracker.onrender.com/)

![Location Tracker Demo](./static/images/demo.gif) 
*(Note: You can create a small GIF of your application working and add it here. Name it `demo.gif` and place it in the `static/images/` folder.)*

---

## ✨ Features

- **Real-time GPS Tracking**: View location updates live on Google Maps without refreshing the page, powered by WebSockets.
- **User Authentication**: Secure registration and login system for users.
- **Admin Dashboard**: A dedicated dashboard for admin users to monitor the live location of any registered user.
- **Location History**: A date picker allows users to view the complete route history for any specific day.
- **Geofencing**: Admins can create, view, and delete circular geofences on the map for any user.
- **Real-time Alerts**: Automatic alerts are sent to the admin's dashboard via WebSockets when a user enters or exits a defined geofence.
- **Device Monitoring**: Along with location, the application also tracks and displays the device's battery level.
- **Play Sound Remotely**: Admins can send a command to a user's device to play a sound, helping to locate a lost phone nearby.
- **Progressive Web App (PWA)**: The tracking interface can be "installed" on a mobile device's home screen for a native app-like experience.

---

## 🛠️ Tech Stack

- **Backend**: Python, Django, Django REST Framework (for APIs), Django Channels (for WebSockets).
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.
- **Maps & Geolocation**: Google Maps JavaScript API, Browser Geolocation API.
- **Database**: PostgreSQL (Production), SQLite3 (Development).
- **Deployment**: Render, Gunicorn (Process Manager), Daphne (ASGI Server), WhiteNoise (Static Files).
- **Libraries**: `geopy` for distance calculations, `django-pwa` for PWA functionality.
- **Version Control**: Git & GitHub.

---

## 🚀 Getting Started

Follow these instructions to set up and run the project on your local machine.

### Prerequisites

- Python 3.11+
- Git
- A Google Maps API Key with **Maps JavaScript API** and **Geocoding API** enabled.

### Local Setup Instructions

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Rishi0420/django-location-tracker.git
    cd django-location-tracker
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Create a `.env` file in the project root directory and add your secret keys. For this project, you can directly modify `settings.py` for local development.

    In `location_tracker_project/settings.py`, update the following:
    ```python
    # Set your Google Maps API Key
    GOOGLE_MAPS_API_KEY = 'YOUR_GOOGLE_MAPS_API_KEY'
    ```

5.  **Apply database migrations:**
    ```bash
    python manage.py migrate
    ```

6.  **Create a superuser (admin):**
    ```bash
    python manage.py createsuperuser
    ```

7.  **Run the development server:**
    The project uses Django Channels, so it's best to run it with Daphne.
    ```bash
    daphne -p 8000 location_tracker_project.asgi:application
    ```
    Or, you can use the standard Django command:
    ```bash
    python manage.py runserver
    ```

8.  **Access the application:**
    -   Open your browser and go to `http://127.0.0.1:8000/`.
    -   Register a new user or log in with your superuser credentials.

---

## 📝 How to Use

1.  **Register/Login**: Create an account or log in. Admins have access to the dashboard.
2.  **Start Tracking**: On a mobile device, log in and navigate to the `/track` page. Click "Activate Tracking" to start sending location data.
3.  **View Map**: On another device (like a desktop), log in and go to the `/map` page to see your own location in real-time.
4.  **Admin Monitoring**: As an admin, go to the `/dashboard` page. Click "View Map" for any user to see their live location and history. You can also "Add Geofence" or "Play Sound" from this view.

---

Thank you for checking out this project!
