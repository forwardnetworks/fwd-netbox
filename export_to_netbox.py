#!/usr/bin/env python3
"""Demo script for integrating Forward Enterprise with Netbox."""

from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from common import logging, print_variables, setup_loggers, loggers
from netbox_interface import NetboxAPI
from forward_interface import ForwardAPI

CONFIG_FILE = "configuration.yaml"

def main():
    """Main function"""
    with open(CONFIG_FILE, "r", encoding="UTF-8") as f:
        config = load(f, Loader=Loader)

    setup_loggers(config)

    if config["debug"]:
        logging.getLogger().setLevel(logging.DEBUG)
        print_variables(config)
    else:
        logging.getLogger().setLevel(logging.INFO)

    forward = ForwardAPI(config["forward"])
    netbox = NetboxAPI(config["netbox"])

    if config.get("add_sites"):
        logging.info("========> Updating NetBox Sites...")
        log = loggers.get("sites", logging)
        forward_locations = forward.get_locations()
        log.debug(forward_locations)
        create_sites_list, update_sites_list = netbox.add_site_list(forward_locations)
        for site in create_sites_list:
            log.info(f"Added site: {site['name']}")
        for site in update_sites_list:
            log.info(f"Updated site: {site['name']}")
    else:
        logging.info("========> Skipping NetBox Sites Update...")

    if config.get("add_manufacturers"):
        logging.info("========> Updating NetBox Manufacturers...")
        log = loggers.get("manufacturers", logging)
        fwd_vendors = forward.get_vendors()
        log.debug(fwd_vendors)
        fwd_vendors_adapted = netbox.adapt_forward_vendor_query(fwd_vendors)
        create_manufacturers_list = netbox.add_manufacturer_list(fwd_vendors_adapted)
        for m in create_manufacturers_list:
            log.info(f"Added manufacturer: {m['name']}")
    else:
        logging.info("========> Skipping NetBox Manufacturers Update...")

    if config.get("add_device_roles"):
        logging.info("========> Updating NetBox Device Roles...")
        log = loggers.get("roles", logging)
        fwd_device_types = forward.get_device_types()
        log.debug(fwd_device_types)
        fwd_device_types_adapted = netbox.adapt_forward_device_type_query(fwd_device_types)
        create_roles_list = netbox.add_role_list(fwd_device_types_adapted)
        for role in create_roles_list:
            log.info(f"Added role: {role['name']}")
    else:
        logging.info("========> Skipping NetBox Device Roles Update...")

    if config.get("add_device_types"):
        logging.info("========> Updating NetBox Device Types...")
        log = loggers.get("device_types", logging)
        fwd_models = forward.get_models()
        log.debug(fwd_models)
        fwd_models_adapted = netbox.adapt_forward_model_query(fwd_models)
        create_device_types_list = netbox.add_device_type_list(fwd_models_adapted)
        for dt in create_device_types_list:
            log.info(f"Added device type: {dt['model']}")
    else:
        logging.info("========> Skipping NetBox Device Types Update...")

    if config.get("add_devices"):
        logging.info("========> Updating NetBox Devices...")
        log = loggers.get("devices", logging)
        fwd_devices = forward.get_devices()
        log.debug(fwd_devices)
        fwd_devices_adapted = netbox.adapt_forward_device_query(fwd_devices)
        create_devices_list, update_devices_list = netbox.add_device_list(fwd_devices_adapted)
        for d in create_devices_list:
            log.info(f"Added device: {d['name']}")
        for d in update_devices_list:
            log.info(f"Updated device: {d['name']}")
    else:
        logging.info("========> Skipping NetBox Device Update...")

    if config.get("add_virtual_device_contexts"):
        logging.info("========> Updating NetBox Virtual Device Contexts...")
        log = loggers.get("vdcs", logging)
        fwd_vdcs = forward.get_virtual_device_contexts()
        log.debug(fwd_vdcs)
        adapted_vdcs = netbox.adapt_forward_virtual_device_context_query(fwd_vdcs)
        create_vdc_list, update_vdc_list = netbox.add_virtual_device_context_list(adapted_vdcs)
        for v in create_vdc_list:
            log.info(f"Added VDC: {v['name']}")
        for v in update_vdc_list:
            log.info(f"Updated VDC: {v['name']}")
    else:
        logging.info("========> Skipping NetBox Virtual Device Contexts Update...")

    if config.get("add_virtual_chassis"):
        logging.info("========> Updating NetBox Virtual Chassis...")
        log = loggers.get("virtual_chassis", logging)
        fwd_vcs = forward.get_virtual_chassis()
        log.debug(fwd_vcs)
        create_vcs_list, update_vcs_list = netbox.add_virtual_chassis_list(fwd_vcs)
        for vc in create_vcs_list:
            log.info(f"Added chassis: {vc['name']}")
        for vc in update_vcs_list:
            log.info(f"Updated chassis: {vc['name']}")
    else:
        logging.info("========> Skipping NetBox Virtual Chassis Update...")

    if config.get("add_interfaces"):
        logging.info("========> Updating NetBox Interfaces...")
        log = loggers.get("interfaces", logging)
        fwd_interfaces = forward.get_interfaces()
        log.debug(fwd_interfaces)
        fwd_interfaces_adapted = netbox.adapt_forward_interface_query(fwd_interfaces)
        create_interfaces_list, update_interfaces_list = netbox.add_interface_list(fwd_interfaces_adapted)
        for iface in create_interfaces_list:
            log.info(f"Added interface: {iface['name']}")
        for iface in update_interfaces_list:
            log.info(f"Updated interface: {iface['name']}")
    else:
        logging.info("========> Skipping NetBox Interface Update...")

if __name__ == "__main__":
    main()
