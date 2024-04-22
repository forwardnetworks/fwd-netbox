"""Set of common functions"""
import logging
import json
import requests

# setup logging logging configuration
logging.basicConfig(level=logging.INFO)  # Set the default logging level to INFO


def print_variables(config):
    """Debug function print all configuration variables"""
    logging.debug("======================== Configuration.yaml variables")
    logging.debug("Debug: {%s}", config["debug"])
    logging.debug("add_sites: %s", config["add_sites"])
    logging.debug("add_manufacturers: %s", config["add_manufacturers"])
    logging.debug("add_device_roles: %s", config["add_device_roles"])
    logging.debug("add_device_types: %s", config["add_device_types"])
    logging.debug("add_devices: %s", config["add_devices"])
    logging.debug("add_interfaces: %s", config["add_interfaces"])
    logging.debug("Forward")
    logging.debug("Host: %s", config["forward"]["host"])
    logging.debug("authentication: %s", config["forward"]["authentication"])
    logging.debug("network_id: %s", config["forward"]["network_id"])
    logging.debug("locations_query_id: %s", config["forward"]["nqe"]["locations_query_id"])
    logging.debug("vendors_query_id: %s", config["forward"]["nqe"]["vendors_query_id"])
    logging.debug("device_roles_query_id: %s", config["forward"]["nqe"]["device_roles_query_id"])
    logging.debug("device_types_query_id: %s", config["forward"]["nqe"]["device_types_query_id"])
    logging.debug("devices_query_id: %s", config["forward"]["nqe"]["devices_query_id"])
    logging.debug("interfaces_query_id: %s", config["forward"]["nqe"]["interfaces_query_id"])
    logging.debug("NetBox:")
    logging.debug("host: %s", config["netbox"]["host"])
    logging.debug("authentication: %s", config["netbox"]["authentication"])
    logging.debug("======================== Configuration.yaml variables end")


def create_slug(name):
    """Function to crete a slug from a name by replacing blank spaces with dashes
    and making it all lowercases
    """
    return name.lower().replace(' ', '-')


class ApiConnector:
    """Generic class to handle api connections"""

    def __init__(self, host: str, authentication: str, http_headers, ssl_verify=True, timeout=30):
        """Constructor handling endpoint and authentication"""
        self.host = host
        self.authentication = authentication
        self.http_headers = http_headers
        self.timeout = timeout
        self.ssl_verify = ssl_verify

    def _request(self, method: str, path: str, headers, payload=None):
        """Generic HTTP method handler"""
        method = method.upper()
        url = f"{self.host}{path}"
        if headers is None:
            headers = self.http_headers
        logging.debug("Launching %s request to: %s", method.upper(), url)
        match method:
            case "GET":
                response = requests.get(
                    url, headers=headers, timeout=self.timeout, verify=self.ssl_verify
                )
            case "POST":
                response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=self.timeout,
                                         verify=self.ssl_verify)
            case "PATCH":
                response = requests.patch(url, headers=headers, data=json.dumps(payload), timeout=self.timeout,
                                          verify=self.ssl_verify)
            case "PUT":
                response = requests.put(url, headers=headers, data=json.dumps(payload), timeout=self.timeout,
                                        verify=self.ssl_verify)
            case _:
                logging.warning("Method not implemented %s", method.upper())
                raise requests.RequestException("Request Method not implemented")

        if response.status_code >= 400:
            logging.warning(
                "Request failed status code: %d -> message: %s", response.status_code,
                response.text
            )
            return None
        elif "Content-Type" in response.headers and response.headers["Content-Type"] == "application/json":
            return response.json()
        elif "Content-Type" in response.headers and response.headers["Content-Type"] != "application/json":
            logging.warning("Response Content-Type is not matching an expected \
                             API response: %s", response.headers["Content-Type"])
            raise requests.RequestException("Unexpected Content type")
        return None

    def _get(self, path: str, headers=None):
        """Generic GET request handler"""
        return self._request("GET", path, headers)

    def _post(self, path: str, payload, headers=None):
        """Generic POST request handler"""
        return self._request("POST", path, headers, payload)

    def _patch(self, path: str, payload, headers=None):
        """Generic PATCH request handler"""
        return self._request("PATCH", path, headers, payload)

    def _put(self, path: str, payload, headers=None):
        """Generic PUT request handler"""
        return self._request("PUT", path, headers, payload)
