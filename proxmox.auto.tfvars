###############################################################################
# proxmox.auto.tfvars — Proxmox connection and common config
###############################################################################

proxmox_endpoint = "https://192.168.50.12:8006/"
proxmox_node     = "steam"
proxmox_storage  = "local-lvm"

# SSH key deployed into every container at creation time
# Manager key (george@IvorTheEngine) — deployed to all existing containers 2026-03-13
ssh_public_key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJ6fA0xsXu+YMANF/JwmrfrzvRV7b7f8H6qWJF93hKLp george@IvorTheEngine"
