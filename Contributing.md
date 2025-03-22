# Contributing to AirflowLLMCompanion

## Install Airflow

https://airflow.apache.org/docs/apache-airflow/stable/start.html

For testing this project you only need to run `airflow webserver`

## Install this Library

From this project directory `airflow_llm_plugin`

```
pip install -e .
```

## Airflow MCP Library

For this project we need an MCP library which you can clone from here
https://github.com/yangkyeongmo/mcp-server-apache-airflow

In `mcp_client.py` file change the path to the cloned repo path.

We will change this in the future