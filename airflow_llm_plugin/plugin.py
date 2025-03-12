import sys
import types
from flask import Blueprint
from airflow.www.app import csrf

from airflow_llm_plugin.routes import register_routes
from flask_appbuilder import expose, BaseView as AppBuilderBaseView
from airflow_llm_plugin.models import ChatMessage

class LLMView(AppBuilderBaseView):
    """AppBuilder view for LLM plugin."""
    route_base = "/llm"
    
    @expose("/model-config")
    def model_config(self):
        """View for model configuration."""
        return self.render_template("model_config.html")
    
    @expose("/chat")
    def chat(self):
        """View for chat interface."""
        return self.render_template("chat.html")
    
    @expose("/dag-generator")
    def dag_generator(self):
        """View for DAG generator."""
        return self.render_template("dag_generator.html")

class LLMPlugin:
    """Main class for Airflow LLM plugin."""
    
    def __init__(self):
        self.blueprint = Blueprint(
            'airflow_llm_plugin',
            __name__,
            template_folder='templates',
            static_folder='static',
            static_url_path='/static/airflow_llm_plugin'
        )
        
        # Register routes with CSRF protection
        register_routes(self.blueprint, csrf)
        
        # AppBuilder integration
        self.appbuilder_views = [
            {
                "view": LLMView(),
                "category": "LLM Tools",
            }
        ]
        
        self.appbuilder_menu_items = [
            {
                "name": "LLM Model Configuration",
                "href": "/llm/model-config",
                "category": "LLM Tools"
            },
            {
                "name": "LLM Chat",
                "href": "/llm/chat",
                "category": "LLM Tools"
            },
            {
                "name": "DAG Generator",
                "href": "/llm/dag-generator",
                "category": "LLM Tools"
            }
        ]

        self.models = [ChatMessage]
