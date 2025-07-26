import os
import requests

class HASSLightController:
    """
    Controller for sending effect commands to Home Assistant lights via REST API.
    Uses %HASS_SERVER% and %HASS_TOKEN% environment variables.
    """

    def __init__(self, base_url=None, token=None):
        """
        Initialize the controller.

        Args:
            base_url (str): Base URL of the Home Assistant instance (e.g., 'http://192.168.2.4')
            token (str): Long-lived access token for authentication
        """
        # Use environment variables if not provided
        self.base_url = (base_url or os.environ.get("HASS_SERVER", "")).rstrip('/')
        self.token = token or os.environ.get("HASS_TOKEN", "")
        if not self.base_url or not self.token:
            raise ValueError("HASS_SERVER and HASS_TOKEN must be set as environment variables or passed explicitly.")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def set_effect(self, effect, entity_ids):
        """
        Set an effect on one or more light entities.

        Args:
            effect (str): The effect name to set (e.g., 'DDP')
            entity_ids (list of str): List of entity_id strings for the lights

        Returns:
            dict: The JSON response from Home Assistant, or None if request failed
        """
        url = f"{self.base_url}/api/services/light/turn_on"
        payload = {
            "effect": effect,
            "entity_id": entity_ids
        }
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error sending effect to Home Assistant: {e}")
            return None

# Example usage:
# Make sure to set the environment variables %HASS_SERVER% and %HASS_TOKEN% before running.
# import os
# os.environ["HASS_SERVER"] = "http://192.168.2.4"
# os.environ["HASS_TOKEN"] = "your_long_lived_access_token"
#
# controller = HASSLightController()
# result = controller.set_effect(
#     effect="DDP",
#     entity_ids=
# )
# print(result)
