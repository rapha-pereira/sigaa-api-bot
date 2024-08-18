"""APIs module. Contains the APIs handlers classes."""

from dataclasses import dataclass
from urllib.parse import urljoin

import httpx


@dataclass
class SIGAA:
    """Dataclass for SIGAA API."""

    base_url: str
    endpoints_mapping: dict


class SIGAAClient:
    def __init__(self):
        from sigaa_api_bot.bot.main import api_available_services_dict, api_base_url

        self.sigaa = SIGAA(
            base_url=api_base_url,
            endpoints_mapping=api_available_services_dict,
        )

    async def call(self, endpoint: str, auth: tuple) -> httpx.Response:
        """Call the API."""
        async with httpx.AsyncClient() as client:
            url = urljoin(
                self.sigaa.base_url, self.sigaa.endpoints_mapping.get(endpoint)
            )
            response = await client.get(url=url, auth=auth, timeout=40)
            response.raise_for_status()
            return response.json()
