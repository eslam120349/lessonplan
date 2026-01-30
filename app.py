# app.py
import os
import logging
from flask import Flask
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Supabase client ONLY
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("❌ Missing Supabase credentials!")
    raise ValueError("SUPABASE_URL and SUPABASE_KEY required")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    app.config["SUPABASE_CLIENT"] = supabase
    logger.info("✅ Supabase initialized")
except Exception as e:
    logger.error(f"❌ Supabase error: {e}")
    raise

# Login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'routes.login'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.get_by_id(user_id)

# Import routes
from routes import routes
app.register_blueprint(routes)

logger.info("✅ Flask app ready")
