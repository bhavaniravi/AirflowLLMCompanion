import sys
import types
from airflow.plugins_manager import AirflowPlugin
from airflow_llm_plugin.plugin import LLMPlugin
from airflow.utils.db import provide_session

@provide_session
def create_custom_table(model, session=None):
    engine = session.get_bind()
    model.__table__.create(engine, checkfirst=True)

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
    models = LLMPlugin().models

    def on_load(self, *args, **kwargs):
        for model in self.models:
            create_custom_table(model)
