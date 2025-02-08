# Python Agent

A flexible Python-based agent system that can operate on both Telegram and Discord using user accounts (not bots). Features multiple character personalities and LLM integration for natural conversations.

## Features

- Multi-platform support (Telegram and Discord) using user accounts
- Multiple character personalities with easy customization
- Character selection at startup
- LLM integration for natural language generation
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
```

3. Configure environment:
```env
# Agent Configuration
ENABLE_MARKETING=true    # Enable/disable marketing messages
ENABLE_REPLIES=true      # Enable/disable reply messages
ENABLE_DEBUG_LOGS=false  # Enable/disable debug logging

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.3:latest
```

4. Configure characters:
- Edit or create character templates in `characters/templates/`
- Available templates:
  - `cryptoshiller.json`: Crypto trading expert
  - `techsupport.json`: Technical support specialist
  - `fitnesscoach.json`: Fitness and wellness coach
- Create new characters by adding JSON files to the templates directory

5. Run the agent:
```bash
python main.py
```

On first run:
1. Select a character from the available options
2. Enter the verification code sent to your Telegram account

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
│       └── fitnesscoach.json
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
└── main.py
```

## Character Templates

Create new characters by adding JSON files to `characters/templates/` following this structure:

```json
{
    "name": "YourCharacterName",
    "username": "username_bot",
    "modelProvider": "ollama",
    "clients": ["telegram", "discord"],
    
    "personality": {},
    "communication": {},
    
    "templates": {
        "reply": "Your character's reply template here: {message}",
        "marketing": "Your character's marketing message template here"
    },
    
    "rules": {
        "message": {
            "min_length": 10,
            "max_length": 150,
            "response_chance": 0.6
        },
        "blocked_terms": ["spam", "bot", "scam", "fake"]
    }
}
```

## Development

- Use Python 3.8 or higher
- Follow PEP 8 style guide
- Add type hints for all functions
- Use async/await for I/O operations

## Testing

Run tests with pytest:
```bash
pytest
```

## License

MIT License
