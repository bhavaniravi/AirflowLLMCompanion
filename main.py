# This file is for development and testing purposes only.
# In production, the plugin will be installed alongside Airflow and use Airflow's webserver.

import os
import logging
import warnings
import sys

# Suppress some common warnings when importing Airflow modules
warnings.filterwarnings("ignore", message="No airflow_local_settings")
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Create a mock "airflow" module and its submodules for development mode
# This will allow the plugin to run without a full Airflow installation
import types
mock_airflow = types.ModuleType('airflow')
mock_airflow.models = types.ModuleType('airflow.models')
mock_airflow.utils = types.ModuleType('airflow.utils')
mock_airflow.utils.db = types.ModuleType('airflow.utils.db')
mock_airflow.models.base = types.ModuleType('airflow.models.base')
mock_airflow.models.base.Base = None
mock_airflow.www = types.ModuleType('airflow.www')
mock_airflow.www.app = types.ModuleType('airflow.www.app')
mock_airflow.www.app.csrf = None

# Provide a mock implementation of create_session
class MockSession:
    def __init__(self):
        pass
    
    def __enter__(self):
        from airflow_llm_plugin.models import db
        return db.session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        from airflow_llm_plugin.models import db
        if exc_type is None:
            db.session.commit()
        else:
            db.session.rollback()
        return False

mock_airflow.utils.db.create_session = MockSession

# Add the mock modules to sys.modules
sys.modules['airflow'] = mock_airflow
sys.modules['airflow.models'] = mock_airflow.models
sys.modules['airflow.utils'] = mock_airflow.utils
sys.modules['airflow.utils.db'] = mock_airflow.utils.db
sys.modules['airflow.models.base'] = mock_airflow.models.base
sys.modules['airflow.www'] = mock_airflow.www
sys.modules['airflow.www.app'] = mock_airflow.www.app

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Configure logging
logging.basicConfig(level=logging.INFO)  # Changed to INFO to reduce noise
logger = logging.getLogger(__name__)

# Create a simple Flask app for testing the plugin
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure the database for development
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database
from airflow_llm_plugin.models import db
db.init_app(app)

# Create models for development environment only
with app.app_context():
    # Create only the LLM plugin tables
    from airflow_llm_plugin.models import LLMModelConfig, ChatMessage, DAGPrompt
    db.metadata.tables = {
        'llm_model_config': LLMModelConfig.__table__,
        'llm_chat_messages': ChatMessage.__table__,
        'llm_dag_prompts': DAGPrompt.__table__
    }
    db.create_all()

# Load the Airflow LLM Plugin
from airflow_llm_plugin.plugin import LLMPlugin
llm_plugin = LLMPlugin()

# Register the plugin's blueprint
app.register_blueprint(llm_plugin.blueprint, url_prefix='/airflow-llm')

# Development server
if __name__ == '__main__':
    logger.info("Starting development server on port 5000...")
    logger.info("Note: This is for development purposes only. In production, use Airflow's webserver.")
    app.run(host='0.0.0.0', port=5000, debug=True)