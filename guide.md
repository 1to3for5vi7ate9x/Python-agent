# Agent GUI Guide

This guide explains how to use the graphical user interface (GUI) for the Python-based agent.

## Character Selection

1.  **Character Dropdown:** Select a character template from the dropdown menu. This will load the corresponding prompt into the prompt editor.
2.  **Prompt Editor:** View and edit the prompt for the selected character.
3.  **Save Prompt:** Click the "Save Prompt" button to save any changes you make to the prompt. The changes are saved to the corresponding `_prompt.txt` file in the `prompts/` directory.
4.  **Add Character (+):** Click the "+" button to add a new character. A dialog will appear:
    *   Enter the character name.
    *   Enter the prompt content.
    *   Click "Ok" to create the character. This will create a new `.json` file in `characters/templates/` and a `_prompt.txt` file in `prompts/`. The new character will be added to the dropdown.

## Configuration

The configuration panel allows you to set various parameters for the agent.  Click "Save Config" to save the settings to `config.json`. The settings are automatically loaded when the GUI starts.

### Agent Configuration

*   **Marketing Messages:** Enable or disable marketing messages.
*   **Replies:** Enable or disable agent replies.
*   **Debug Logs:** Enable or disable debug logging.

### Marketing Configuration

*   **Message Threshold:** Number of messages before a marketing message can be triggered.
*   **Time Threshold (Hours):** Time (in hours) before a marketing message can be triggered.
*   **Cooldown (Hours):** Base cooldown period between marketing messages.
*   **Activity Threshold:** Number of messages to consider a group active.
*   **Cooldown Reduction:** Hours to reduce the cooldown per activity.
*   **Min Cooldown (Hours):** Minimum cooldown period.
*   **Max Length:** Maximum length of marketing messages.

### Telegram Configuration

1.  **API ID:** Enter your Telegram API ID.
2.  **API Hash:** Enter your Telegram API hash.
3.  **Phone:** Enter your phone number, including the country code (e.g., +15551234567).
4.  **Session Name:** This field will be automatically populated after you connect to Telegram.
5.  **Allowed Chats:** Enter a comma-separated list of allowed Telegram chat IDs.
6.  **Connect to Telegram:** Click this button to authenticate with Telegram:
    *   If you haven't logged in before (or if the session is invalid), a dialog will appear.
    *   Enter your phone number if it is not already filled.
    *   Click "Send Code".
    *   You will receive a code via Telegram. Enter the code in the dialog.
    *   Click "Login".
    *   If successful, your session name will be saved, and you won't need to enter the code again unless the session expires.

### Discord Configuration

1.  **Token:** Enter your Discord user token.
2.  **Allowed Channels:** Enter a comma-separated list of allowed Discord channel IDs.

### Ollama Configuration (Optional)

1.  **Base URL:** Enter the base URL for your Ollama instance (if using Ollama).
2.  **Model:** Enter the Ollama model name (if using Ollama).

### Gemini Configuration

1. **API Key:** Enter your Google Gemini API key.

### Proxy Configuration (Optional)

1.  **Telegram Proxy Host:** Enter your Telegram proxy host (if using a proxy).
2.  **Telegram Proxy Port:** Enter your Telegram proxy port (if using a proxy).
3.  **Telegram Proxy Username:** Enter your Telegram proxy username (if using a proxy).
4.  **Telegram Proxy Password:** Enter your Telegram proxy password (if using a proxy).

## Running the Bot

1.  **Run Bot:** Click the "Run Bot" button to start the agent.  (Currently, this is a simulated action. In a full implementation, this would start the actual bot process.)

## Logging

*   **Conversation Log:** Displays real-time messages between the user and the agent.
*   **Logging Display:** Shows log messages (info, warnings, errors, debug) from the agent and the GUI.