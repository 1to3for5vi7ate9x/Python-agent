# Project Information: Python Agent

This document provides a concise overview of the Python Agent project.

## Description

A flexible Python-based agent system capable of operating on both Telegram and Discord using user accounts (not bots). It features multiple character personalities and integrates with LLMs (Ollama and Gemini) for natural language conversations. The agent can be configured with different characters, each having its own prompt and behavior.

## Key Features

-   **Multi-Platform Support:** Operates on Telegram and Discord using user accounts.
-   **Character Personalities:** Supports multiple character personalities defined through JSON templates and prompt files.
-   **Character Selection:** Allows selection of a character at startup.
-   **LLM Integration:** Integrates with Ollama and Gemini for natural language generation.
-   **Environment Controls:** Provides environment variables for configuring marketing messages, replies, and debug logs.
-   **Asynchronous Operations:** Uses `async/await` for concurrent operations.
-   **Logging:** Includes advanced logging with configurable verbosity.
-   **Human-like Behavior:** Simulates human-like behavior with typing indicators and response delays.

## Project Structure

The project is organized into the following directories:

-   `characters/`: Contains character definitions and templates.
    -   `templates/`: JSON files defining character attributes and prompt file locations.
-   `clients/`: Contains client implementations for interacting with Telegram and Discord.
    -   `telegram/`: Telegram client and message manager.
    -   `discord/`: Discord client and message manager.
-   `core/`: Contains core functionalities like character management, generation, and message handling.
    -   `character_manager.py`: Manages character selection and loading.
    -   `generation.py`: Handles interaction with LLMs for text generation.
    -   `marketing_manager.py`: Manages marketing messages.
    -   `message_handler.py`: Processes incoming messages.
-   `prompts/`: Contains text files defining character prompts for the LLMs.
-   `main.py`: The main entry point for the application.
-   `requirements.txt`: Lists project dependencies.
-  `.env`: Stores environment variables for configuration (API keys, tokens, etc.).
-  `README.md`: Project documentation.

## Setup

1.  **Virtual Environment:** Create and activate a Python 3.11 (recommended) virtual environment.
2.  **Dependencies:** Install dependencies using `pip install -r requirements.txt`.
3.  **Environment Variables:** Create a `.env` file and configure the necessary environment variables (see README.md for details).
4.  **Character Configuration:** Edit or create character templates in `characters/templates/` and corresponding prompt files in `prompts/`.
5. **Run:** Execute the agent with `python main.py`.

## Character Configuration

Characters are defined by JSON templates in `characters/templates/` and corresponding prompt files in `prompts/`. The JSON template specifies the character's name, username, model provider, model, supported clients, and the path to the prompt file. The prompt file contains a detailed description of the character's persona and instructions for the LLM.