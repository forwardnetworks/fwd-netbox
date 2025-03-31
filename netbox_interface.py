"""Set of functions related to Netbox API interactions"""
from math import ceil
from common import ApiConnector, logging, create_slug


class NetboxAPI(ApiConnector):
    """API implementation for Netbox"""

    def __init__(self, config, ssl_verify=True):
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
                              timeout=config["timeout"])
        self.speeds_types = {  # Static mapping of port speeds
            10:     "100base-tx",
            100:    "100base-tx",
            1000:   "1000base-t",
            2500:   "2.5gbase-t",
            5000:   "5gbase-t",
            10000:  "10gbase-t",
            25000:  "25gbase-x-sfp28",
            40000:  "40gbase-x-qsfpp",
            50000:  "50gbase-x-sfp28",
            100000: "100gbase-x-qsfp28",
            None: "other"
        }
        self.request_limit = config.get("post_limit", 50)  # Defaults to 50
        self.post_limit = config.get("post_limit", 100)
        self.allow_deletes = config.get("allow_deletes", False)# Chunk size for bulk POST/PATCH operations

    def get_manufacturers(self):
        """Get Manufacturers from netbox"""
        logging.debug("Getting Manufacturers From NetBox...")
        return self._get_paginated("/api/dcim/manufacturers/")

    def get_roles(self):
        """Get Roles from netbox"""
        logging.debug("Getting Roles From NetBox...")
        return self._get_paginated("/api/dcim/device-roles/")

    def get_sites(self):
        """Get Sites from Netbox using API"""
        logging.debug("Getting Sites From NetBox...")
        return self._get_paginated("/api/dcim/sites/")

    def get_device_types(self):
        """Get Device Types form Netbox using API"""
        logging.debug("Getting Device Types from NetBox...")
        return self._get_paginated("/api/dcim/device-types/")

    def get_devices(self) -> dict:
        """Get Devices form Netbox using API"""
        logging.debug("Getting Devices from NetBox...")
        response = self._get_paginated("/api/dcim/devices/")
        if response is not None:
            return response
        raise ValueError("Received empty response")

    def get_interfaces(self) -> dict:
        """Get Interfaces using API"""
        logging.debug("Getting Interfaces from Netbox using API")
        response = self._get_paginated("/api/dcim/interfaces/")
        if response is not None:
            return response
        raise ValueError("Received empty response")

    def get_virtual_device_contexts(self) -> dict:
        """Get Virtual Device Contexts from NetBox using API"""
        logging.debug("Getting Virtual Device Contexts from NetBox...")
        response = self._get_paginated("/api/dcim/virtual-device-contexts/")
        if response is not None:
            return response
        raise ValueError("Received empty response")

    def get_virtual_chassis(self) -> dict:
        """Get Virtual Chassis from NetBox using API"""
        logging.debug("Getting Virtual Chassis from NetBox...")
        response = self._get_paginated("/api/dcim/virtual-chassis/")
        if response is not None:
            return response
        raise ValueError("Received empty response")

    def add_site(self, site):
        """Add a Site to netbox"""
        logging.debug(f"Adding {site} site to NetBox...")
        self._post("/api/dcim/sites/", site)

    def patch_sites(self, sites: list):
        """Patch existing Sites in netbox"""
        logging.debug("Patching Sites in Netbox...")
        self._patch("/api/dcim/sites/", sites)

    def add_site_list(self, fwd_locations):
        """Add list of sites to netbox:
        This function gets a list of forward locations, it then
        iterates over the existing site list present
        in Netbox to find existing sites, using sets
        then it extract sites not present. For the
        devices present it adds the id of the site
        and patches the list as a whole. For the site
        list of non-existing sites it posts each site
        individually.

        Keyword arguments:
        fwd_locations -- List of devices to add into Netbox.
        """
        logging.debug(f"======> Adding a list of {len(fwd_locations)} sites")
        site_res = self.get_sites()
        if site_res is not None:
            existing_sites = site_res["results"]  # Sites already in NetBox
        update_sites = []    # List of sites to be updated in NetBox
        create_sites = []    # List of sites to be added in NetBox
        add_unknown_site = True

        for site in fwd_locations:
            for existing_site in existing_sites:
                if site["name"] == existing_site["name"].lower():
                    site["id"] = existing_site["id"]
                    site["name"] = existing_site["name"]
                    update_sites.append(site)

                if existing_site["name"].lower() == "unknown":
                    add_unknown_site = False

        create_sites = [site for site in fwd_locations if "id" not in site.keys()]

        # If a device in Forward is not assigned to any location, its location is set to "unknown" in the NQE query
        # The following two lines create an unknown_site and append it to the list of sites to be created
        if add_unknown_site:
            logging.debug("Appending Unknown site to the list of sites to be created")
            unknown_site = {
                'name': 'Unknown',
                'slug': 'unknown',
                'status': 'active',
                'physical_address': 'unknown',
                'comments': 'Site Added by Forward Enterprise'
            }
            create_sites.append(unknown_site)
        else:
            logging.debug("Unknown site already present in NetBox")

        # convert the first character of each word to uppercase (or title case) and
        # the remaining characters of the word to lowercase.
        # Comment the 2 lines below if you prefer to keep original name
        for site in create_sites:
            site["name"] = site["name"].title()

        # Update existing devices
        self.patch_sites(update_sites)

        # Create new Devices
        for site in create_sites:
            self.add_site(site)

        return create_sites, update_sites

    def add_device_type(self, device_type):
        """Add a device type to netbox"""
        logging.debug("Adding %s device type to NetBox...", device_type)
        self._post("/api/dcim/device-types/", device_type)

    def add_device_type_list(self, fwd_models):
        """Add list of device types to netbox:
        This function gets a list of forward device models, it then
        iterates over the existing device types list present
        in Netbox to find existing types, using sets
        then it extract types not present. For the type
        list of non-existing types it posts each type
        individually.

        Keyword arguments:
        fwd_models -- List of device models to add into Netbox device types.
        """
        logging.debug("++++++++++++++ add_device_type_list ++++++++++++++")
        logging.debug("Adding a list of %d device types", len(fwd_models))
        device_types = self.get_device_types()
        if device_types is not None:
            existing_device_types = device_types["results"]  # Device Types already in NetBox
        create_device_types = []    # List of device types to be added in NetBox
        for device_type in fwd_models:
            for existing_device_type in existing_device_types:
                if device_type["model"] == existing_device_type["model"]:
                    device_type["id"] = existing_device_type["id"]
        create_device_types = [device_type for device_type in fwd_models if "id" not in device_type.keys()]

        # Create new Device Types
        for device_type in create_device_types:
            self.add_device_type(device_type)
        return create_device_types

    def add_manufacturer(self, manufacturer):
        """Add a Manufacturer to netbox"""
        logging.debug(f"Adding {manufacturer} Manufacturer to NetBox...")
        self._post("/api/dcim/manufacturers/", manufacturer)

    def add_manufacturer_list(self, fwd_vendors):
        """Add list of manufacturers to netbox:
        This function gets a list of forward vendors, it then
        iterates over the existing manufacturer list present
        in Netbox to find existing manufacturers, using sets
        then it extract vendors not present. For the vendor
        list of non-existing vendors it posts each vendor
        individually.

        Keyword arguments:
        fwd_vendors -- List of vendor to add into Netbox manufacturers.
        """
        logging.debug(f"Adding a list of {len(fwd_vendors)} manufacturers")
        manufacturers = self.get_manufacturers()
        if manufacturers is not None:
            existing_manufacturers = manufacturers[
                "results"
            ]  # Manufacturers already in NetBox
        create_manufacturers = []    # List of devices to be added in NetBox
        for manufacturer in fwd_vendors:
            for existing_manufacturer in existing_manufacturers:
                if manufacturer["name"] == existing_manufacturer["name"]:
                    manufacturer["id"] = existing_manufacturer["id"]
        create_manufacturers = [manufacturer for manufacturer in fwd_vendors if "id" not in manufacturer.keys()]

        # Create new Manufacturers
        for manufacturer in create_manufacturers:
            self.add_manufacturer(manufacturer)
        return create_manufacturers

    def add_role(self, role):
        """Add a Device Role to netbox"""
        logging.debug(f"Adding {role} Device Role to NetBox...")
        self._post("/api/dcim/device-roles/", role)

    def add_role_list(self, fwd_device_types):
        """Add list of device roles to netbox:
        This function gets a list of forward device type, it then
        iterates over the existing roles list present
        in Netbox to find existing roles, using sets
        then it extract roles not present. For the roles
        list of non-existing roles it posts each role
        individually.

        Keyword arguments:
        fwd_device_types -- List of device types to add into Netbox roles.
        """
        logging.debug(f"Adding a list of {len(fwd_device_types)} device roles")
        roles = self.get_roles()
        if roles is not None:
            existing_roles = roles["results"]  # Roles already in NetBox
        create_roles = []    # List of roles to be added in NetBox
        for role in fwd_device_types:
            for existing_role in existing_roles:
                if role["name"] == existing_role["name"]:
                    role["id"] = existing_role["id"]
        create_roles = [role for role in fwd_device_types if "id" not in role.keys()]

        # Create new roles
        for role in create_roles:
            self.add_role(role)
        return create_roles

    def add_device(self, device):
        """Add a Device to netbox"""
        logging.debug(f"Adding Device {device} to NetBox...")
        self._post("/api/dcim/devices/", device)

    def patch_devices(self, devices: list):
        """Patch existing devices"""
        logging.debug("Patching devices in Netbox...")
        self._patch("/api/dcim/devices/", devices)

    def add_device_list(self, fwd_devices):
        """Add list of devices:
        This function gets a list of devices, it then
        iterates over the existing device list present
        in Netbox to find existing devices, using sets
        then it extract devices not present. For the
        devices present it adds the id of the device
        and patches the list as a whole. For the device
        list of non-existing devices it posts each device
        individually.

        Keyword arguments:
        fwd_devices -- List of devices to add into Netbox.
        """
        logging.debug(f"Adding a list of {len(fwd_devices)} devices")
        existing_devices = self.get_devices()["results"]  # Devices already in NetBox
        update_devices = []    # List of devices to be updated in NetBox
        create_devices = []    # List of devices to be added in NetBox
        for device in fwd_devices:
            for existing_device in existing_devices:
                if device["name"] == existing_device["name"]:
                    device["id"] = existing_device["id"]
                    update_devices.append(device)
        create_devices = [device for device in fwd_devices if "id" not in device.keys()]

        # Update existing devices
        self.patch_devices(update_devices)

        # Create new Devices
        for device in create_devices:
            self.add_device(device)

        return create_devices, update_devices

    def add_interface(self, interface):
        """Add an Interface to netbox"""
        logging.debug(f"Adding {interface} Interface to NetBox...")
        self._post("/api/dcim/interfaces/", interface)

    def patch_interfaces(self, interfaces):
        """PATCH interfaces in chunks using NetBox bulk PATCH API"""
        logging.debug(f"Bulk PATCHing {len(interfaces)} interfaces")
        self._bulkpatch("/api/dcim/interfaces/", interfaces)

    def add_interface_list(self, interfaces):
        """Adds a list of interfaces using chunked POST and PATCH"""
        logging.debug(f"Adding a list of {len(interfaces)} interfaces")
        existing_interfaces = self.get_interfaces()["results"]
        update_interfaces = []
        create_interfaces = []

        for interface in interfaces:
            for existing in existing_interfaces:
                if (
                    interface["name"] == existing["name"]
                    and interface["device"] == existing["device"]["id"]
                ):
                    interface["id"] = existing["id"]
                    update_interfaces.append(interface)
                    break

        create_interfaces = [i for i in interfaces if "id" not in i]

        if update_interfaces:
            logging.info(f"Bulk PATCHing {len(update_interfaces)} interfaces...")
            self.patch_interfaces(update_interfaces)

        if create_interfaces:
            logging.info(f"Bulk POSTing {len(create_interfaces)} interfaces...")
            self._bulkpost("/api/dcim/interfaces/", create_interfaces)

        return create_interfaces, update_interfaces

    def add_virtual_device_context(self, vdc):
        """Add a Virtual Device Context to NetBox"""
        logging.debug(f"Adding Virtual Device Context {vdc} to NetBox...")
        self._post("/api/dcim/virtual-device-contexts/", vdc)

    def patch_virtual_device_contexts(self, vdcs: list):
            logging.debug("Patching Virtual Device Contexts in NetBox...")
            self._patch("/api/dcim/virtual-device-contexts/", vdcs)

    def add_virtual_device_context_list(self, vdcs):
        """Adds a list of virtual device contexts, patches if already exists

        Keyword arguments:
        vdcs -- List of virtual device contexts to add into NetBox.
        """
        logging.debug(f"Adding a list of {len(vdcs)} virtual device contexts")
        existing_vdcs = self.get_virtual_device_contexts()["results"]
        update_vdcs = []
        create_vdcs = []

        for vdc in vdcs:
            for existing_vdc in existing_vdcs:
                if (
                    vdc["name"] == existing_vdc["name"]
                    and vdc["device"] == existing_vdc["device"]["id"]
                ):
                    vdc["id"] = existing_vdc["id"]
                    update_vdcs.append(vdc)
                    break  # Avoid duplicate updates

        create_vdcs = [vdc for vdc in vdcs if "id" not in vdc.keys()]

        self.patch_virtual_device_contexts(update_vdcs)

        for vdc in create_vdcs:
            self.add_virtual_device_context(vdc)

        return create_vdcs, update_vdcs

    def add_virtual_chassis(self, vc):
        logging.debug(f"Adding Virtual Chassis {vc} to NetBox...")
        self._post("/api/dcim/virtual-chassis/", vc)

    def patch_virtual_chassis(self, vcs: list):
        logging.debug("Patching Virtual Chassis in NetBox...")
        self._patch("/api/dcim/virtual-chassis/", vcs)

    def add_virtual_chassis_list(self, chassis_list):
        logging.debug(f"Adding a list of {len(chassis_list)} virtual chassis")
        existing_chassis = self.get_virtual_chassis()["results"]
        update_chassis = []
        create_chassis = []

        for chassis in chassis_list:
            for existing in existing_chassis:
                if chassis["name"] == existing["name"]:
                    chassis["id"] = existing["id"]
                    update_chassis.append(chassis)
                    break

        create_chassis = [ch for ch in chassis_list if "id" not in ch]

        self.patch_virtual_chassis(update_chassis)

        for chassis in create_chassis:
            self.add_virtual_chassis(chassis)

        return create_chassis, update_chassis

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

    def _get_manufacturer_map_helper(self) -> dict:
        """Helper method that returns a dictionary of Manufacturers and the id"""
        results = self.get_manufacturers()
        manufacturers = {}
        if results is None:
            logging.warning("No manufacturers where found in NetBox.")
            return {}
        for result in results["results"]:
            # Convert the names of NetBox roles to lowercase to enable case-insensitive lookup
            manufacturers[result["name"].lower()] = result["id"]
        logging.debug(f"NetBox Manufacturers List: {manufacturers}")
        return manufacturers

    def _get_role_map_helper(self) -> dict:
        """Helper method that returns a dictionary of Roles and the id"""
        results = self.get_roles()
        roles = {}
        if results is None:
            logging.warning("No roles where found.")
            return {}
        for result in results["results"]:
            # Convert the names of NetBox roles to lowercase to enable case-insensitive lookup
            roles[result["name"].lower()] = result["id"]
        return roles

    def _get_device_type_map_helper(self) -> dict:
        """Helper method that returns a dictionary of device types and the id"""
        results = self.get_device_types()
        device_types = {}
        if results is None:
            logging.warning("No device types where found in NetBox.")
            return {}
        for result in results["results"]:
            # Convert the names of NetBox roles to lowercase to enable case-insensitive lookup
            device_types[result["display"].lower()] = result["id"]
        logging.debug(f"====== NetBox Device Types List: {device_types}")
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

    def adapt_forward_vendor_query(self, query):
        """Helper method to convert a vendor forward query into a Netbox Manufacturer Query"""
        for entry in query:
            entry["name"] = entry["name"].title()
            entry["slug"] = create_slug(entry["slug"])
        return query

    def adapt_forward_model_query(self, query):
        """Helper method to convert a device models forward query into a Netbox device types Query"""
        manufacturers = self._get_manufacturer_map_helper()
        logging.debug(f"NetBox Manufacturers: {manufacturers}")
        for entry in query:
            # slug transformation
            if entry["slug"] is None:
                entry["slug"] = "unknown"
            else:
                entry["slug"] = create_slug(entry["slug"])

            # part_number transformation
            if entry["part_number"] is None:
                entry["part_number"] = "unknown"

            # model transformation
            if entry["model"] is None:
                entry["model"] = "unknown"

            # Manufacturer transformation
            if entry["manufacturer"].lower() in manufacturers:
                entry["manufacturer"] = manufacturers[entry["manufacturer"].lower()]
            else:
                entry["manufacturer"] = manufacturers["Unknown"]

        return query

    def adapt_forward_device_type_query(self, query):
        """Helper method to convert a Forward Device Types query into a Netbox Roles Query"""
        for entry in query:
            entry["name"] = entry["name"].title()
            entry["slug"] = create_slug(entry["slug"])
        return query

    def adapt_forward_device_query(self, query):
        """Helper method to convert a device forward query into a Netbox Query"""
        logging.debug(f"====> adapt_forward_device_query {query}")

        # Convert the names of Forward and NetBox to lowercase to enable case-insensitive lookup
        sites = self._get_site_map_helper()
        sites = {key.lower(): value for key, value in sites.items()}
        logging.debug(f"==> NetBox sites {sites}")

        devices = self._get_device_type_map_helper()
        logging.debug(f"==> NetBox devices types {devices}")

        roles = self._get_role_map_helper()
        logging.debug(f"==> NetBox roles {roles}")

        for entry in query:
            logging.debug(f"==> Device entry {entry}")

            # Device type transformation
            if entry["device_type"] is None:
                entry["device_type"] = "unknown"
            else:
                entry["device_type"] = devices[entry["device_type"].lower()]

                # Site transformation
            entry["site"] = entry["site"].lower()
            if entry["site"] in sites.keys():
                entry["site"] = sites[entry["site"]]
            else:
                logging.info("Site %s not in NetBox", entry["site"])

            # Role transformation
            entry["role"] = entry["role"].lower()
            if entry["role"] in roles:
                entry["role"] = roles[entry["role"]]
            else:
                logging.info("Role %s unknown", entry["role"])

        return query

    def adapt_forward_interface_query(self, query):
        """Helper method to convert an interface forward query into a Netbox Query"""
        devices = self._get_interface_map_helper()
        for entry in query:
            entry["device"] = devices[entry["device"]]
            entry["type"] = self.speeds_types[entry["type"]]
            if entry["speed"] is not None:
                entry["speed"] *= 1000
            else:
                entry["speed"] = 0

        return query

    def _get_paginated(self, original_path: str):
        path = f"{original_path}?limit={self.request_limit}"
        response = self._get(path)
        if response is not None:
            count = response["count"]
            if count > self.request_limit:
                for i in range(1, ceil(count/self.request_limit)):
                    new_path = f"{path}&offset={(self.request_limit*i)}"
                    offset_response = self._get(new_path)
                    if offset_response is not None:
                        response["results"] = response["results"] + offset_response["results"]
        return response
