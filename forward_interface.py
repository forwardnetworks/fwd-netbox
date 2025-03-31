"""Set of functions related to Forward API interactions"""
from common import ApiConnector, logging, requests


class ForwardAPI(ApiConnector):
    """Forward API implementation"""
    def __init__(self, config, ssl_verify=True):
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
                              timeout=config["timeout"])
        self.network_id = config["network_id"]
        self.locations_query_id = config["nqe"]["locations_query_id"]
        self.vendors_query_id = config["nqe"]["vendors_query_id"]
        self.device_types_query_id = config["nqe"]["device_types_query_id"]
        self.device_models_query_id = config["nqe"]["device_models_query_id"]
        self.devices_query_id = config["nqe"]["devices_query_id"]
        self.interfaces_query_id = config["nqe"]["interfaces_query_id"]
        self.virtual_device_contexts_query_id = config["nqe"]["virtual_device_contexts_query_id"]
        self.virtual_chassis_query_id = config["nqe"]["virtual_chassis_query_id"]
        self.nqe_limit = config.get("nqe_limit", 1000)

    def get_locations(self, network_id=None, query_id=None) -> dict:
        """Get Location list using Forward NQE API"""
        if network_id is None:
            network_id = self.network_id
        if query_id is None:
            query_id = self.locations_query_id
        return self.run_nqe_query(query_id, network_id)

    def get_vendors(self, network_id=None, query_id=None) -> dict:
        """Get Vendor list using Forward NQE API"""
        if network_id is None:
            network_id = self.network_id
        if query_id is None:
            query_id = self.vendors_query_id
        return self.run_nqe_query(query_id, network_id)

    def get_device_types(self, network_id=None, query_id=None) -> dict:
        """Get device types list using NQE API"""
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
        if network_id is None:
            network_id = self.network_id
        if query_id is None:
            query_id = self.devices_query_id
        return self.run_nqe_query(query_id, network_id)

    def get_interfaces(self, network_id=None, query_id=None) -> dict:
        """Get interfaces list using NQE API"""
        if network_id is None:
            network_id = self.network_id
        if query_id is None:
            query_id = self.interfaces_query_id
        return self.run_nqe_query(query_id, network_id)

    def get_virtual_device_contexts(self, network_id=None, query_id=None) -> dict:
        """Get virtual device context list using Forward NQE API"""
        if network_id is None:
            network_id = self.network_id
        if query_id is None:
            query_id = self.virtual_device_contexts_query_id
        return self.run_nqe_query(query_id, network_id)

    def get_virtual_chassis(self, network_id=None, query_id=None) -> dict:
        """Get virtual chassis list using Forward NQE API"""
        if network_id is None:
            network_id = self.network_id
        if query_id is None:
            query_id = self.virtual_chassis_query_id
        return self.run_nqe_query(query_id, network_id)

    def run_nqe_query(self, query_id, network_id=None) -> list:
        """Execute a paginated NQE query and return all results"""
        if network_id is None:
            network_id = self.network_id
        snapshot_id = self.get_latest_snapshot(network_id)["id"]
        logging.debug("Running Forward NQE Query...")

        offset = 0
        limit = 1000
        total_items = None
        all_items = []

        while total_items is None or offset < total_items:
            data = {
                "queryId": query_id,
                "queryOptions": {
                    "offset": offset,
                    "limit": limit
                }
            }

            response = self._post(f"/api/nqe?snapshotId={snapshot_id}", data)
            if response is None or "items" not in response:
                logging.warning(f"No results from NQE at offset {offset}")
                break

            if total_items is None:
                total_items = response.get("totalNumItems", 0)
                logging.debug(f"NQE reported totalNumItems={total_items}")

            all_items.extend(response["items"])
            offset += limit

        logging.info(f"Fetched {len(all_items)} items from NQE query {query_id}")
        return all_items

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
