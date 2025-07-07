AgentX Documentation
====================

AgentX is a modern, AI-powered multi-agent framework for building intelligent systems.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   getting_started
   api/index

Getting Started
===============

AgentX is a framework for building multi-agent AI systems. It provides:

* **Multi-Agent Orchestration**: Coordinate multiple AI agents working together
* **Built-in Tools**: File operations, web search, memory management, and more
* **Flexible Configuration**: YAML-based configuration for easy setup
* **Event System**: Comprehensive event handling and middleware support
* **Memory Management**: Persistent memory with multiple backend options

Installation
------------

Install AgentX using pip:

.. code-block:: bash

   pip install agentx-py

Quick Start
-----------

Create a simple agent:

.. code-block:: python

   from agentx import Agent, execute_task

   # Create and run a simple task
   result = await execute_task(
       "Write a hello world message",
       config_path="config/team.yaml"
   )
   print(result)

API Reference
=============

The complete API reference is automatically generated from the source code:

.. toctree::
   :maxdepth: 1
   
   api/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

