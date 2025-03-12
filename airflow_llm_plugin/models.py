import datetime
import json
import os
import sys
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy

# Check for mock airflow modules that could have been created in main.py
airflow_mock_available = 'airflow' in sys.modules and hasattr(sys.modules['airflow'], 'utils') and hasattr(sys.modules['airflow'].utils, 'db')

# For a standalone Flask app, we use these imports
try:
    # Try to import Airflow-specific modules
    if airflow_mock_available:
        # Use mock modules if available (development mode)
        from airflow.utils.db import create_session
        # Use SQLAlchemy's Base
        Base = declarative_base()
        # Flag indicating mock Airflow environment
        IN_AIRFLOW = True
    else:
        # Try actual Airflow imports (production mode)
        from airflow.models import DagBag
        from airflow.utils.db import create_session
        from airflow.models.base import Base
        # Flag to indicate we're in a real Airflow environment
        IN_AIRFLOW = True
except ImportError:
    # If Airflow imports fail, we're in a standalone environment
    Base = declarative_base()
    create_session = None
    IN_AIRFLOW = False

# Create a db object for compatibility with both Airflow and standalone Flask
db = SQLAlchemy(model_class=Base)

class LLMModelConfig(Base):
    """Model for storing LLM configuration."""
    __tablename__ = 'llm_model_config'
    
    id = Column(Integer, primary_key=True)
    provider = Column(String(50), nullable=False)  # 'openai', 'anthropic', 'gemini'
    model_name = Column(String(100), nullable=False)
    default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    @classmethod
    def get_default_config(cls):
        """Get the default model configuration."""
        with create_session() as session:
            config = session.query(cls).filter(cls.default == True).first()
            if not config:
                # If no default is set, create one with OpenAI
                config = cls(
                    provider='openai',
                    model_name='gpt-4o',
                    default=True
                )
                session.add(config)
                session.commit()
            return config
    
    @classmethod
    def set_default_config(cls, provider, model_name):
        """Set a new default model configuration."""
        with create_session() as session:
            # Clear any existing defaults
            session.query(cls).filter(cls.default == True).update({cls.default: False})
            
            # Find if the config already exists
            config = session.query(cls).filter(
                cls.provider == provider,
                cls.model_name == model_name
            ).first()
            
            if config:
                config.default = True
            else:
                config = cls(
                    provider=provider,
                    model_name=model_name,
                    default=True
                )
                session.add(config)
            
            session.commit()
            return config
    
class ChatMessage(Base):
    """Model for storing chat messages."""
    __tablename__ = 'llm_chat_messages'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    @classmethod
    def get_chat_history(cls, session_id, limit=50):
        """Get chat history for a session."""
        if IN_AIRFLOW:
            with create_session() as session:
                messages = session.query(cls).filter(
                    cls.session_id == session_id
                ).order_by(cls.created_at.asc()).limit(limit).all()
                return messages
        else:
            messages = db.session.query(cls).filter(
                cls.session_id == session_id
            ).order_by(cls.created_at.asc()).limit(limit).all()
            return messages

class DAGPrompt(Base):
    """Model for storing DAG generation prompts."""
    __tablename__ = 'llm_dag_prompts'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    prompt = Column(Text, nullable=False)
    dag_id = Column(String(100), nullable=True)  # The generated DAG ID
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    @classmethod
    def create_dag_from_prompt(cls, prompt_id):
        """Generate and save a DAG from a prompt."""
        from airflow_llm_plugin.api.dag_generator import generate_dag_from_prompt
        
        if IN_AIRFLOW:
            with create_session() as session:
                prompt = session.query(cls).filter(cls.id == prompt_id).first()
                if not prompt:
                    return None
                
                # Generate the DAG file content
                dag_id, dag_content = generate_dag_from_prompt(prompt.prompt, prompt.name)
                
                # Save the DAG file to the dags folder
                dags_folder = os.environ.get('AIRFLOW_HOME', '/opt/airflow') + '/dags'
                os.makedirs(dags_folder, exist_ok=True)
                
                dag_file_path = f"{dags_folder}/llm_generated_{dag_id}.py"
                with open(dag_file_path, 'w') as f:
                    f.write(dag_content)
                
                # Update the prompt with the DAG ID
                prompt.dag_id = dag_id
                session.commit()
                
                # Refresh the DAG bag to load the new DAG
                from airflow.models import DagBag
                DagBag().get_dag(dag_id)
                
                return dag_id
        else:
            # Standalone mode implementation
            prompt = db.session.query(cls).filter(cls.id == prompt_id).first()
            if not prompt:
                return None
            
            # Generate the DAG file content
            dag_id, dag_content = generate_dag_from_prompt(prompt.prompt, prompt.name)
            
            # Save the DAG file to a local dags folder for testing
            dags_folder = "dags"
            os.makedirs(dags_folder, exist_ok=True)
            
            dag_file_path = f"{dags_folder}/llm_generated_{dag_id}.py"
            with open(dag_file_path, 'w') as f:
                f.write(dag_content)
            
            # Update the prompt with the DAG ID
            prompt.dag_id = dag_id
            db.session.commit()
            
            return dag_id
