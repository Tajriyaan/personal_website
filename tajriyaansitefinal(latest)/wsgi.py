import sys
import os

# Add the directory containing your app to Python's path
app_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, app_dir)

# Import your Flask app object
from app import app as app

if __name__ == "__main__":
    app.run()
