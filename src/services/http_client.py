import requests
import time
from config import logger
import os
import concurrent.futures


class HttpClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def get(self, paths: list, is_json=True, max_retries=2, retry_delay=1):
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=os.cpu_count()
        ) as executor:
            futures = [
                executor.submit(self._get_single, path, max_retries, retry_delay)
                for path in paths
            ]
            results = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        return [response.json() if is_json else response.text for response in results]

    def generate(self, paths: list, max_retries=2, retry_delay=1):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self._get_single, path, max_retries, retry_delay)
                for path in paths
            ]
            for future in concurrent.futures.as_completed(futures):
                response = future.result()
                yield {"response": response.json(), "url": response.url}

    def _get_single(self, path, max_retries, retry_delay):
        retries = 0
        while retries < max_retries:
            try:
                response = requests.get(f"{self.base_url}{path}")
                logger.info(f"GET {response.url} - {response.status_code}")
                return response
            except requests.RequestException as e:
                retries += 1
                logger.warning(
                    f"Failed to get response for path: {path}. Retrying in {retry_delay} seconds"
                )
                time.sleep(retry_delay)

        logger.warning(f"Failed to get response for path: {path}")
        raise requests.RequestException(f"Failed to get response for path: {path}")
