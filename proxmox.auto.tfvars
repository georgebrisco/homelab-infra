###############################################################################
# proxmox.auto.tfvars — Proxmox connection and common config
###############################################################################

proxmox_endpoint = "https://192.168.50.12:8006/"
proxmox_node     = "steam"
proxmox_storage  = "local-lvm"

# SSH key deployed into every container at creation time
# NOTE: This is the mgmt-lxc key. Phase 2 will update to the manager's actual key.
ssh_public_key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICuCEpkiokrOAr/t9ju7k0enUOJJAsJICyQj0/Wqmq6j mgmt-lxc"
