###############################################################################
# proxmox.auto.tfvars — shared config (single source of truth)
#
# This file lives at the repo root and is symlinked into each Terraform project:
#   mgmt-infra/proxmox.auto.tfvars       -> ../proxmox.auto.tfvars
#   monitoring-infra/proxmox.auto.tfvars -> ../proxmox.auto.tfvars
#   website-infra/proxmox.auto.tfvars    -> ../proxmox.auto.tfvars
#
# Terraform auto-loads *.auto.tfvars files so no -var-file flag is needed.
###############################################################################

# Proxmox host — update proxmox_endpoint here when the host IP changes
proxmox_endpoint = "https://192.168.50.12:8006/"
proxmox_node     = "steam"
proxmox_storage  = "local-lvm"

# SSH key deployed into every container at creation time (mgmt-lxc keypair on manager)
# Rotate by updating this value and running terraform apply + ansible-playbook on each project
ssh_public_key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICuCEpkiokrOAr/t9ju7k0enUOJJAsJICyQj0/Wqmq6j mgmt-lxc"
