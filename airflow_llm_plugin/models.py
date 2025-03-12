import datetime
import json
import os
import sys
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy
from airflow.models import DagBag
from airflow.utils.db import create_session
from airflow.models.base import Base

airflow_mock_available = 'airflow' in sys.modules and hasattr(sys.modules['airflow'], 'utils') and hasattr(sys.modules['airflow'].utils, 'db')

db = SQLAlchemy(model_class=Base)

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
        with create_session() as session:
            messages = session.query(cls).filter(
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
