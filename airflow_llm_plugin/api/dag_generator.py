import os
import re
from datetime import datetime
from airflow_llm_plugin.models import db, DAGPrompt
from airflow_llm_plugin.api.model_config import get_default_llm_client

def save_prompt(name, prompt, description=None):
    """Save a DAG generation prompt.
    
    Args:
        name (str): The name of the prompt
        prompt (str): The prompt text
        description (str, optional): A description of the prompt
        
    Returns:
        dict: Details of the saved prompt
    """
    dag_prompt = DAGPrompt(
        name=name,
        description=description,
        prompt=prompt,
        active=True
    )
    
    db.session.add(dag_prompt)
    db.session.commit()
    
    return {
        "id": dag_prompt.id,
        "name": dag_prompt.name,
        "description": dag_prompt.description,
        "prompt": dag_prompt.prompt,
        "active": dag_prompt.active,
        "created_at": dag_prompt.created_at.isoformat()
    }

def list_prompts():
    """List all saved DAG prompts.
    
    Returns:
        list: List of prompt dictionaries
    """
    prompts = db.session.query(DAGPrompt).order_by(DAGPrompt.created_at.desc()).all()
    
    result = []
    for prompt in prompts:
        result.append({
            "id": prompt.id,
            "name": prompt.name,
            "description": prompt.description,
            "prompt": prompt.prompt,
            "dag_id": prompt.dag_id,
            "active": prompt.active,
            "created_at": prompt.created_at.isoformat()
        })
    
    return result

def delete_prompt(prompt_id):
    """Delete a DAG prompt.
    
    Args:
        prompt_id (int): The ID of the prompt to delete
        
    Returns:
        bool: Success flag
    """
    prompt = db.session.query(DAGPrompt).filter(DAGPrompt.id == prompt_id).first()
    if not prompt:
        raise ValueError(f"Prompt with ID {prompt_id} not found")
    
    db.session.delete(prompt)
    db.session.commit()
    
    return True

def generate_dag_from_prompt_id(prompt_id):
    """Generate a DAG from a saved prompt.
    
    Args:
        prompt_id (int): The ID of the prompt to use
        
    Returns:
        str: The ID of the generated DAG
    """
    prompt = db.session.query(DAGPrompt).filter(DAGPrompt.id == prompt_id).first()
    if not prompt:
        raise ValueError(f"Prompt with ID {prompt_id} not found")
    
    dag_id, dag_content = generate_dag_from_prompt(prompt.prompt, prompt.name)
    
    # Save the DAG file
    dags_folder = os.environ.get('AIRFLOW_HOME', '/opt/airflow') + '/dags'
    os.makedirs(dags_folder, exist_ok=True)
    
    dag_file_path = f"{dags_folder}/llm_generated_{dag_id}.py"
    with open(dag_file_path, 'w') as f:
        f.write(dag_content)
    
    # Update the prompt with the DAG ID
    prompt.dag_id = dag_id
    db.session.commit()
    
    return dag_id

def generate_dag_from_prompt(prompt, name):
    """Generate a DAG from a user prompt.
    
    Args:
        prompt (str): The user's prompt for DAG generation
        name (str): The name of the prompt/DAG
        
    Returns:
        tuple: (dag_id, dag_content)
    """
    # Create a sanitized DAG ID from the name
    dag_id = re.sub(r'[^a-zA-Z0-9_]', '_', name.lower().strip())
    dag_id = f"llm_dag_{dag_id}_{int(datetime.now().timestamp())}"
    
    # Combine with instructions for the LLM
    system_prompt = """
    You are an Apache Airflow DAG generator. Your task is to create a Python file containing a complete, functional Airflow DAG based on the user's request.
    
    Follow these rules:
    1. Generate only valid Python code that will work with Apache Airflow 2.5+
    2. Include necessary imports at the top
    3. Use best practices for Airflow DAGs
    4. Include a detailed docstring that explains the DAG's purpose
    5. Set reasonable default arguments
    6. Create a DAG object with the provided DAG ID
    7. Include appropriate tasks based on the user's request
    8. Set up task dependencies using the >> operator
    9. Include error handling where appropriate
    10. Add comments to explain complex sections
    11. Don't include any placeholder or TODO comments
    12. Ensure the code is complete and ready to run
    """
    
    full_prompt = f"""Based on this request, generate a complete Airflow DAG Python file:

Request: {prompt}

The DAG ID should be: {dag_id}

Only respond with the Python code of the DAG, nothing else.
"""
    
    # Get the LLM client
    llm_client = get_default_llm_client()
    
    # Generate the DAG code
    dag_content = llm_client.get_completion(full_prompt, system_prompt)
    
    # Clean up the response to ensure it's just Python code
    dag_content = dag_content.strip()
    if dag_content.startswith("```python"):
        dag_content = dag_content[len("```python"):].strip()
    if dag_content.endswith("```"):
        dag_content = dag_content[:-3].strip()
    
    return dag_id, dag_content
