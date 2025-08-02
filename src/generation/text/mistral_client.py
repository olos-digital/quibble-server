import os
from typing import List
import requests

from src.utilities import logger

logger = logger.setup_logger("MistralClient logger")

class MistralClient:
	def __init__(self, api_key: str | None = None):
		"""
		Initialize the MistralClient with an API key.
		The API key can be provided directly or via the MISTRAL_API_KEY environment variable.
		
		Args:
			api_key (str | None): The Mistral API key. If None, it will look for MISTRAL_API_KEY in the environment.
		Raises:
			ValueError: If no API key is provided or found in the environment.
		"""
		self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
		if not self.api_key:
			logger.error("❌ MISTRAL_API_KEY not found!")
			raise ValueError("❌ MISTRAL_API_KEY not found!")

		self.api_url = os.getenv("MISTRAL_API_URL")
		self.headers = {
			"Authorization": f"Bearer {self.api_key}",
			"Content-Type": "application/json"
		}
		logger.debug("MistralClient initialized with provided API key.")

	def generate_text(self, prompt: str, model: str = "mistral-medium", max_tokens: int = 300) -> dict:
		"""
		Sends a request to the Mistral API to generate text based on a prompt.

		Args:
			prompt (str): The text prompt to send to the model.
			model (str): The Mistral model to use (default: mistral-medium).
			max_tokens (int): Maximum number of tokens to generate in the response.

		Returns:
			dict: The API response as a dictionary.

		Raises:
			requests.RequestException: If the request fails due to network issues.
			requests.HTTPError: If the API returns an unsuccessful status code.
		"""
		payload = {
			"model": model,
			"messages": [{"role": "user", "content": prompt}],
			"temperature": 0.7,
			"max_tokens": max_tokens
		}

		try:
			logger.info(f"Sending request to Mistral API with model '{model}' and prompt: {prompt[:50]}...")
			resp = requests.post(self.api_url, headers=self.headers, json=payload, timeout=30)
			resp.raise_for_status()

		except requests.Timeout:
			logger.error("Request to Mistral API timed out.")
			raise

		except requests.ConnectionError as ce:
			logger.error(f"Connection error occurred: {ce}")
			raise

		except requests.HTTPError as he:
			logger.error(f"HTTP error occurred: {he} | Response: {getattr(he.response, 'text', '')}")
			raise

		except requests.RequestException as re:
			logger.error(f"Request exception occurred: {re}")
			raise

		try:
			response_json = resp.json()

		except ValueError as ve:
			logger.error(f"Failed to parse JSON response: {ve}")
			raise

		logger.debug("Received successful response from Mistral API.")
		return response_json

	def generate_posts(self, prompt: str, n: int = 5) -> List[str]:
		"""
		Generate `n` separate post drafts from one prompt.

		Args:
			prompt (str): The prompt to use for generating posts.
			n (int): Number of drafts to generate.

		Returns:
			List[str]: List of generated post drafts.

		Raises:
			Exception: If any call to generate_text fails.
		"""
		drafts = []
		logger.info(f"Generating {n} post drafts for the given prompt.")
		
		for i in range(n):
			try:
				response = self.generate_text(prompt)
				drafts.append(response)
				logger.debug(f"Draft {i+1}/{n} generated successfully.")

			except Exception as e:
				logger.error(f"Failed to generate draft {i+1}: {e}")
				continue

		if not drafts:
			logger.warning("No drafts were generated successfully.")

		return drafts
