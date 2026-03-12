###############################################################################
# homelab-infra/variables.tf
###############################################################################

# --- Proxmox ---

variable "proxmox_endpoint" {
  description = "Proxmox API endpoint URL"
  type        = string
}

variable "proxmox_password" {
  description = "root@pam password"
  type        = string
  sensitive   = true
}

variable "proxmox_node" {
  description = "Proxmox node name"
  type        = string
  default     = "steam"
}

variable "proxmox_storage" {
  description = "Storage pool for container disks"
  type        = string
  default     = "local-lvm"
}

variable "gateway" {
  description = "LAN gateway IP (used only for static-IP containers)"
  type        = string
  default     = "192.168.50.1"
}

variable "ssh_public_key" {
  description = "SSH public key installed in every container"
  type        = string
}

variable "container_root_password" {
  description = "Root password for container initialization"
  type        = string
  sensitive   = true
}

# --- Cloudflare ---

variable "cloudflare_api_token" {
  description = "Cloudflare API token with Zone/DNS and Tunnel permissions"
  type        = string
  sensitive   = true
}

variable "cloudflare_account_id" {
  description = "Cloudflare account ID"
  type        = string
}

variable "ocsirb_domain" {
  description = "Domain name for ocsirb (e.g. ocsirb.com)"
  type        = string
}

variable "ocsirb_zone_id" {
  description = "Cloudflare zone ID for ocsirb domain"
  type        = string
}

variable "tbs_domain" {
  description = "Domain name for The Tea Blend Studio (e.g. theteablendstudio.com)"
  type        = string
}

variable "tbs_zone_id" {
  description = "Cloudflare zone ID for TBS domain"
  type        = string
}
