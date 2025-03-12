from airflow_llm_plugin.models import db, ChatMessage
from airflow_llm_plugin.api.model_config import get_default_llm_client
from airflow_llm_plugin.llm.prompts import SYSTEM_PROMPT
from airflow_llm_plugin.mcp_tools.mcp_client import load_tools

def process_chat_message(message, session_id):
    """Process a chat message and get a response from the LLM.
    
    Args:
        message (str): The user's message
        session_id (str): The current chat session ID
        
    Returns:
        str: The LLM's response
    """
    # Save the user message
    user_message = ChatMessage(
        session_id=session_id,
        role="user",
        content=message
    )
    db.session.add(user_message)
    db.session.commit()
    
    # Get chat history
    history = get_message_history(session_id)
    
    # Get the LLM client
    llm_client = get_default_llm_client()
    
    try:
        print (history)
        # Send the message to the LLM
        tools = load_tools()
        print (tools)
        response_text = llm_client.get_chat_completion(history, tools=tools)
        
        # Save the assistant's response
        assistant_message = ChatMessage(
            session_id=session_id,
            role="assistant",
            content=response_text
        )
        db.session.add(assistant_message)
        db.session.commit()
        
        return response_text
    except Exception as e:
        # Log the error and save a failure message
        import logging
        logging.exception(f"Error getting LLM completion: {str(e)}")
        
        error_message = f"Sorry, I encountered an error: {str(e)}"
        assistant_message = ChatMessage(
            session_id=session_id,
            role="assistant",
            content=error_message
        )
        db.session.add(assistant_message)
        db.session.commit()
        
        return error_message

def get_message_history(session_id, limit=20):
    """Get the chat message history in a format suitable for LLM API.
    
    Args:
        session_id (str): The chat session ID
        limit (int): Maximum number of messages to retrieve
        
    Returns:
        list: List of message dictionaries with role and content
    """
    messages = db.session.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at.asc()).limit(limit).all()
    
    # Add a system message to provide context
    history = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]
    
    # Add the chat history
    for msg in messages:
        history.append({
            "role": msg.role,
            "content": msg.content
        })
    
    return history

def get_chat_history(session_id, limit=50):
    """Get the chat history for display in the UI.
    
    Args:
        session_id (str): The chat session ID
        limit (int): Maximum number of messages to retrieve
        
    Returns:
        list: List of message dictionaries
    """
    messages = ChatMessage.get_chat_history(session_id, limit)
    
    history = []
    for msg in messages:
        history.append({
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.created_at.isoformat()
        })
    
    return history
