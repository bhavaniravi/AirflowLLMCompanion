import sys
import types
from airflow.plugins_manager import AirflowPlugin
from airflow_llm_plugin.plugin import LLMPlugin

class AirflowLLMPlugin(AirflowPlugin):
    name = "airflow_llm_plugin"
    
    operators = []
    hooks = []
    executors = []
    macros = []
    admin_views = []
    flask_blueprints = [LLMPlugin().blueprint]
    menu_links = []
    appbuilder_views = LLMPlugin().appbuilder_views
    appbuilder_menu_items = LLMPlugin().appbuilder_menu_items
    global_operator_extra_links = []
    operator_extra_links = []
