# Python Agent

A flexible Python-based agent system that can operate on both Telegram and Discord using user accounts (not bots). Features multiple character personalities and LLM integration for natural conversations.

## Features

- Multi-platform support (Telegram and Discord) using user accounts
- Multiple character personalities defined through prompt files
- Character selection at startup
- LLM integration (Ollama and Gemini) for natural language generation
- Environment controls for marketing and debug features
- Async/await support for concurrent operations
- Advanced logging with configurable verbosity
- Human-like behavior with typing indicators and response delays

## Requirements

- Python 3.11 (recommended) or later
- pip (will be automatically upgraded to latest version)

## Setup

1. Create and activate virtual environment:
```bash
# Create virtual environment with Python 3.11
python3.11 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

2. Install dependencies:
```bash
# Make sure your virtual environment is activated (venv)
# First, upgrade pip to latest version
pip install --upgrade pip

# Then install project dependencies
pip install -r requirements.txt
```

2. Set up environment variables:
Create a `.env` file with:
```env
# Telegram User Account Settings
TELEGRAM_API_ID=your_api_id          # Get from https://my.telegram.org
TELEGRAM_API_HASH=your_api_hash      # Get from https://my.telegram.org
TELEGRAM_PHONE=your_phone_number     # Format: +1234567890
TELEGRAM_SESSION_NAME=user_session

# Discord User Account
DISCORD_TOKEN=your_user_token        # Your Discord user account token

# Allowed Channels/Groups (comma-separated)
TELEGRAM_ALLOWED_CHATS=-100123456789,-100987654321
DISCORD_ALLOWED_CHANNELS=channel_id1,channel_id2

# Optional: Proxy Settings
# TELEGRAM_PROXY_HOST=
# TELEGRAM_PROXY_PORT=
# TELEGRAM_PROXY_USERNAME=
# TELEGRAM_PROXY_PASSWORD=

# Gemini Settings
GEMINI_API_KEY=your_gemini_api_key  # Replace with your actual Gemini API key
```

3. Configure environment:
```env
# Agent Configuration
ENABLE_MARKETING=true    # Enable/disable marketing messages
ENABLE_REPLIES=true      # Enable/disable reply messages
ENABLE_DEBUG_LOGS=false  # Enable/disable debug logging

# Marketing Configuration
MARKETING_MESSAGE_THRESHOLD=5      # Number of messages before marketing trigger
MARKETING_TIME_THRESHOLD_HOURS=6.0 # Hours before time-based marketing trigger
MARKETING_COOLDOWN_HOURS=6.0       # Hours to wait between marketing messages
MARKETING_RANDOM_CHANCE=0.2        # Probability (0-1) of random marketing trigger
MARKETING_MAX_LENGTH=500           # Maximum length of marketing messages

# Ollama Configuration (optional if using Gemini)
OLLAMA_BASE_URL=http://localhost:11434  # Remove if not using Ollama
OLLAMA_MODEL=llama3.3:latest          # Remove if not using Ollama
```
4. Configure characters:

- Edit or create character templates in `characters/templates/`.
- Create corresponding prompt files in `prompts/`.
- Available templates:
    - `cryptoshiller.json`: Crypto trading expert
    - `techsupport.json`: Technical support specialist
    - `fitnesscoach.json`: Fitness and wellness coach
    - `neuronlinkenthusiast.json`: Enthusiastic NeuronLink user
- Create new characters by adding JSON files to the templates directory and corresponding prompt files to the `prompts/` directory.

5. Run the agent:
```bash
python main.py
```

On first run:

1.  Select a character from the available options.
2.  Enter the verification code sent to your Telegram account (if using Telegram).

## Project Structure

```
python-agent/
├── requirements.txt
├── README.md
├── characters/
│   ├── base.py
│   └── templates/
│       ├── cryptoshiller.json
│       ├── techsupport.json
│       ├── fitnesscoach.json
│       └── neuronlinkenthusiast.json
├── core/
│   ├── generation.py
│   ├── character_manager.py
│   ├── marketing_manager.py
│   ├── message_handler.py
│   └── types.py
├── clients/
│   ├── base.py
│   ├── telegram/
│   │   ├── client.py
│   │   └── message_manager.py
│   └── discord/
│       ├── client.py
│       └── message_manager.py
├── prompts/
│   ├── cryptoshiller_prompt.txt
│   ├── fitnesscoach_prompt.txt
│   ├── neuronlink_prompt.txt
│   └── techsupport_prompt.txt
└── main.py
```
## Character Templates and Prompts

Character templates are simplified JSON files in `characters/templates/` that define basic character information and point to a prompt file.  The structure is:

```json
{
    "name": "YourCharacterName",
    "username": "yourcharacter_bot",
    "modelProvider": "gemini",
    "model": "gemini-1.5-flash-002",
    "clients": ["telegram", "discord"],
    "prompt_file": "prompts/yourcharacter_prompt.txt"
}
```

Create a corresponding prompt file in the `prompts/` directory. This file should contain a detailed description of the character's persona, communication style, and instructions for the LLM.  See the existing prompt files for examples.

## Development

- Use Python 3.11 or higher
- Follow PEP 8 style guide
- Add type hints for all functions
- Use async/await for I/O operations

## Testing
(Testing section to be updated later)

## License

MIT License
