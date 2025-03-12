# from setuptools import setup, find_packages

# setup(
#     name="airflow-llm-plugin",
#     version="0.1.0",
#     description="Airflow plugin integrating LLM capabilities for model configuration, chat functionality, and DAG generation",
#     author="Airflow Community",
#     author_email="your-email@example.com",
#     packages=find_packages(),
#     include_package_data=True,
#     install_requires=[
#         "apache-airflow>=2.5.0",
#         "openai>=1.0.0",
#         "anthropic>=0.10.0",
#         "google-generativeai>=0.1.0",
#         "langchain>=0.1.0",
#     ],
#     entry_points={
#         "airflow.plugins": [
#             "airflow_llm_plugin = airflow_llm_plugin.plugin.LLMPlugin"
#         ]
#     },
#     classifiers=[
#         "Development Status :: 4 - Beta",
#         "Environment :: Web Environment",
#         "Framework :: Apache Airflow",
#         "Intended Audience :: Developers",
#         "License :: OSI Approved :: Apache Software License",
#         "Programming Language :: Python :: 3",
#         "Programming Language :: Python :: 3.8",
#         "Programming Language :: Python :: 3.9",
#         "Programming Language :: Python :: 3.10",
#         "Programming Language :: Python :: 3.11",
#     ],
# )