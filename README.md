
# Forward Enterprise and NetBox

## Forward Enterprise

Forward Networks’ flagship product, [Forward Enterprise](https://www.forwardnetworks.com/forward-enterprise/), provides a vendor-agnostic *network digital twin* of the network.

This software platform generates a virtual replica, commonly known as a digital twin, encompassing your entire network, including all its devices, connections, and configurations, both on-premises and in the cloud.

The platform enables you to:

- **Proactively identify and resolve issues**
- **Gain deeper network visibility**
- **Simplify network operations**
- **Enhance security posture**

## NetBox

**NetBox** is a **network documentation and Infrastructure Resource Modeling (IRM)** tool designed specifically for network engineers and operators.

It provides:

- **IP address management**
- **DCIM functionality**
- **A centralized source of truth**

## Better Together

The integration between Forward Enterprise and NetBox enables you to:

- Onboard NetBox from Forward Enterprise (Locations, Vendors, Device Types, Models, Devices, Interfaces, Virtual Device Contexts, Virtual Chassis)
- Optionally import device attributes from NetBox into Forward (roles, tenants, racks, etc.)

---

# Onboard a NetBox instance with Forward Data

## Script Execution Workflow

![Script Workflow](./images/script_workflow.png)

The Python script will:

1. **Retrieve Forward Data** (via NQE queries)
2. **Retrieve NetBox Data**
3. **Translate & Map**
4. **Push into NetBox**

|     Forward     |     NetBox      |
|-----------------|-----------------|
| Locations       | Sites           |
| Vendors         | Manufacturers   |
| Device Types    | Device Roles    |
| Device Models   | Device Types    |
| Devices         | Devices         |
| Interfaces      | Interfaces      |
| Virtual Device Contexts | Virtual Device Contexts |
| Virtual Chassis | Virtual Chassis |

---

## Prerequisites

1. **Forward NQE queries** from the Forward Library
2. **A NetBox instance** (can be empty)
3. **Python 3.10+** on your local system
4. *(Optional)* Flask for web-based config creation

---

## Try it Out

### 1. Clone the repository

```bash
git clone https://github.com/forwardnetworks/fwd-netbox
cd fwd-netbox
```

### 2. Create `configuration.yaml`

Two ways to do this:

#### Option 1: Copy the example

```bash
cp configuration.yaml.example configuration.yaml
```

#### Option 2: Use the web form

```bash
python3 netbox_form.py
```

Then open `http://127.0.0.1:5000` in your browser.

### 3. Minimal Example of Configuration

```yaml
forward:
  host: https://fwd.app
  authentication: Basic <auth>
  network_id: 12345
  timeout: 60
  nqe_limit: 1000
  nqe:
    locations_query_id: <id>
    vendors_query_id: <id>
    device_types_query_id: <id>
    device_models_query_id: <id>
    devices_query_id: <id>
    interfaces_query_id: <id>
    virtual_device_contexts_query_id: <id>
    virtual_chassis_query_id: <id>

netbox:
  host: https://netbox.example.com
  authentication: Token <token>
  timeout: 90
  post_limit: 100
  allow_deletes: false

debug: false

add_sites: true
add_manufacturers: true
add_device_roles: true
add_device_types: true
add_devices: true
add_interfaces: true
add_virtual_device_contexts: true
add_virtual_chassis: true
```

---

## 4. Run the Script

```bash
python3 export_to_netbox.py
```

---

## 5. Verify in NetBox

You should see new Sites, Devices, Interfaces, VDCs, and Virtual Chassis populated.

---

## Customizing the Integration

You can customize by modifying:

- NQE queries (and use custom ones with new IDs)
- Python transformation logic (`netbox_interface.py`)

Update your `configuration.yaml` with your new query IDs.

---

## NQE Queries

Forward provides prebuilt NQE queries in:

`/Forward Library/External/NetBox/Forward Devices`

These include:

- Locations
- Vendors
- Device Types
- Device Models
- Devices
- Interfaces
- Virtual Device Contexts
- Virtual Chassis

---

## Deleting Items

If `allow_deletes: true` is set, the script will:

- Compare Forward data to NetBox data
- Delete items in NetBox that are missing from Forward
- Log everything it's about to delete before doing so

---

## Feedback and Contributions

Main contributors:
- Manuel Corona, Forward Networks ([GitHub](https://github.com/Gusymochis), [LinkedIn](https://www.linkedin.com/in/mcorona-ayala/), [Twitter](https://twitter.com/coldalchemy))
- Fabrizio Maccioni, Forward Networks ([GitHub](https://github.com/maccioni), [LinkedIn](https://www.linkedin.com/in/fabrizio-maccioni/), [Twitter](https://twitter.com/fabrimaccioni))
- Craig Johnson, Forward Networks ([GitHub](https://github.com/captainpacket), [LinkedIn](https://www.linkedin.com/in/captainpacket), [Twitter](https://twitter.com/captainpacket))

Join the conversation or get help at the [Forward Networks Community](https://community.forwardnetworks.com/).
