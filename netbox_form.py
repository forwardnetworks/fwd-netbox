from flask import Flask, request, render_template
import yaml

app = Flask(__name__)

default_values = {
    "debug": False,
    "add_sites": True,
    "add_manufacturers": True,
    "add_device_roles": True,
    "add_device_types": True,
    "add_devices": True,
    "add_interfaces": True,
    "add_virtual_device_contexts": True,
    "add_virtual_chassis": True,
    "forward_host": "https://fwd.app",
    "forward_authentication": "<basic auth>",
    "forward_network_id": "123456",
    "forward_timeout": 60,
    "nqe_device_models_query_id": "FQ_b28e7cde85cd0ce72d08dc4ab92ba66d6067f4d4",
    "nqe_device_types_query_id": "FQ_64a3a84cd27d225e5dd22e44a7e8d2f98d513a44",
    "nqe_vendors_query_id": "FQ_dfa37b83121f84406e6da206365a4d4294f0ccaa",
    "nqe_devices_query_id": "FQ_837817437f52a25bcfb88fe2b789040af9d44daa",
    "nqe_interfaces_query_id": "FQ_97bcba26a420b4ed948bbd5d9c628e17150979e7",
    "nqe_locations_query_id": "FQ_7327e06da074e257fffe3b4968b8986c85dcd4e9",
    "netbox_host": "<URL>",
    "netbox_authentication": "<auth token>",
    "netbox_timeout": 90,
    "request_limit": 50,
    "post_limit": 100,
    "allow_deletes": False
}

@app.route('/', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        # Collect form data
        form_data = request.form.to_dict()

        # Convert form data into YAML structure
        yaml_data = {
            "debug": form_data.get("debug") == "true",
            "add_sites": form_data.get("add_sites") == "true",
            "add_manufacturers": form_data.get("add_manufacturers") == "true",
            "add_device_roles": form_data.get("add_device_roles") == "true",
            "add_device_types": form_data.get("add_device_types") == "true",
            "add_devices": form_data.get("add_devices") == "true",
            "add_interfaces": form_data.get("add_interfaces") == "true",
            "add_virtual_device_contexts": form_data.get("add_virtual_device_contexts") == "true",
            "add_virtual_chassis": form_data.get("add_virtual_chassis") == "true",
            "forward": {
                "host": form_data.get("forward_host"),
                "authentication": "Basic " + form_data.get("forward_authentication"),
                "network_id": int(form_data.get("forward_network_id")),
                "timeout": int(form_data.get("forward_timeout", 60)),
                "nqe": {
                    "device_models_query_id": form_data.get("nqe_device_models_query_id"),
                    "device_types_query_id": form_data.get("nqe_device_types_query_id"),
                    "vendors_query_id": form_data.get("nqe_vendors_query_id"),
                    "devices_query_id": form_data.get("nqe_devices_query_id"),
                    "interfaces_query_id": form_data.get("nqe_interfaces_query_id"),
                    "locations_query_id": form_data.get("nqe_locations_query_id"),
                },
            },
            "netbox": {
                "host": form_data.get("netbox_host"),
                "authentication": "Token " + form_data.get("netbox_authentication"),
                "timeout": int(form_data.get("netbox_timeout", 90)),
                "request_limit": int(form_data.get("request_limit", 50)),
                "post_limit": int(form_data.get("post_limit", 100)),
                "allow_deletes": form_data.get("allow_deletes") == "true"
            },
        }

        # Write YAML data to a file
        with open('configuration.yaml', 'w') as yaml_file:
            yaml.dump(yaml_data, yaml_file, default_flow_style=False, sort_keys=False)

        return "YAML configuration file has been generated successfully."

    return render_template('netbox.html', defaults=default_values)


if __name__ == '__main__':
    app.run(debug=True)
