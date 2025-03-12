from flask import request, jsonify, render_template, session, url_for
from werkzeug.exceptions import BadRequest
import uuid

from airflow_llm_plugin.api.model_config import get_model_configs
from airflow_llm_plugin.api.chat import process_chat_message, get_chat_history
from airflow_llm_plugin.api.dag_generator import save_prompt, list_prompts, generate_dag_from_prompt_id, delete_prompt

def register_routes(blueprint, csrf):
    """Register routes for the plugin."""
    
    # Create a mock CSRF decorator if needed
    if csrf is None:
        class MockCSRF:
            @staticmethod
            def exempt(f):
                return f
        csrf = MockCSRF()
    
    # Model Config Routes
    @blueprint.route('/api/model-config', methods=['GET'])
    def get_model_config_route():
        """Get all model configs, including the default one."""
        try:
            configs = get_model_configs()
        except Exception as e:
            print(f"Error getting model configs: {e}")
            return jsonify({"success": False, "error": str(e)}), 400
        
        return configs.model_dump(mode="json")
    
    # Chat Routes
    @blueprint.route('/api/chat/session', methods=['GET'])
    def get_chat_session():
        """Get or create a chat session ID."""
        if 'chat_session_id' not in session:
            session['chat_session_id'] = str(uuid.uuid4())
        
        return jsonify({"session_id": session['chat_session_id']})
    
    @blueprint.route('/api/chat/history', methods=['GET'])
    def get_chat_history_route():
        """Get chat history for the current session."""
        session_id = request.args.get('session_id') or session.get('chat_session_id')
        if not session_id:
            return jsonify({"success": False, "error": "No chat session found"}), 400
        
        history = get_chat_history(session_id)
        return jsonify({"success": True, "history": history})
    
    @blueprint.route('/api/chat/message', methods=['POST'])
    @csrf.exempt
    def send_chat_message():
        """Process a chat message and get a response."""
        try:
            data = request.get_json()
            message = data.get('message')
            session_id = data.get('session_id') or session.get('chat_session_id')
            
            if not message:
                raise BadRequest("Message is required")
            
            if not session_id:
                session_id = str(uuid.uuid4())
                session['chat_session_id'] = session_id
            
            response = process_chat_message(message, session_id)
            return jsonify({
                "success": True,
                "response": response,
                "session_id": session_id
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 400
    
    # DAG Generator Routes
    @blueprint.route('/api/dag/prompts', methods=['GET'])
    def list_prompts_route():
        """List all saved DAG prompts."""
        prompts = list_prompts()
        return jsonify({"success": True, "prompts": prompts})
    
    @blueprint.route('/api/dag/prompts', methods=['POST'])
    @csrf.exempt
    def save_prompt_route():
        """Save a DAG generation prompt."""
        try:
            data = request.get_json()
            name = data.get('name')
            description = data.get('description')
            prompt = data.get('prompt')
            
            if not name or not prompt:
                raise BadRequest("Name and prompt are required fields")
            
            result = save_prompt(name, prompt, description)
            return jsonify({
                "success": True,
                "prompt_id": result["id"]
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 400
    
    @blueprint.route('/api/dag/prompts/<int:prompt_id>', methods=['DELETE'])
    @csrf.exempt
    def delete_prompt_route(prompt_id):
        """Delete a DAG generation prompt."""
        try:
            delete_prompt(prompt_id)
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 400
    
    @blueprint.route('/api/dag/generate/<int:prompt_id>', methods=['POST'])
    @csrf.exempt
    def generate_dag_route(prompt_id):
        """Generate a DAG from a saved prompt."""
        try:
            dag_id = generate_dag_from_prompt_id(prompt_id)
            if not dag_id:
                raise BadRequest("Failed to generate DAG")
            
            return jsonify({
                "success": True,
                "dag_id": dag_id
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 400
    
    # Page Routes (for direct access without AppBuilder)
    @blueprint.route('/model-config')
    def model_config_page():
        """Model configuration page."""
        return render_template('model_config.html')
    
    @blueprint.route('/chat')
    def chat_page():
        """Chat interface page."""
        return render_template('chat.html')
    
    @blueprint.route('/dag-generator')
    def dag_generator_page():
        """DAG generator page."""
        return render_template('dag_generator.html')
