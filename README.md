# Airflow LLM Plugin

An Apache Airflow plugin providing LLM integration with custom web interfaces for model configuration, chat functionality, and automated DAG generation from natural language prompts.

## Features

- **Model Configuration**: Configure and manage different LLM providers (OpenAI, Anthropic, Google) and their respective models
- **Chat Interface**: Interact with LLMs right from Airflow's interface
- **DAG Generator**: Create Airflow DAGs from natural language prompts

## Supported LLM Providers

- OpenAI (GPT-4o and other models)
- Anthropic (Claude 3.5 Sonnet and other models)
- Google (Gemini models)

## Installation

```bash
# Install from PyPI (once published)
pip install airflow-llm-plugin

# Or install from source
pip install -e .
```

## Configuration

This plugin requires API keys for the LLM providers you want to use. Set these in your Airflow environment:

```bash
# For OpenAI
export OPENAI_API_KEY=your_openai_key

# For Anthropic
export ANTHROPIC_API_KEY=your_anthropic_key

# For Google
export GOOGLE_API_KEY=your_google_key
```

## Usage

After installation, the plugin will automatically register with Airflow. You'll see new menu items in the Airflow UI:

1. **LLM Model Configuration**: Set and configure which LLM provider and model to use
2. **LLM Chat**: Interactive chat interface using the configured LLM
3. **DAG Generator**: Create DAGs from natural language prompts

## Development

### Setup Development Environment

Checkout [Contributing.md](./Contributing.md) file


### Database Models

The plugin creates its own tables in the Airflow database:
- `llm_model_config`: Stores LLM provider and model configurations
- `llm_chat_messages`: Stores chat history
- `llm_dag_prompts`: Stores DAG generation prompts

## License

Apache License 2.0