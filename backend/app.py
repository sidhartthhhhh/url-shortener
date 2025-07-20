# app.py - The main Flask application file

from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import string
import random
from datetime import datetime, timedelta

# --- App Setup ---
app = Flask(__name__)
# Gotta have this so our frontend on another domain can actually talk to this server.
CORS(app)

# --- Quick & Dirty "Database" for the Demo ---
# Obviously, you'd never do this in production. This is our stand-in for a real
# database like Postgres/Mongo and a cache like Redis. It's just a couple of dicts.
db = {
    "urls": {},      # Where we'll store the link data.
    "analytics": {}  # For tracking click counts.
}
cache = {} # This is our fake Redis. Speeds up lookups for popular links.

# --- Helper Functions ---

def generate_short_code(length=7):
    """
    Whips up a new short code. It keeps trying until it finds one that's not already in use.
    """
    chars = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choice(chars) for _ in range(length))
        # Make sure we don't have a collision. Super unlikely, but hey, better safe than sorry.
        if code not in db["urls"]:
            return code

# --- API Endpoints ---

@app.route("/api/shorten", methods=["POST"])
def shorten_url():
    """
    This is the endpoint for making a new short link.
    The frontend sends us a JSON object, and we do the magic.
    """
    # IMPORTANT: Replace this with your actual local IP address found in Step 1
    # This ensures the generated URL is accessible on your local network.
    SERVER_IP = "192.168.1.5" 

    data = request.get_json()
    long_url = data.get("long_url")

    if not long_url:
        return jsonify({"success": False, "message": "Come on, you have to give me a URL to shorten."}), 400

    # A little sanity check. Let's make sure it looks like a URL.
    if not (long_url.startswith("http://") or long_url.startswith("https://")):
        long_url = "http://" + long_url

    custom_alias = data.get("custom_alias")
    short_code = ""

    # Did the user provide a fancy custom name?
    if custom_alias:
        # If so, we need to check if it's already taken.
        if custom_alias in db["urls"]:
            return jsonify({"success": False, "message": "Bummer, that custom name is already taken."}), 409 # 409 Conflict
        short_code = custom_alias
    else:
        # Nope, so we'll just generate a random one.
        short_code = generate_short_code()

    # Handle the expiration date if the user set one.
    expires_at = None
    if data.get("expiry_days"):
        try:
            days = int(data.get("expiry_days"))
            expires_at = (datetime.utcnow() + timedelta(days=days)).isoformat() + "Z"
        except (ValueError, TypeError):
            # Whoops, they sent something that wasn't a number.
            return jsonify({"success": False, "message": "The expiry needs to be a number of days."}), 400

    # Alright, let's save this thing to our "database".
    db["urls"][short_code] = {
        "long_url": long_url,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "expires_at": expires_at,
    }
    db["analytics"][short_code] = 0 # Start the click count at zero.

    # Use the configured IP address to build the short URL
    short_url = f"http://{SERVER_IP}:5000/{short_code}"

    # Let's print to the console so we can see what's happening during development.
    print(f"--- DB WRITE --- \n{db}")

    # Send back a nice, happy response to the frontend.
    return jsonify({
        "success": True,
        "short_url": short_url,
        "long_url": long_url,
        "expires_at": expires_at
    }), 201 # 201 Created


@app.route("/<short_code>", methods=["GET"])
def redirect_to_long_url(short_code):
    """
    This is the big one. A user clicks a short link, hits this endpoint, and gets sent away.
    """
    # Step 1: Check the cache. It's way faster than the DB.
    if short_code in cache:
        print(f"--- CACHE HIT for {short_code} ---")
        record = cache[short_code]
    # Step 2: Not in the cache? Fine, let's check the main database.
    elif short_code in db["urls"]:
        print(f"--- CACHE MISS for {short_code} ---")
        record = db["urls"][short_code]
        # Let's be smart and put it in the cache for next time.
        cache[short_code] = record
        print(f"--- CACHE WRITE for {short_code} ---")
    # Step 3: It's nowhere to be found.
    else:
        return "Sorry, we couldn't find a link for that.", 404

    # Is this link past its expiration date?
    if record.get("expires_at") and datetime.fromisoformat(record["expires_at"][:-1]) < datetime.utcnow():
        # It's dead. Let's clean up its remains from our records.
        db["urls"].pop(short_code, None)
        cache.pop(short_code, None)
        db["analytics"].pop(short_code, None)
        return "Whoops, this link has expired.", 410 # 410 Gone

    # It's a valid click! Let's count it.
    if short_code in db["analytics"]:
        db["analytics"][short_code] += 1
    
    print(f"--- ANALYTICS UPDATE --- \n{db['analytics']}")

    # And... redirect!
    return redirect(record["long_url"], code=301)


# This is a little helper for our frontend since it can't handle a 301 redirect directly.
@app.route("/api/lookup/<short_code>", methods=["GET"])
def lookup_short_code(short_code):
    """
    Just looks up a code and returns the long URL without redirecting.
    Super useful for our single-page-app demo.
    """
    if short_code in db["urls"]:
        return jsonify({"success": True, "long_url": db["urls"][short_code]["long_url"]})
    else:
        return jsonify({"success": False, "message": "Short link not found."}), 404


# --- Let's get this thing running ---
if __name__ == "__main__":
    # IMPORTANT: host='0.0.0.0' makes the server accessible from other devices on your network.
    app.run(host='0.0.0.0', debug=True, port=5000)
