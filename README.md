# Python Agent Eliza

A Python implementation of the Eliza agent system using Telegram and Discord user accounts (not bots).

## Features

- Support for both Telegram and Discord platforms using user accounts
- Character-based responses using LLM integration
- Async/await support for concurrent operations
- Type safety with Pydantic models
- Advanced logging with Loguru
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

3. Configure your character:
- Edit or create new character templates in `characters/templates/`
- Follow the format in `cryptoshiller.json`

4. Run the agent:
```bash
python main.py
```

On first run, you'll be prompted to enter the verification code sent to your Telegram account.

## Project Structure

```
python-agent/
├── requirements.txt
├── README.md
├── characters/
│   ├── base.py
│   └── templates/
│       └── cryptoshiller.json
├── core/
│   ├── generation.py
│   ├── environment.py
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
