"""Config file. Here we set the bot configuration and load it from a json file."""

import json
import os
from typing import Any, Dict, List

from dotenv import load_dotenv

load_dotenv()


class Config:
    _instance = None

    def __new__(cls) -> "Config":
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _open_config_file(self) -> Dict[str, Any]:
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        try:
            with open(config_path, "r") as config_file:
                return json.load(config_file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise RuntimeError(
                f"The configuration file was not found or not loaded correctly: {e}"
            )

    def _load_config(self) -> None:
        config_data = self._open_config_file()
        self._token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self._api_base_url: str = config_data.get("api_base_url", "")
        self._api_services: Dict[str, List] = config_data.get("services", {})

        self._validate_config()

    def _validate_config(self) -> None:
        if not self._token:
            raise ValueError("`TELEGRAM_BOT_TOKEN` wasn't defined in .env vars.")
        if not self._api_base_url:
            raise ValueError("`api_base_url` wasn't defined in config.json file.")
        if not isinstance(self._api_services, dict):
            raise ValueError(
                f"`services` should be a dict, received: {type(self._api_services)}."
            )

    def get_available_api_services(self) -> List[str]:
        """returns a list of available services."""
        return list(self._api_services.get("available", []).keys())

    def get_api_endpoints(self) -> List[str]:
        """returns a list of API endpoints."""
        return list(self._api_services.get("available", []).values())

    @property
    def token(self) -> str:
        """returns the Telegram bot token."""
        return self._token

    @property
    def api_base_url(self) -> str:
        """returns the API base URL."""
        return self._api_base_url

    @property
    def available_api_services(self) -> Dict[str, List]:
        """returns the API services."""
        return self._api_services.get("available", {})
