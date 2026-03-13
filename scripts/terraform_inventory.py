#!/usr/bin/env python3
"""Dynamic Ansible inventory from Terraform outputs + devices.yml.

Usage:
  ansible-playbook -i scripts/terraform_inventory.py playbook.yml

Reads Terraform outputs directly from state (no cache) and merges
with devices.yml for non-Proxmox hosts.
"""
import json
import subprocess
import sys
import os

try:
    import yaml
except ImportError:
    # Fallback: parse simple YAML manually if PyYAML not installed
    yaml = None

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(SCRIPT_DIR, "..")
DEVICES_FILE = os.path.join(PROJECT_DIR, "devices.yml")


def get_terraform_outputs():
    """Read outputs directly from Terraform state."""
    result = subprocess.run(
        ["terraform", "output", "-json"],
        cwd=PROJECT_DIR, capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"Warning: terraform output failed: {result.stderr}", file=sys.stderr)
        return {}
    raw = json.loads(result.stdout)
    return {k: v["value"] for k, v in raw.items()}


def load_devices():
    """Load non-Proxmox devices from devices.yml."""
    if not os.path.exists(DEVICES_FILE):
        return {"managed_devices": [], "non_managed_reservations": []}
    with open(DEVICES_FILE) as f:
        if yaml:
            return yaml.safe_load(f) or {}
        else:
            # Minimal fallback — better to install PyYAML
            import re
            content = f.read()
            print("Warning: PyYAML not installed, devices.yml parsing may be incomplete", file=sys.stderr)
            return {"managed_devices": [], "non_managed_reservations": []}


def build_inventory(outputs, devices):
    containers = outputs.get("containers", {})
    k3s_server_ip = outputs.get("k3s_server_ip", "")
    k3s_container_ids = outputs.get("k3s_container_ids", [])

    inventory = {
        "_meta": {"hostvars": {}},
        "all": {"children": ["containers", "physical_devices"]},
        "containers": {
            "hosts": [],
            "children": ["k3s_cluster", "tunnel_hosts"],
        },
        "physical_devices": {"hosts": []},
        "k3s_cluster": {"children": ["k3s_server", "k3s_agents"]},
        "k3s_server": {"hosts": []},
        "k3s_agents": {"hosts": []},
        "tunnel_hosts": {"hosts": []},
        "proxmox_host": {"hosts": []},
    }

    # --- Terraform-managed containers ---
    for key, ct in containers.items():
        hostname = ct["hostname"]
        ip = ct.get("reserved_ip", "")
        if not ip:
            continue

        inventory["containers"]["hosts"].append(hostname)
        inventory["_meta"]["hostvars"][hostname] = {
            "ansible_host": ip,
            "ansible_user": "root",
            "vm_id": ct["vm_id"],
            "container_key": key,
            "container_roles": ct["roles"],
            "mac": ct.get("mac", ""),
        }

        # Auto-group by role
        for role in ct.get("roles", []):
            if role == "k3s_server":
                inventory["k3s_server"]["hosts"].append(hostname)
            elif role == "k3s_agent":
                inventory["k3s_agents"]["hosts"].append(hostname)
            elif role == "tunnel":
                inventory["tunnel_hosts"]["hosts"].append(hostname)
            else:
                group = role + "_hosts"
                if group not in inventory:
                    inventory[group] = {"hosts": []}
                    inventory["all"]["children"].append(group)
                inventory[group]["hosts"].append(hostname)

    # --- Physical devices from devices.yml ---
    for dev in devices.get("managed_devices", []):
        hostname = dev["name"]
        inventory["physical_devices"]["hosts"].append(hostname)
        inventory["_meta"]["hostvars"][hostname] = {
            "ansible_host": dev["ip"],
            "ansible_user": dev.get("ansible_user", "root"),
            "mac": dev.get("mac", ""),
            "device_roles": dev.get("roles", []),
        }
        for role in dev.get("roles", []):
            if role == "proxmox_host":
                group = "proxmox_host"
            else:
                group = role + "_hosts"
            if group not in inventory:
                inventory[group] = {"hosts": []}
                inventory["all"]["children"].append(group)
            inventory[group]["hosts"].append(hostname)

    # --- Group vars ---
    if k3s_server_ip:
        inventory["k3s_cluster"]["vars"] = {
            "k3s_server_ip": k3s_server_ip,
            "k3s_container_ids": k3s_container_ids,
        }

    return inventory


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        outputs = get_terraform_outputs()
        devices = load_devices()
        inventory = build_inventory(outputs, devices)
        print(json.dumps(inventory, indent=2))
    elif len(sys.argv) > 1 and sys.argv[1] == "--host":
        print(json.dumps({}))
    else:
        print(json.dumps({"_meta": {"hostvars": {}}}))
