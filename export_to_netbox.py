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
    debug_flag = False  # Set this to True or False based on your needs
    # Import variables from file
    with open(CONFIG_FILE, "r", encoding="UTF-8") as f:
        config = load(f, Loader=Loader)

    if debug_flag:
        logging.getLogger().setLevel(logging.DEBUG)  # Set the logging level to DEBUG if the debug flag is True
        print_variables(config)

    forward = ForwardAPI(config["forward"])
    netbox = NetboxAPI(config["netbox"])
    devices = forward.get_devices()
    logging.debug("========================Forward Devices========================")
    logging.debug(devices)
    netbox_devices = netbox.adapt_forward_device_query(devices)
    logging.debug("========================NetBox Devices========================")
    logging.debug(netbox_devices)
    netbox.add_device_list(netbox_devices, config["interactive"])
    interfaces = forward.get_interfaces()
    logging.debug("========================Forward Interfaces========================")
    logging.debug(interfaces)
    netbox_interfaces = netbox.adapt_forward_interface_query(interfaces)
    logging.debug("========================NetBox Interfaces========================")
    logging.debug(netbox_interfaces)
    netbox.add_interface_list(netbox_interfaces)


if __name__ == "__main__":
    main()
