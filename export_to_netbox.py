#!/usr/bin/env python3
"""Demo script for integrating Forward Enterprise with Netbox."""
from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader
from common import logging, print_variables
from netbox_interface import NetboxAPI
from forward_interface import ForwardAPI


CONFIG_FILE = "configuration.yaml"


def main():
    """Main function"""
    # Import variables from file
    with open(CONFIG_FILE, "r", encoding="UTF-8") as f:
        config = load(f, Loader=Loader)

    if config["debug"]:
        logging.getLogger().setLevel(logging.DEBUG)  # Set the logging level to DEBUG if the debug flag is True
        print_variables(config)
    else:
        logging.getLogger().setLevel(logging.INFO)  # Otherwise, set it to INFO

    forward = ForwardAPI(config["forward"])
    netbox = NetboxAPI(config["netbox"])

    if config["add_sites"]:
        logging.info("========> Updating NetBox Sites...")
        # Forward Locations are mapped to NetBox Sites
        forward_locations = forward.get_locations()
        logging.debug(forward_locations)
        create_sites_list, update_sites_list = netbox.add_site_list(forward_locations)

        if len(create_sites_list) > 0:
            logging.info(f"{len(create_sites_list)} site[s] added to NetBox")
            for site in create_sites_list:
                logging.info(site["name"])
        if len(update_sites_list) > 0:
            logging.info(f"{len(update_sites_list)}  NetBox site[s] updated")
            for site in update_sites_list:
                logging.info(site["name"])
    else:
        logging.info("========> Skipping NetBox Sites Update...")

    if config["add_manufacturers"]:
        logging.info("========> Updating NetBox Manufacturers...")
        fwd_vendors = forward.get_vendors()
        logging.debug(f"Forward Vendors {fwd_vendors}")
        fwd_vendors_adapted = netbox.adapt_forward_vendor_query(fwd_vendors)
        logging.debug(f"NetBox devices {fwd_vendors_adapted}")
        create_manufacturers_list = netbox.add_manufacturer_list(fwd_vendors_adapted)

        if len(create_manufacturers_list):
            logging.info(f"========> {len(create_manufacturers_list)} manufacturer[s] added to NetBox")
            for manufacturer in create_manufacturers_list:
                logging.info(manufacturer["name"])
        else:
            logging.info("========> NetBox Manufacturers is up-to-date")
    else:
        logging.info("========> Skipping NetBox Manufacturers Update...")

    if config["add_device_roles"]:
        logging.info("========> Updating NetBox Device Roles...")
        fwd_device_types = forward.get_device_types()
        logging.debug(f"Forward Device Types {fwd_device_types}")
        fwd_device_types_adapted = netbox.adapt_forward_device_type_query(fwd_device_types)
        logging.debug(f"NetBox devices {fwd_device_types_adapted}")
        create_roles_list = netbox.add_role_list(fwd_device_types_adapted)

        if len(create_roles_list):
            logging.info(f"========> {len(create_roles_list)} device roles[s] added to NetBox")
            for role in create_roles_list:
                logging.info(role["name"])
        else:
            logging.info("========> NetBox Device Roles is up-to-date")
    else:
        logging.info("========> Skipping NetBox Device Roles Update...")

    if config["add_device_types"]:
        logging.info("========> Updating NetBox Device Types...")
        fwd_models = forward.get_models()
        logging.debug(f"Forward Device Models {fwd_models}")
        fwd_models_adapted = netbox.adapt_forward_model_query(fwd_models)
        logging.debug(f"NetBox devices types {fwd_models_adapted}")
        create_device_types_list = netbox.add_device_type_list(fwd_models_adapted)

        if len(create_device_types_list):
            logging.info(f"========> {len(create_device_types_list)} device types[s] added to NetBox")
            for device_type in create_device_types_list:
                logging.info(device_type["model"])
        else:
            logging.info("========> NetBox Device Types is up-to-date")
    else:
        logging.info("========> Skipping NetBox Device Types Update...")

    if config["add_devices"]:
        logging.info("========> Updating NetBox Devices...")
        fwd_devices = forward.get_devices()
        logging.debug(f"Forward Devices {fwd_devices}")
        fwd_devices_adapted = netbox.adapt_forward_device_query(fwd_devices)
        logging.debug(f"NetBox devices {fwd_devices_adapted}")
        create_devices_list, update_devices_list = netbox.add_device_list(fwd_devices_adapted)

        if len(create_devices_list):
            logging.info(f"========> {len(create_devices_list)} device[s] added to NetBox")
            for device in create_devices_list:
                logging.info(device["name"])
        if len(update_devices_list) > 0:
            logging.info(f"========> {len(update_devices_list)} NetBox device[s] updated")
            for device in update_devices_list:
                logging.info(device["name"])
    else:
        logging.info("========> Skipping NetBox Device Update...")

    if config["add_interfaces"]:
        logging.info("========> Updating NetBox Interfaces...")
        fwd_interfaces = forward.get_interfaces()
        logging.debug(f"Forward Devices {fwd_interfaces}")
        fwd_interfaces_adapted = netbox.adapt_forward_interface_query(fwd_interfaces)
        logging.debug(f"NetBox devices {fwd_interfaces_adapted}")
        create_interfaces_list, update_interfaces_list = netbox.add_interface_list(fwd_interfaces_adapted)

        if len(create_interfaces_list) > 0:
            logging.info(f"========> {len(create_interfaces_list)} interface[s] added to NetBox")
        if len(update_interfaces_list) > 0:
            logging.info(f"========> {len(update_interfaces_list)} NetBox interface[s] updated")
    else:
        logging.info("========> Skipping NetBox Interface Update...")

    if config.get("add_virtual_device_contexts", False):
        logging.info("========> Updating NetBox Virtual Device Contexts...")
        fwd_vdcs = forward.get_virtual_device_contexts()
        logging.debug(f"Forward Virtual Device Contexts {fwd_vdcs}")
        create_vdc_list, update_vdc_list = netbox.add_virtual_device_context_list(fwd_vdcs)

        if len(create_vdc_list) > 0:
            logging.info(f"========> {len(create_vdc_list)} virtual device context[s] added to NetBox")
        if len(update_vdc_list) > 0:
            logging.info(f"========> {len(update_vdc_list)} NetBox virtual device context[s] updated")
    else:
        logging.info("========> Skipping NetBox Virtual Device Contexts Update...")

    if config.get("add_virtual_chassis", False):
        logging.info("========> Updating NetBox Virtual Chassis...")
        fwd_vcs = forward.get_virtual_chassis()
        logging.debug(f"Forward Virtual Chassis {fwd_vcs}")
        create_vcs_list, update_vcs_list = netbox.add_virtual_chassis_list(fwd_vcs)

        if len(create_vcs_list) > 0:
            logging.info(f"========> {len(create_vcs_list)} virtual chassis[s] added to NetBox")
        if len(update_vcs_list) > 0:
            logging.info(f"========> {len(update_vcs_list)} NetBox virtual chassis[s] updated")
    else:
        logging.info("========> Skipping NetBox Virtual Chassis Update...")

if __name__ == "__main__":
    main()
