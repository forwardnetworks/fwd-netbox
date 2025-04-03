import logging
import json
import os
import requests
from datetime import datetime

# === Logging Setup ===

# Timestamp for this run
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Directory for logs
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# Dictionary to store loggers
loggers = {}

# Initialize the root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

# Console handler (INFO and above)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('[%(levelname)s] %(message)s')
console_handler.setFormatter(console_formatter)
root_logger.addHandler(console_handler)

# Dynamically create named loggers based on config keys
def setup_loggers(config):
    """Create per-feature log files based on config flags like add_devices, add_interfaces, etc."""
    feature_keys = [k for k in config.keys() if k.startswith("add_") and config[k]]

    for key in feature_keys:
        name = key.replace("add_", "")
        log_file = os.path.join(log_dir, f"{name}_{timestamp}.log")

        feature_logger = logging.getLogger(name)
        file_handler = logging.FileHandler(log_file, mode='w')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s:%(name)s:%(message)s'))

        feature_logger.addHandler(file_handler)
        feature_logger.setLevel(logging.DEBUG)

        loggers[name] = feature_logger

    # Always create a general fallback logger
    general_log_file = os.path.join(log_dir, f"general_{timestamp}.log")
    general_logger = logging.getLogger("general")
    file_handler = logging.FileHandler(general_log_file, mode='w')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s:%(name)s:%(message)s'))
    general_logger.addHandler(file_handler)
    general_logger.setLevel(logging.DEBUG)
    loggers["general"] = general_logger


# === Utility Functions ===

def print_variables(config):
    """Debug function to print all configuration variables"""
    logging.debug("======================== Configuration.yaml variables")
    for key, value in config.items():
        if isinstance(value, dict):
            logging.debug(f"{key}:")
            for subkey, subvalue in value.items():
                logging.debug(f"  {subkey}: {subvalue}")
        else:
            logging.debug(f"{key}: {value}")
    logging.debug("======================== Configuration.yaml variables end")


def create_slug(name):
    """Convert a name into a NetBox slug (lowercase, hyphenated)"""
    return name.lower().replace(' ', '-')


# === API Connector ===

class ApiConnector:
    """Generic class to handle API connections"""

    def __init__(self, host: str, authentication: str, http_headers, ssl_verify=True, timeout=30):
        self.host = host
        self.authentication = authentication
        self.http_headers = http_headers
        self.timeout = timeout
        self.ssl_verify = ssl_verify

    def _request(self, method: str, path: str, headers=None, payload=None):
        """Generic HTTP method handler"""
        method = method.upper()
        url = f"{self.host}{path}"
        if headers is None:
            headers = self.http_headers

        logging.debug("Launching %s request to: %s", method, url)

        try:
            match method:
                case "GET":
                    response = requests.get(url, headers=headers, timeout=self.timeout, verify=self.ssl_verify)
                case "POST":
                    response = requests.post(url, headers=headers, data=json.dumps(payload),
                                             timeout=self.timeout, verify=self.ssl_verify)
                case "PATCH":
                    response = requests.patch(url, headers=headers, data=json.dumps(payload),
                                              timeout=self.timeout, verify=self.ssl_verify)
                case "PUT":
                    response = requests.put(url, headers=headers, data=json.dumps(payload),
                                            timeout=self.timeout, verify=self.ssl_verify)
                case "DELETE":
                    response = requests.delete(url, headers=headers, data=json.dumps(payload),
                                               timeout=self.timeout, verify=self.ssl_verify)
                case _:
                    raise ValueError(f"Unsupported HTTP method: {method}")

            if response.status_code >= 400:
                logging.warning("Request failed [%s %s] %d: %s",
                                method, path, response.status_code, response.text)
                return None

            content_type = response.headers.get("Content-Type", "")
            if "application/json" in content_type:
                return response.json()
            else:
                logging.warning("Unexpected Content-Type in response: %s", content_type)
                return None

        except requests.RequestException as e:
            logging.error("Request failed with exception: %s", str(e))
            return None

    def _get(self, path: str, headers=None):
        return self._request("GET", path, headers)

    def _post(self, path: str, payload, headers=None):
        return self._request("POST", path, headers, payload)

    def _patch(self, path: str, payload, headers=None):
        return self._request("PATCH", path, headers, payload)

    def _put(self, path: str, payload, headers=None):
        return self._request("PUT", path, headers, payload)

    def _bulkpost(self, path: str, payload_list: list):
        for i in range(0, len(payload_list), self.post_limit):
            chunk = payload_list[i:i + self.post_limit]
            logging.debug(f"POSTing chunk of {len(chunk)} items to {path}")
            self._request("POST", path, self.http_headers, payload=chunk)

    def _bulkpatch(self, path: str, payload_list: list):
        for i in range(0, len(payload_list), self.post_limit):
            chunk = payload_list[i:i + self.post_limit]
            logging.debug(f"PATCHing chunk of {len(chunk)} items to {path}")
            self._request("PATCH", path, self.http_headers, payload=chunk)

    def _bulkdelete(self, path: str, payload_list: list):
        for i in range(0, len(payload_list), self.post_limit):
            chunk = payload_list[i:i + self.post_limit]
            logging.debug(f"DELETEing chunk of {len(chunk)} items from {path}")
            self._request("DELETE", path, self.http_headers, payload=chunk)
