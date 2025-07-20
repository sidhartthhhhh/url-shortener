Flask URL Shortener
A full-stack URL shortener application built with a Python Flask backend and a vanilla HTML/CSS/JavaScript frontend. This project provides core features like URL shortening, custom aliases, link expiration, and redirection.

Features
URL Shortening: Convert long URLs into a compact, unique alias.

Custom Aliases: Users can suggest their own custom short names.

Link Expiration: Set an optional expiration date for any short link.

Redirection: Seamlessly redirects users from the short link to the original URL.

Clean UI: A simple and responsive user interface for creating links.

Tech Stack
Backend: Python, Flask, Flask-CORS

Frontend: HTML, Tailwind CSS, JavaScript

Database: In-memory Python dictionary (for demonstration purposes)

Project Structure
URL-Shortener-Project/
├── backend/
│   ├── app.py              # Main Flask application
│   └── requirements.txt    # Python dependencies
│
├── frontend/
│   └── index.html          # The single-page frontend
│
├── .gitignore              # Files to be ignored by Git
└── README.md               # This file

Getting Started
Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

Prerequisites
Python 3.8+

pip and venv

Installation & Setup
Clone the repository:

git clone https://github.com/your-username/url-shortener-flask.git
cd url-shortener-flask

Set up and activate the backend virtual environment:

cd backend
python -m venv venv
# On macOS/Linux
source venv/bin/activate
# On Windows
venv\Scripts\activate

Install backend dependencies:

pip install -r requirements.txt

Configure the IP Address:
Before running, you need to configure the server's IP address so other devices can connect to it.

Find your computer's local IP address (e.g., 192.168.1.5).

Open backend/app.py and update the SERVER_IP variable.

Open frontend/index.html and update the API_BASE_URL variable to match.

Running the Application
Start the backend server:
From the backend/ directory, run:

python app.py

The server will start on http://<YOUR_IP_ADDRESS>:5000.

Launch the frontend:
Navigate to the frontend/ directory and open the index.html file in your web browser.

You can now use the application to shorten URLs.