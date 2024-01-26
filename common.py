"""Set of common functions"""
import logging
import json
import requests

# setup logging logging configuration
logging.basicConfig(level=logging.INFO)  # Set the default logging level to INFO


def print_variables(config):
    """Debug function print all configuration variables"""
    logging.debug("netbox_url: %s", config["netbox"]["host"])
    logging.debug("netbox_auth_token: %s", config["netbox"]["authentication"])
    logging.debug("fwd_url: %s", config["forward"]["host"])
    logging.debug("fwd_snapshot_id: %s", config["forward"]["network_id"])
    logging.debug("fwd_basic_auth: %s", config["forward"]["authentication"])
    logging.debug("fwd_nqe_query_id: %s", config["forward"]["nqe"]["devices_query_id"])
    logging.debug("fwd_nqe_query_id: %s", config["forward"]["nqe"]["interfaces_query_id"])
    logging.debug("fwd_nqe_query_id: %s", config["netbox"]["host"])
    logging.debug("fwd_nqe_query_id: %s", config["netbox"]["authentication"])
    logging.debug("fwd_nqe_query_id: %s", config["netbox"]["device"]["role"])


class ApiConnector:
    """Generic class to handle api connections"""

    def __init__(self, host: str, authentication: str, http_headers, ssl_verify=True, timeout=30):
        """Constructor handling endpoint and authentication"""
        self.host = host
        self.authentication = authentication
        self.http_headers = http_headers
        self.ssl_verify = ssl_verify
        self.timeout = timeout

    def _request(self, method: str, path: str, headers, payload=None):
        """Generic HTTP method handler"""
        method = method.upper()
        url = f"{self.host}{path}"
        if headers is None:
            headers = self.http_headers
        logging.debug("Launching %s request to: %s", method.upper(), url)
        match method:
            case "GET":
                response = requests.get(url, headers=headers, timeout=self.timeout, verify=self.ssl_verify)
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
            logging.warning("Request failed status code: %d -> message: %s", response.status_code, response.text)
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
