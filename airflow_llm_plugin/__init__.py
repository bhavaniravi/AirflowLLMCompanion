import sys
import types

# Create mock Airflow modules if needed
if 'airflow' not in sys.modules:
    # Create a mock "airflow" module hierarchy for development
    airflow = types.ModuleType('airflow')
    airflow.plugins_manager = types.ModuleType('airflow.plugins_manager')
    
    # Create a mock AirflowPlugin class
    class AirflowPlugin:
        pass
    
    airflow.plugins_manager.AirflowPlugin = AirflowPlugin
    
    # Register the mock modules
    sys.modules['airflow'] = airflow
    sys.modules['airflow.plugins_manager'] = airflow.plugins_manager
else:
    # If airflow is already mocked or loaded, import from there
    from airflow.plugins_manager import AirflowPlugin

# Import plugin implementation
from airflow_llm_plugin.plugin import LLMPlugin

# This is the entry point for the Airflow plugin
class AirflowLLMPlugin(AirflowLLMPlugin):
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
