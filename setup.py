from setuptools import setup, find_packages
import subprocess


install_deps = [
    "anthropic>=0.49.0",
    "autogen-agentchat>=0.4.9.2",
    "autogen-ext[grpc,mcp,ollama,openai]>=0.4.9.2",
    "bs4>=0.0.2",
    "gradio>=5.22.0",
    "httpx>=0.28.1",
    "ipywidgets>=8.1.5",
    "langchain-anthropic>=0.3.10",
    "langchain-community>=0.3.20",
    "langchain-experimental>=0.3.4",
    "langchain-openai>=0.3.9",
    "langgraph>=0.3.18",
    "langgraph-checkpoint-sqlite>=2.0.6",
    "langsmith>=0.3.18",
    "lxml>=5.3.1",
    "mcp-server-fetch>=2025.1.17",
    "mcp[cli]>=1.5.0",
    "openai>=1.68.2",
    "openai-agents>=0.0.15",
    "playwright>=1.51.0",
    "plotly>=6.0.1",
    "polygon-api-client>=1.14.5",
    "psutil>=7.0.0",
    "pypdf>=5.4.0",
    "pypdf2>=3.0.1",
    "python-dotenv>=1.0.1",
    "requests>=2.32.3",
    "semantic-kernel>=1.25.0",
    "sendgrid>=6.11.0",
    "setuptools>=78.1.0",
    "smithery>=0.1.0",
    "speedtest-cli>=2.1.3",
    "wikipedia>=1.4.0",
    ]

with open("README.md", "r") as fh:
    long_description = fh.read()

__version__ = None
exec(open("cheapNPC/_version.py").read())

setup(
    name='cheapNPC',
    version='0.1',
    packages=find_packages(),
    install_requires=install_deps,
    author='Leonardo de Melo João',
    author_email='leomelo168@gmail.com',
    description='This is a python implementation of the the Cheap NPC project.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/LMeloJ/cheapNPC',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: GPU :: NVIDIA CUDA",
        "Intended Audience :: Education :: Developers",
        "Natural Language :: English",
        "Topic :: Scientific/Engineering :: \
            Artificial Intelligence :: Agentic AI",
        "Topic :: Software Development :: Libraries",
    ],
    python_requires='>=3.12',
)