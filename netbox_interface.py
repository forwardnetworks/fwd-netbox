"""Set of functions related to Netbox API interactions"""
from common import ApiConnector, logging


class NetboxAPI(ApiConnector):
    """API implementation for Netbox"""

    def __init__(self, config, ssl_verify=True, timeout=30):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "ForwardNetworks/1.0",
            "Authorization": config["authentication"]
        }
        ApiConnector.__init__(self,
                              config["host"],
                              config["authentication"],
                              http_headers=headers,
                              ssl_verify=ssl_verify,
                              timeout=timeout)
        self.device_role = config["device"]["role"]
        self.speeds_types = {  # Static mapping of port speeds
            "SPEED_100MB": "100base-tx",
            "SPEED_1GB": "1000base-t",
            "SPEED_10GB": "10gbase-t"
        }
        self.speed_to_int = {
            "SPEED_100MB": 100,
            "SPEED_1GB": 1000000,
            "SPEED_10GB": 10000000
        }

    def get_roles(self):
        """Get Roles from netbox"""
        logging.debug("Getting Roles From NetBox...")
        return self._get("/api/dcim/device-roles/")

    def get_sites(self):
        """Get Sites from Netbox using API"""
        logging.debug("Getting Sites From NetBox...")
        return self._get("/api/dcim/sites/")

    def get_device_types(self):
        """Get device types form Netbox using API"""
        logging.debug("Getting device types from NetBox...")
        return self._get("/api/dcim/device-types/")

    def get_devices(self) -> dict:
        """Get devices form Netbox using API"""
        logging.debug("Getting devices from NetBox...")
        response = self._get("/api/dcim/devices/")
        if response is not None:
            return response
        raise ValueError("Received empty response")

    def get_interfaces(self) -> dict:
        """Get Interfaces using API"""
        logging.debug("Getting interfaces from Netbox using API")
        response = self._get("/api/dcim/interfaces/")
        if response is not None:
            return response
        raise ValueError("Received empty response")

    def add_device(self, device):
        """Add devices to netbox"""
        logging.debug("Adding devices to NetBox...")
        self._post("/api/dcim/devices/", device)

    def patch_devices(self, devices: list):
        """Patch existing devices"""
        logging.debug("Patching devices in Netbox...")
        self._patch("/api/dcim/devices/", devices)

    def add_device_list(self, devices):
        """Add list of devices:
        This function gets a list of devices, it then
        iterates over the existing device list present
        in Netbox to find existing devices, using sets
        the it extract devices not present. For the
        devices present it adds the id of the device
        and patches the list as a whole. For the device
        list of non-existing devices it posts each device
        individually.

        Keyword arguments:
        devices -- List of devices to add into Netbox.
        """
        logging.debug("Adding a list of %d devices", len(devices))
        existing_devices = self.get_devices()["results"]
        update_devices = []
        create_devices = []
        for device in devices:
            for existing_device in existing_devices:
                if device["name"] == existing_device["name"]:
                    device["id"] = existing_device["id"]
                    update_devices.append(device)
        create_devices = [device for device in devices if "id" not in device.keys()]
        self.patch_devices(update_devices)
        for device in create_devices:
            self.add_device(device)

    def add_interface(self, interface):
        """Add devices to netbox"""
        logging.debug("Adding devices to NetBox...")
        self._post("/api/dcim/interfaces/", interface)

    def patch_interfaces(self, interfaces):
        """Add devices to netbox"""
        logging.debug("Adding devices to NetBox...")
        self._patch("/api/dcim/interfaces/", interfaces)

    def add_interface_list(self, interfaces):
        """Adds a list of interfaces, patches if already exists"""
        logging.debug("Adding a list of %d devices", len(interfaces))
        existing_interfaces = self.get_interfaces()["results"]
        update_interfaces = []
        create_interfaces = []
        print(interfaces)
        for interface in interfaces:
            for existing_interface in existing_interfaces:
                if interface["name"] == existing_interface["name"]:
                    interface["id"] = existing_interface["id"]
                    update_interfaces.append(interface)
        create_interfaces = [interface for interface in interfaces if "id" not in interface.keys()]
        self.patch_interfaces(update_interfaces)
        for interface in create_interfaces:
            self.add_interface(interface)

    def _get_site_map_helper(self) -> dict:
        """Helper method that returns a dictionary of Sites and the id"""
        results = self.get_sites()
        sites = {}
        if results is None:
            logging.warning("No sites where found.")
            return {}
        for result in results["results"]:
            sites[result["name"]] = result["id"]
        return sites

    def _get_device_map_helper(self) -> dict:
        """Helper method that returns a dictionary of Devices and the id"""
        results = self.get_device_types()
        device_types = {}
        if results is None:
            logging.warning("No devices where found.")
            return {}
        for result in results["results"]:
            device_types[result["model"]] = result["id"]
        return device_types

    def _get_interface_map_helper(self) -> dict:
        """Helper method that returns a dictionary of Devices and the id"""
        results = self.get_devices()
        devices = {}
        if results is None:
            logging.warning("No devices where found.")
            return {}
        for result in results["results"]:
            devices[result["name"]] = result["id"]
        return devices

    def adapt_forward_device_query(self, query):
        """Helper method to convert a device forward query into a Netbox Query"""
        sites = self._get_site_map_helper()
        devices = self._get_device_map_helper()
        for entry in query:
            entry["device_type"] = devices[entry["device_type"]]
            if entry["site"] is not None:
                entry["site"] = sites[entry["site"]]
            else:
                entry["site"] = sites["Default"]
            entry["role"] = self.device_role
        return query

    def adapt_forward_interface_query(self, query):
        """Helper method to convert an interface forward query into a Netbox Query"""
        devices = self._get_interface_map_helper()
        for entry in query:
            entry["device"] = devices[entry["device"]]
            entry["type"] = self.speeds_types[entry["type"]]
            entry["speed"] = self.speed_to_int[entry["speed"]]
        return query
