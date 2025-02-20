import httpx
from typing import Optional, Dict, Any, List
from loguru import logger
import json
import os
import google.generativeai as genai
import time
import asyncio


class GeminiGenerationManager:
    def __init__(self, api_key: str = None, default_model: str = "gemini-1.5-flash-002"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set the GEMINI_API_KEY environment variable.")
        genai.configure(api_key=self.api_key)
        self.default_model = default_model
        self.model = genai.GenerativeModel(self.default_model)
        self.last_request_time = 0
        self.rate_limit_delay = 2  # seconds
        logger.info(f"Initializing GeminiGenerationManager with default model: {self.default_model}")

    async def generate_text(self, context: str, model: str = None, personality: str = "") -> str:
        """Generate text using the specified Gemini model."""
        try:
            # Apply rate limiting
            current_time = time.time()
            time_since_last_request = current_time - self.last_request_time
            if time_since_last_request < self.rate_limit_delay:
                delay = self.rate_limit_delay - time_since_last_request
                logger.info(f"Applying rate limit. Delaying for {delay:.2f} seconds.")
                await asyncio.sleep(delay)

            logger.debug(f"Starting Gemini text generation process with model: {model or self.default_model}")

            # Incorporate personality into the context
            if personality:
                context = f"Personality: {personality}\n\n{context}"

            chat = self.model.start_chat()

            response = await chat.send_message_async(context)
            self.last_request_time = time.time()  # Update last request time


            if response.text:
                generated_text = response.text.strip()
                logger.debug(f"Successfully generated {len(generated_text)} characters")
                return generated_text
            else:
                logger.error("Gemini generation failed: No text returned")
                return "[INTERNAL] Gemini generation failed: No text returned"

        except Exception as e:
            logger.error(f"Unexpected error during Gemini generation: {str(e)}")
            return f"[INTERNAL] An unexpected error occurred with Gemini: {str(e)}"

    async def generate_marketing_message(self, template: str, character_name: str) -> str:
        """Generate a marketing message using the template with Gemini."""
        try:
            logger.debug(f"Generating Gemini marketing message for character: {character_name}")
            response = await self.generate_text(template)
            if not response.startswith("[INTERNAL]"):
                cleaned_response = response.strip().strip('"\'')
                logger.debug(f"Generated Gemini marketing message of length {len(cleaned_response)}")
                return cleaned_response
            logger.error(f"Failed to generate Gemini marketing message: {response}")
            return ""
        except Exception as e:
            logger.error(f"Error in Gemini marketing message generation: {str(e)}")
            return ""

class GenerationManager:
    def __init__(self, model_provider: str = "ollama", base_url: str = None, default_model: str = None, api_key: str = None):
        self.model_provider = model_provider.lower()
        self.base_url = base_url
        self.default_model = default_model
        self.api_key = api_key
        self.generator = self._initialize_generator()

        logger.info(f"Initializing GenerationManager with provider: {self.model_provider}")

    def _initialize_generator(self):
        if self.model_provider == "ollama":
            return OllamaGenerationManager(base_url=self.base_url, default_model=self.default_model)
        elif self.model_provider == "gemini":
            return GeminiGenerationManager(api_key=self.api_key, default_model=self.default_model)
        else:
            raise ValueError(f"Unsupported model provider: {self.model_provider}")

    async def generate_text(self, context: str, model: str = None, personality: str = "") -> str:
        return await self.generator.generate_text(context, model, personality)

    async def generate_marketing_message(self, template: str, character_name: str) -> str:
        return await self.generator.generate_marketing_message(template, character_name)


class OllamaGenerationManager:
    def __init__(self, base_url: str = None, default_model: str = None):
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.default_model = default_model or os.getenv("OLLAMA_MODEL", "llama3.3:latest")
        self.client = None
        logger.info(f"Initializing OllamaGenerationManager with base URL: {self.base_url} and default model: {self.default_model}")

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create an HTTP client"""
        if self.client is None or self.client.is_closed:
            logger.debug("Creating new HTTP client")
            self.client = httpx.AsyncClient(timeout=60.0)
        return self.client

    async def _check_server_connection(self) -> bool:
        """Check if the Ollama server is accessible"""
        try:
            client = await self._get_client()
            logger.debug(f"Checking server connection at {self.base_url}")
            response = await client.get(f"{self.base_url}/api/version")
            if response.status_code == 200:
                version = response.json().get('version')
                logger.info(f"Connected to Ollama server version: {version}")
                return True
            logger.error(f"Failed to connect to Ollama server: {response.status_code} - {response.text}")
            return False
        except httpx.ConnectError as e:
            logger.error(f"Connection error to Ollama server at {self.base_url}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking server connection: {str(e)}")
            return False

    async def _list_models(self) -> List[str]:
        """Get list of available models from the Ollama server"""
        try:
            client = await self._get_client()
            logger.debug("Fetching available models")
            response = await client.get(f"{self.base_url}/api/tags")

            if response.status_code == 200:
                models = [m.get('name') for m in response.json().get('models', [])]
                logger.debug(f"Found {len(models)} models: {models}")
                return models

            logger.error(f"Failed to list models: {response.status_code} - {response.text}")
            return []
        except httpx.ConnectError as e:
            logger.error(f"Connection error while listing models: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error listing models: {str(e)}")
            return []

    async def generate_text(self, context: str, model: str = None) -> str:
        """Generate text using the specified model"""
        try:
            # First check server connection
            logger.debug("Starting text generation process")
            if not await self._check_server_connection():
                return "[INTERNAL] Could not connect to Ollama server"

            # List available models
            available_models = await self._list_models()
            if not available_models:
                return "[INTERNAL] No models available on the server"

            # Use default model if none specified
            model_to_use = model or self.default_model
            logger.debug(f"Using model: {model_to_use}")

            if model_to_use not in available_models:
                logger.error(f"Model '{model_to_use}' not found. Available models: {available_models}")
                return f"[INTERNAL] Model '{model_to_use}' not available. Please use one of: {', '.join(available_models)}"

            client = await self._get_client()
            logger.debug(f"Generating text with model: {model_to_use}")
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model_to_use,
                    "prompt": context,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "top_k": 40,
                        "num_predict": 100,
                    }
                }
            )

            if response.status_code != 200:
                logger.error(f"API error: {response.status_code} - {response.text}")
                return "[INTERNAL] Error communicating with language model"

            result = response.json()
            if 'response' not in result:
                logger.error(f"Unexpected response format: {json.dumps(result, indent=2)}")
                return "[INTERNAL] Invalid response from language model"

            generated_text = result['response'].strip()
            logger.debug(f"Successfully generated {len(generated_text)} characters")
            return generated_text

        except httpx.ConnectError as e:
            logger.error(f"Connection error during generation: {e}")
            return "[INTERNAL] Connection error with language model server"
        except Exception as e:
            logger.error(f"Unexpected error during generation: {str(e)}")
            return "[INTERNAL] An unexpected error occurred"

    async def generate_marketing_message(self, template: str, character_name: str) -> str:
        """Generate a marketing message using the template"""
        try:
            logger.debug(f"Generating marketing message for character: {character_name}")
            response = await self.generate_text(template)
            if not response.startswith("[INTERNAL]"):
                cleaned_response = response.strip().strip('"\'')
                logger.debug(f"Generated marketing message of length {len(cleaned_response)}")
                return cleaned_response
            logger.error(f"Failed to generate marketing message: {response}")
            return ""

        except Exception as e:
            logger.error(f"Error in marketing message generation: {str(e)}")
            return ""