"""Set of functions related to Forward API interactions"""
from common import ApiConnector, logging, requests


class ForwardAPI(ApiConnector):
    """Forward API implementation"""
    def __init__(self, config, ssl_verify=True, timeout=30):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": config["authentication"]
        }
        ApiConnector.__init__(self,
                              config["host"],
                              config["authentication"],
                              http_headers=headers,
                              ssl_verify=ssl_verify,
                              timeout=timeout)
        self.network_id = config["network_id"]
        self.locations_query_id = config["nqe"]["locations_query_id"]
        self.vendors_query_id = config["nqe"]["vendors_query_id"]
        self.device_types_query_id = config["nqe"]["device_types_query_id"]
        self.device_models_query_id = config["nqe"]["device_models_query_id"]
        self.devices_query_id = config["nqe"]["devices_query_id"]
        self.interfaces_query_id = config["nqe"]["interfaces_query_id"]

    def get_locations(self, network_id=None, query_id=None) -> dict:
        """Get Location list using Forward NQE API"""
        if network_id is None:
            network_id = self.network_id
        if query_id is None:
            query_id = self.locations_query_id
        return self.run_nqe_query(query_id, network_id)

    def get_vendors(self, network_id=None, query_id=None) -> dict:
        """Get Vendor list using Forward NQE API"""
        # Use network_id defined in the constructor
        if network_id is None:
            network_id = self.network_id
        if query_id is None:
            query_id = self.vendors_query_id
        return self.run_nqe_query(query_id, network_id)

    def get_device_types(self, network_id=None, query_id=None) -> dict:
        """Get device types list using NQE API"""
        # Use network_id defined in the constructor
        if network_id is None:
            network_id = self.network_id
        if query_id is None:
            query_id = self.device_types_query_id
        return self.run_nqe_query(query_id, network_id)

    def get_models(self, network_id=None, query_id=None) -> dict:
        """Get device models list using NQE API"""
        if network_id is None:
            network_id = self.network_id
        if query_id is None:
            query_id = self.device_models_query_id
        return self.run_nqe_query(query_id, network_id)

    def get_devices(self, network_id=None, query_id=None) -> dict:
        """Get device list using NQE API"""
        # Use network_id defined in the constructor
        if network_id is None:
            network_id = self.network_id
        if query_id is None:
            query_id = self.devices_query_id
        return self.run_nqe_query(query_id, network_id)

    def get_interfaces(self, network_id=None, query_id=None) -> dict:
        """Get device list using NQE API"""
        # Use network_id defined in the constructor
        if network_id is None:
            network_id = self.network_id
        if query_id is None:
            query_id = self.interfaces_query_id
        return self.run_nqe_query(query_id, network_id)

    def run_nqe_query(self, query_id, network_id=None) -> dict:
        """Execute query based on id"""
        # Use network_id defined in the constructor
        if network_id is None:
            network_id = self.network_id
        snapshot_id = self.get_latest_snapshot(network_id)["id"]
        logging.debug("Running Forward NQE Query...")
        data = {"queryId": query_id}
        nqe_result = self._post(f"/api/nqe?snapshotId={snapshot_id}", data)
        if nqe_result is not None:
            return nqe_result["items"]
        logging.debug(nqe_result)
        raise requests.RequestException("Invalid response")

    def get_latest_snapshot(self, network_id=None) -> dict:
        """Get latest snapshot id"""
        if network_id is None:
            network_id = self.network_id
        logging.debug("Running Forward latest snapshot query...")
        snapshot = self._get(f"/api/networks/{network_id}/snapshots/latestProcessed")
        if snapshot is not None:
            return snapshot
        logging.debug(snapshot)
        raise requests.RequestException("Invalid response")
