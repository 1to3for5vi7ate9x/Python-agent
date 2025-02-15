import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QComboBox,
    QGroupBox,
    QFormLayout,
    QLineEdit,
    QCheckBox,
    QTextEdit,
    QPushButton,
    QDialog,
    QHBoxLayout,
    QDialogButtonBox,
    QScrollArea
)
from PyQt5.QtCore import pyqtSignal, QObject
import asyncio

from telethon.sync import TelegramClient
from telethon import errors

# Placeholder for the agent's logic. In a real application, this would be
# imported from the appropriate modules.
class Agent(QObject):
    message_received = pyqtSignal(str)
    log_updated = pyqtSignal(str, str)  # Message, Log Level

    def __init__(self):
        super().__init__()
        self.character = None
        self.prompt = None

    def set_character(self, character_name, prompt_content):
        self.character = character_name
        self.prompt = prompt_content
        self.log_updated.emit(f"Character set to: {character_name}", "info")

    # Simulate receiving a message
    async def simulate_message(self):
        await asyncio.sleep(2)  # Simulate some delay
        self.message_received.emit("Hello from the agent!")
        self.log_updated.emit("Received a message", "info")

    async def simulate_log_message(self):
        await asyncio.sleep(5)
        self.log_updated.emit("This is a warning message", "warning")

    def run_bot(self):
        self.log_updated.emit("Bot started (simulated).", "info")
        # In a real implementation, this would start the actual bot.
        # This could involve calling a function from main.py, or starting
        # a new process.


class MainWindow(QMainWindow):
    def __init__(self, agent):
        super().__init__()
        self.agent = agent
        self.setWindowTitle("Agent Control Panel")

        # --- Main Layout ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Character Selection ---
        self.character_combo = QComboBox()
        self.populate_character_dropdown()
        
        # Layout for character selection and add button
        character_layout = QHBoxLayout()
        character_layout.addWidget(self.character_combo)
        self.add_character_button = QPushButton("+")
        character_layout.addWidget(self.add_character_button)
        main_layout.addLayout(character_layout)
        

        self.prompt_editor = QTextEdit()
        self.prompt_editor.setPlaceholderText("Prompt will appear here...")
        main_layout.addWidget(self.prompt_editor)

        self.save_prompt_button = QPushButton("Save Prompt")
        main_layout.addWidget(self.save_prompt_button)

        # --- Configuration Panel ---
        config_group = QGroupBox("Configuration")
        config_scroll_area = QScrollArea() # Create scroll area
        config_scroll_area.setWidgetResizable(True) # Important!
        config_widget = QWidget() # Create a widget to hold the layout
        config_layout = QVBoxLayout(config_widget) # Put the layout on this widget

        # Agent Configuration
        agent_config_group = QGroupBox("Agent Configuration")
        agent_config_layout = QFormLayout(agent_config_group)
        self.marketing_enabled = QCheckBox()
        agent_config_layout.addRow("Marketing Messages:", self.marketing_enabled)
        self.replies_enabled = QCheckBox()
        agent_config_layout.addRow("Replies:", self.replies_enabled)
        self.debug_enabled = QCheckBox()
        agent_config_layout.addRow("Debug Logs:", self.debug_enabled)
        config_layout.addWidget(agent_config_group)

        # Marketing Configuration
        marketing_config_group = QGroupBox("Marketing Configuration")
        marketing_config_layout = QFormLayout(marketing_config_group)
        self.marketing_message_threshold_input = QLineEdit()
        marketing_config_layout.addRow("Message Threshold:", self.marketing_message_threshold_input)
        self.marketing_time_threshold_hours_input = QLineEdit()
        marketing_config_layout.addRow("Time Threshold (Hours):", self.marketing_time_threshold_hours_input)
        self.marketing_cooldown_hours_input = QLineEdit()
        marketing_config_layout.addRow("Cooldown (Hours):", self.marketing_cooldown_hours_input)
        self.marketing_activity_threshold_input = QLineEdit()
        marketing_config_layout.addRow("Activity Threshold:", self.marketing_activity_threshold_input)
        self.marketing_cooldown_reduction_input = QLineEdit()
        marketing_config_layout.addRow("Cooldown Reduction:", self.marketing_cooldown_reduction_input)
        self.marketing_min_cooldown_hours_input = QLineEdit()
        marketing_config_layout.addRow("Min Cooldown (Hours):", self.marketing_min_cooldown_hours_input)
        self.marketing_max_length_input = QLineEdit()
        marketing_config_layout.addRow("Max Length:", self.marketing_max_length_input)
        config_layout.addWidget(marketing_config_group)


        # Telegram Configuration
        telegram_config_group = QGroupBox("Telegram Configuration")
        telegram_config_layout = QFormLayout(telegram_config_group)
        self.telegram_api_id_input = QLineEdit()
        telegram_config_layout.addRow("API ID:", self.telegram_api_id_input)
        self.telegram_api_hash_input = QLineEdit()
        telegram_config_layout.addRow("API Hash:", self.telegram_api_hash_input)
        self.telegram_phone_input = QLineEdit()
        telegram_config_layout.addRow("Phone:", self.telegram_phone_input)
        self.telegram_session_name_input = QLineEdit()
        telegram_config_layout.addRow("Session Name:", self.telegram_session_name_input)
        self.telegram_allowed_chats_input = QLineEdit()
        telegram_config_layout.addRow("Allowed Chats:", self.telegram_allowed_chats_input)
        self.connect_telegram_button = QPushButton("Connect to Telegram")
        telegram_config_layout.addRow(self.connect_telegram_button)
        config_layout.addWidget(telegram_config_group)


        # Discord Configuration
        discord_config_group = QGroupBox("Discord Configuration")
        discord_config_layout = QFormLayout(discord_config_group)
        self.discord_token_input = QLineEdit()
        discord_config_layout.addRow("Token:", self.discord_token_input)
        self.discord_allowed_channels_input = QLineEdit()
        discord_config_layout.addRow("Allowed Channels:", self.discord_allowed_channels_input)
        config_layout.addWidget(discord_config_group)

        # Ollama Configuration
        ollama_config_group = QGroupBox("Ollama Configuration (Optional)")
        ollama_config_layout = QFormLayout(ollama_config_group)
        self.ollama_base_url_input = QLineEdit()
        ollama_config_layout.addRow("Base URL:", self.ollama_base_url_input)
        self.ollama_model_input = QLineEdit()
        ollama_config_layout.addRow("Model:", self.ollama_model_input)
        config_layout.addWidget(ollama_config_group)

        # Gemini Configuration
        gemini_config_group = QGroupBox("Gemini Configuration")
        gemini_config_layout = QFormLayout(gemini_config_group)
        self.gemini_api_key_input = QLineEdit()
        gemini_config_layout.addRow("API Key:", self.gemini_api_key_input)
        config_layout.addWidget(gemini_config_group)
        
        # Proxy Configuration
        proxy_config_group = QGroupBox("Proxy Configuration (Optional)")
        proxy_config_layout = QFormLayout(proxy_config_group)
        self.telegram_proxy_host_input = QLineEdit()
        proxy_config_layout.addRow("Telegram Proxy Host:", self.telegram_proxy_host_input)
        self.telegram_proxy_port_input = QLineEdit()
        proxy_config_layout.addRow("Telegram Proxy Port:", self.telegram_proxy_port_input)
        self.telegram_proxy_username_input = QLineEdit()
        proxy_config_layout.addRow("Telegram Proxy Username:", self.telegram_proxy_username_input)
        self.telegram_proxy_password_input = QLineEdit()
        proxy_config_layout.addRow("Telegram Proxy Password:", self.telegram_proxy_password_input)
        config_layout.addWidget(proxy_config_group)

        self.save_config_button = QPushButton("Save Config")
        config_layout.addWidget(self.save_config_button)

        config_scroll_area.setWidget(config_widget)  # Set the content widget
        main_layout.addWidget(config_scroll_area)  # Add the scroll area to the main layout

        # --- Run Button ---
        self.run_button = QPushButton("Run Bot")
        main_layout.addWidget(self.run_button)

        # --- Conversation Log ---
        self.conversation_log = QTextEdit()
        self.conversation_log.setReadOnly(True)
        self.conversation_log.setPlaceholderText("Conversation will appear here...")
        main_layout.addWidget(self.conversation_log)

        # --- Logging Display ---
        self.logging_display = QTextEdit()
        self.logging_display.setReadOnly(True)
        self.logging_display.setPlaceholderText("Logs will appear here...")
        main_layout.addWidget(self.logging_display)

        # --- Connections ---
        self.character_combo.currentIndexChanged.connect(self.character_selected)
        self.agent.message_received.connect(self.append_message)
        self.agent.log_updated.connect(self.append_log)
        self.save_config_button.clicked.connect(self.save_config)
        self.save_prompt_button.clicked.connect(self.save_prompt)
        self.add_character_button.clicked.connect(self.add_new_character)
        self.connect_telegram_button.clicked.connect(lambda: asyncio.create_task(self.connect_to_telegram()))
        self.run_button.clicked.connect(self.agent.run_bot)

        # --- Initial setup ---
        self.load_config() # Load initial config

        # --- Simulate some agent activity (for testing) ---
        asyncio.create_task(self.agent.simulate_message())
        asyncio.create_task(self.agent.simulate_log_message())


    def populate_character_dropdown(self):
        templates_dir = os.path.join("characters", "templates")
        try:
            # Get list of .json files, remove extension
            characters = [
                os.path.splitext(f)[0]
                for f in os.listdir(templates_dir)
                if f.endswith(".json")
            ]
            self.character_combo.addItems(characters)
        except FileNotFoundError:
            self.logging_display.append(
                '<font color="red">Error: characters/templates directory not found.</font>'
            )
            # Disable character selection, or handle the error as appropriate.

    def character_selected(self):
        character_name = self.character_combo.currentText()
        prompt_path = os.path.join(
            "prompts", f"{character_name}_prompt.txt"
        )
        if character_name == "neuronlinkenthusiast":
            prompt_path = os.path.join(
                "prompts", "neuronlink_prompt.txt"
            )
        try:
            with open(prompt_path, "r") as f:
                prompt_content = f.read()
            self.agent.set_character(character_name, prompt_content)
            self.prompt_editor.setText(prompt_content)

        except FileNotFoundError:
            self.logging_display.append(
                f'<font color="red">Error: Prompt file not found for {character_name}.</font>'
            )
            # Consider disabling further actions or showing an error message.

    def save_prompt(self):
        character_name = self.character_combo.currentText()
        if not character_name:
            self.logging_display.append('<font color="red">No character selected.</font>')
            return

        prompt_path = os.path.join(
            "prompts", f"{character_name}_prompt.txt"
        )
        if character_name == "neuronlinkenthusiast":
            prompt_path = os.path.join("prompts", "neuronlink_prompt.txt")

        try:
            with open(prompt_path, "w") as f:
                f.write(self.prompt_editor.toPlainText())
            self.logging_display.append(f'<font color="green">Prompt saved for {character_name}.</font>')
            self.agent.set_character(character_name, self.prompt_editor.toPlainText()) # Update the agent
        except Exception as e:
            self.logging_display.append(f'<font color="red">Error saving prompt: {e}</font>')

    def append_message(self, message):
        self.conversation_log.append(message)

    def append_log(self, message, level):
        color = "black"  # Default
        if level == "warning":
            color = "orange"
        elif level == "error":
            color = "red"
        elif level == "debug":
            color = "blue"
        elif level == "info":
            color = "green"

        self.logging_display.append(f'<font color="{color}">{message}</font>')

    def save_config(self):
        config_data = {
            "marketing_enabled": self.marketing_enabled.isChecked(),
            "replies_enabled": self.replies_enabled.isChecked(),
            "debug_enabled": self.debug_enabled.isChecked(),
            "marketing_message_threshold": self.marketing_message_threshold_input.text(),
            "marketing_time_threshold_hours": self.marketing_time_threshold_hours_input.text(),
            "marketing_cooldown_hours": self.marketing_cooldown_hours_input.text(),
            "marketing_activity_threshold": self.marketing_activity_threshold_input.text(),
            "marketing_cooldown_reduction": self.marketing_cooldown_reduction_input.text(),
            "marketing_min_cooldown_hours": self.marketing_min_cooldown_hours_input.text(),
            "marketing_max_length": self.marketing_max_length_input.text(),
            "telegram_api_id": self.telegram_api_id_input.text(),
            "telegram_api_hash": self.telegram_api_hash_input.text(),
            "telegram_phone": self.telegram_phone_input.text(),
            "telegram_session_name": self.telegram_session_name_input.text(),
            "telegram_allowed_chats": self.telegram_allowed_chats_input.text(),
            "discord_token": self.discord_token_input.text(),
            "discord_allowed_channels": self.discord_allowed_channels_input.text(),
            "ollama_base_url": self.ollama_base_url_input.text(),
            "ollama_model": self.ollama_model_input.text(),
            "gemini_api_key": self.gemini_api_key_input.text(),
            "telegram_proxy_host": self.telegram_proxy_host_input.text(),
            "telegram_proxy_port": self.telegram_proxy_port_input.text(),
            "telegram_proxy_username": self.telegram_proxy_username_input.text(),
            "telegram_proxy_password": self.telegram_proxy_password_input.text(),
        }

        config_file_path = "config.json"

        try:
            with open(config_file_path, 'w') as config_file:
                import json
                json.dump(config_data, config_file, indent=4)
            self.logging_display.append(f'<font color="green">Configuration saved to {config_file_path}</font>')
        except Exception as e:
            self.logging_display.append(f'<font color="red">Error saving config: {e}</font>')



    def load_config(self):
        config_file_path = "config.json"
        try:
            with open(config_file_path, 'r') as config_file:
                import json
                config_data = json.load(config_file)

                self.marketing_enabled.setChecked(config_data.get("marketing_enabled", False))
                self.replies_enabled.setChecked(config_data.get("replies_enabled", False))
                self.debug_enabled.setChecked(config_data.get("debug_enabled", False))
                self.marketing_message_threshold_input.setText(config_data.get("marketing_message_threshold", ""))
                self.marketing_time_threshold_hours_input.setText(config_data.get("marketing_time_threshold_hours", ""))
                self.marketing_cooldown_hours_input.setText(config_data.get("marketing_cooldown_hours", ""))
                self.marketing_activity_threshold_input.setText(config_data.get("marketing_activity_threshold", ""))
                self.marketing_cooldown_reduction_input.setText(config_data.get("marketing_cooldown_reduction", ""))
                self.marketing_min_cooldown_hours_input.setText(config_data.get("marketing_min_cooldown_hours", ""))
                self.marketing_max_length_input.setText(config_data.get("marketing_max_length", ""))
                self.telegram_api_id_input.setText(config_data.get("telegram_api_id", ""))
                self.telegram_api_hash_input.setText(config_data.get("telegram_api_hash", ""))
                self.telegram_phone_input.setText(config_data.get("telegram_phone", ""))
                self.telegram_session_name_input.setText(config_data.get("telegram_session_name", ""))
                self.telegram_allowed_chats_input.setText(config_data.get("telegram_allowed_chats", ""))
                self.discord_token_input.setText(config_data.get("discord_token", ""))
                self.discord_allowed_channels_input.setText(config_data.get("discord_allowed_channels", ""))
                self.ollama_base_url_input.setText(config_data.get("ollama_base_url", ""))
                self.ollama_model_input.setText(config_data.get("ollama_model", ""))
                self.gemini_api_key_input.setText(config_data.get("gemini_api_key", ""))
                self.telegram_proxy_host_input.setText(config_data.get("telegram_proxy_host", ""))
                self.telegram_proxy_port_input.setText(config_data.get("telegram_proxy_port", ""))
                self.telegram_proxy_username_input.setText(config_data.get("telegram_proxy_username", ""))
                self.telegram_proxy_password_input.setText(config_data.get("telegram_proxy_password", ""))

            self.logging_display.append(f'<font color="green">Configuration loaded from {config_file_path}</font>')

        except FileNotFoundError:
            self.logging_display.append(f'<font color="orange">Config file ({config_file_path}) not found. Using defaults.</font>')
        except Exception as e:
            self.logging_display.append(f'<font color="red">Error loading config: {e}</font>')


    async def connect_to_telegram(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Connect to Telegram")
        layout = QVBoxLayout(dialog)

        phone_input = QLineEdit()
        phone_input.setPlaceholderText("Phone Number")
        layout.addWidget(phone_input)

        code_input = QLineEdit()
        code_input.setPlaceholderText("Telegram Code")
        code_input.hide() # Initially hidden
        layout.addWidget(code_input)

        send_code_button = QPushButton("Send Code")
        layout.addWidget(send_code_button)

        login_button = QPushButton("Login")
        login_button.hide() # Initially hidden
        layout.addWidget(login_button)

        buttons = QDialogButtonBox(QDialogButtonBox.Cancel, dialog)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        client = None

        async def send_code_clicked():
            nonlocal client
            phone = phone_input.text().strip()
            if not phone:
                self.logging_display.append('<font color="red">Phone number is required.</font>')
                return

            api_id = self.telegram_api_id_input.text().strip()
            api_hash = self.telegram_api_hash_input.text().strip()

            if not api_id or not api_hash:
                self.logging_display.append('<font color="red">Telegram API ID and API Hash are required.</font>')
                dialog.reject() # Close on error.
                return
            try:
                api_id = int(api_id)
            except ValueError:
                self.logging_display.append('<font color="red">Telegram API ID must be a number.</font>')
                return

            try:
                client = TelegramClient('telegram_auth', api_id, api_hash) # Use a temporary session name
                await client.connect()
                if not await client.is_user_authorized():
                    await client.send_code_request(phone)
                    phone_input.setEnabled(False)
                    send_code_button.hide()
                    code_input.show()
                    login_button.show()

            except errors.ApiIdInvalidError:
                self.logging_display.append('<font color="red">Invalid API ID/Hash.</font>')
                dialog.reject()
            except errors.PhoneNumberInvalidError:
                self.logging_display.append('<font color="red">Invalid phone number.</font>')
            except Exception as e:
                self.logging_display.append(f'<font color="red">Error sending code: {e}</font>')
                if client:
                    await client.disconnect()

        async def login_clicked():
            nonlocal client
            code = code_input.text().strip()
            phone = phone_input.text().strip()
            if not code:
                self.logging_display.append('<font color="red">Code is required.</font>')
                return

            try:
                await client.sign_in(phone, code)
                self.logging_display.append('<font color="green">Successfully logged in to Telegram.</font>')
                # Get the session name and update the input field
                session_name = phone
                self.telegram_session_name_input.setText(session_name)
                dialog.accept()

            except errors.SessionPasswordNeededError:
                self.logging_display.append('<font color="red">Two-factor authentication is enabled. Cannot login.</font>')
            except errors.PhoneCodeInvalidError:
                self.logging_display.append('<font color="red">Invalid code.</font>')
            except Exception as e:
                self.logging_display.append(f'<font color="red">Error logging in: {e}</font>')
            finally:
                if client:
                    await client.disconnect()

        send_code_button.clicked.connect(send_code_clicked)
        login_button.clicked.connect(login_clicked)

        dialog.exec_()


    def add_new_character(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Character")
        layout = QVBoxLayout(dialog)

        name_input = QLineEdit()
        name_input.setPlaceholderText("Character Name")
        layout.addWidget(name_input)

        prompt_input = QTextEdit()
        prompt_input.setPlaceholderText("Enter prompt here...")
        prompt_input.setText("You are a helpful assistant.") # Default prompt
        layout.addWidget(prompt_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec_() == QDialog.Accepted:
            character_name = name_input.text().strip()
            prompt_content = prompt_input.toPlainText()

            if not character_name:
                self.logging_display.append('<font color="red">Character name cannot be empty.</font>')
                return

            # Sanitize character name for filename
            character_name_safe = "".join(c if c.isalnum() else "_" for c in character_name)

            template_path = os.path.join("characters", "templates", f"{character_name_safe}.json")
            prompt_path = os.path.join("prompts", f"{character_name_safe}_prompt.txt")

            # Check if character already exists
            if os.path.exists(template_path) or os.path.exists(prompt_path):
                self.logging_display.append(f'<font color="red">Character "{character_name}" already exists.</font>')
                return

            try:
                # Create template file (empty JSON object)
                with open(template_path, "w") as f:
                    import json
                    json.dump({}, f)  # Empty JSON object

                # Create prompt file
                with open(prompt_path, "w") as f:
                    f.write(prompt_content)

                self.logging_display.append(f'<font color="green">Character "{character_name}" created.</font>')
                self.populate_character_dropdown()  # Refresh dropdown
                self.character_combo.setCurrentText(character_name_safe) # Select the new character

            except Exception as e:
                self.logging_display.append(f'<font color="red">Error creating character: {e}</font>')


async def main():
    app = QApplication(sys.argv)
    agent = Agent()
    main_window = MainWindow(agent)
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    asyncio.run(main())