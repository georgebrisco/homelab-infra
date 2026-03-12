###############################################################################
# homelab-infra/main.tf — Unified container management
# Generated from terraform state to match actual running containers
###############################################################################

terraform {
  required_providers {
    proxmox = {
      source  = "bpg/proxmox"
      version = "~> 0.98"
    }
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

provider "proxmox" {
  endpoint = var.proxmox_endpoint
  username = "root@pam"
  password = var.proxmox_password
  insecure = true

  ssh {
    agent    = true
    username = "root"
  }
}

provider "cloudflare" {
  api_token = var.cloudflare_api_token
}

# =============================================================================
# Shared data
# =============================================================================

locals {
  node    = var.proxmox_node
  storage = var.proxmox_storage
  gw      = var.gateway
}

# =============================================================================
# CT 116 — adguard  (STATIC .2 — critical DNS infrastructure)
# =============================================================================
resource "proxmox_virtual_environment_container" "adguard" {
  node_name    = local.node
  vm_id        = 116
  unprivileged = true
  started      = true

  operating_system {
    template_file_id = "local:vztmpl/ubuntu-24.04-standard_24.04-2_amd64.tar.zst"
    type             = "ubuntu"
  }

  cpu {
    cores = 1
  }

  memory {
    dedicated = 256
    swap      = 0
  }

  disk {
    datastore_id = local.storage
    size         = 4
  }

  network_interface {
    name   = "eth0"
    bridge = "vmbr0"
  }

  initialization {
    hostname = "adguard"

    dns {
      servers = ["1.1.1.1", "8.8.8.8"]
    }

    ip_config {
      ipv4 {
        address = "192.168.50.2/24"
        gateway = local.gw
      }
    }
  }

  lifecycle {
    ignore_changes = [
      operating_system,
      description,
    ]
  }
}

# =============================================================================
# CT 107 — manager
# =============================================================================
resource "proxmox_virtual_environment_container" "manager" {
  node_name    = local.node
  vm_id        = 107
  unprivileged = true
  started      = true

  operating_system {
    template_file_id = "local:vztmpl/ubuntu-24.04-standard_24.04-2_amd64.tar.zst"
    type             = "ubuntu"
  }

  cpu {
    cores = 2
  }

  memory {
    dedicated = 512
    swap      = 512
  }

  disk {
    datastore_id = local.storage
    size         = 8
  }

  network_interface {
    name     = "eth0"
    bridge   = "vmbr0"
    firewall = true
  }

  initialization {
    hostname = "manager"

    dns {
      servers = ["192.168.50.2", "9.9.9.9"]
    }

    ip_config {
      ipv4 {
        address = "dhcp"
      }
    }
  }

  console {
    enabled   = true
    tty_count = 2
    type      = "tty"
  }

  lifecycle {
    ignore_changes = [
      operating_system,
      description,
    ]
  }
}

# =============================================================================
# CT 104 — devbox
# =============================================================================
resource "proxmox_virtual_environment_container" "devbox" {
  node_name    = local.node
  vm_id        = 104
  tags         = ["devbox", "infra"]
  unprivileged = true
  started      = true

  operating_system {
    template_file_id = "local:vztmpl/ubuntu-24.04-standard_24.04-2_amd64.tar.zst"
    type             = "ubuntu"
  }

  cpu {
    cores = 2
  }

  memory {
    dedicated = 2048
    swap      = 0
  }

  disk {
    datastore_id = local.storage
    size         = 32
  }

  mount_point {
    volume = "/mnt/truenas"
    path   = "/mnt/nas"
    backup = false
  }

  mount_point {
    volume = "/mnt/truenas-media"
    path   = "/mnt/media"
    backup = false
  }

  network_interface {
    name   = "eth0"
    bridge = "vmbr0"
  }

  initialization {
    hostname = "devbox"

    dns {
      servers = ["192.168.50.2", "9.9.9.9"]
    }

    ip_config {
      ipv4 {
        address = "dhcp"
      }
    }
  }

  lifecycle {
    ignore_changes = [
      operating_system,
      description,
    ]
  }
}

# =============================================================================
# CT 103 — monitoring
# =============================================================================
resource "proxmox_virtual_environment_container" "monitoring" {
  node_name    = local.node
  vm_id        = 103
  tags         = ["grafana", "monitoring", "prometheus"]
  unprivileged = true
  started      = true

  operating_system {
    template_file_id = "local:vztmpl/ubuntu-24.04-standard_24.04-2_amd64.tar.zst"
    type             = "ubuntu"
  }

  cpu {
    cores = 2
  }

  memory {
    dedicated = 2048
    swap      = 512
  }

  disk {
    datastore_id = local.storage
    size         = 16
  }

  network_interface {
    name   = "eth0"
    bridge = "vmbr0"
  }

  initialization {
    hostname = "monitoring"

    dns {
      servers = ["192.168.50.2", "9.9.9.9"]
    }

    ip_config {
      ipv4 {
        address = "dhcp"
      }
    }
  }

  lifecycle {
    ignore_changes = [
      operating_system,
      description,
    ]
  }
}

# =============================================================================
# CT 108 — uptime-kuma
# =============================================================================
resource "proxmox_virtual_environment_container" "uptime_kuma" {
  node_name    = local.node
  vm_id        = 108
  tags         = ["monitoring", "uptime-kuma"]
  unprivileged = true
  started      = true

  operating_system {
    template_file_id = "local:vztmpl/ubuntu-24.04-standard_24.04-2_amd64.tar.zst"
    type             = "ubuntu"
  }

  cpu {
    cores = 1
  }

  memory {
    dedicated = 512
    swap      = 256
  }

  disk {
    datastore_id = local.storage
    size         = 8
  }

  network_interface {
    name   = "eth0"
    bridge = "vmbr0"
  }

  initialization {
    hostname = "uptime-kuma"

    dns {
      servers = ["192.168.50.2", "9.9.9.9"]
    }

    ip_config {
      ipv4 {
        address = "dhcp"
      }
    }
  }

  lifecycle {
    ignore_changes = [
      operating_system,
      description,
    ]
  }
}

# =============================================================================
# CT 109 — omada  (switch LAST — controls the network!)
# =============================================================================
resource "proxmox_virtual_environment_container" "omada" {
  node_name    = local.node
  vm_id        = 109
  tags         = ["monitoring", "network", "omada"]
  unprivileged = true
  started      = true

  operating_system {
    template_file_id = "local:vztmpl/ubuntu-24.04-standard_24.04-2_amd64.tar.zst"
    type             = "ubuntu"
  }

  cpu {
    cores = 2
  }

  memory {
    dedicated = 4096
    swap      = 1024
  }

  disk {
    datastore_id = local.storage
    size         = 16
  }

  network_interface {
    name   = "eth0"
    bridge = "vmbr0"
  }

  initialization {
    hostname = "omada"

    dns {
      servers = ["192.168.50.2", "9.9.9.9"]
    }

    ip_config {
      ipv4 {
        address = "dhcp"
      }
    }
  }

  lifecycle {
    ignore_changes = [
      operating_system,
      description,
    ]
  }
}

# =============================================================================
# CT 100 — photoprism  (PRIVILEGED, high resources)
# =============================================================================
resource "proxmox_virtual_environment_container" "photoprism" {
  node_name    = local.node
  vm_id        = 100
  tags         = ["community-script", "media", "photo"]
  unprivileged = false
  started      = true

  operating_system {
    template_file_id = "local:vztmpl/debian-12-standard_12.7-1_amd64.tar.zst"
    type             = "debian"
  }

  cpu {
    cores = 15
  }

  memory {
    dedicated = 48000
    swap      = 512
  }

  disk {
    datastore_id = local.storage
    size         = 32
  }

  network_interface {
    name   = "eth0"
    bridge = "vmbr0"
  }

  initialization {
    hostname = "photoprism"

    dns {
      servers = ["192.168.50.2", "9.9.9.9"]
    }

    ip_config {
      ipv4 {
        address = "dhcp"
      }
    }
  }

  console {
    enabled   = true
    tty_count = 2
    type      = "tty"
  }

  lifecycle {
    ignore_changes = [
      operating_system,
      description,
    ]
  }
}

# =============================================================================
# CT 105 — jupyter
# =============================================================================
resource "proxmox_virtual_environment_container" "jupyter" {
  node_name    = local.node
  vm_id        = 105
  unprivileged = true
  started      = true

  operating_system {
    template_file_id = "local:vztmpl/ubuntu-24.04-standard_24.04-2_amd64.tar.zst"
    type             = "ubuntu"
  }

  cpu {
    cores = 2
  }

  memory {
    dedicated = 4096
    swap      = 4096
  }

  disk {
    datastore_id = local.storage
    size         = 72
  }

  network_interface {
    name   = "eth0"
    bridge = "vmbr0"
  }

  initialization {
    hostname = "jupyter"

    dns {
      servers = ["192.168.50.2", "9.9.9.9"]
    }

    ip_config {
      ipv4 {
        address = "dhcp"
      }
    }
  }

  console {
    enabled   = true
    tty_count = 2
    type      = "tty"
  }

  lifecycle {
    ignore_changes = [
      operating_system,
      description,
    ]
  }
}

# =============================================================================
# CT 106 — inference
# =============================================================================
resource "proxmox_virtual_environment_container" "inference" {
  node_name    = local.node
  vm_id        = 106
  unprivileged = true
  started      = true

  operating_system {
    template_file_id = "local:vztmpl/ubuntu-24.04-standard_24.04-2_amd64.tar.zst"
    type             = "ubuntu"
  }

  cpu {
    cores = 2
  }

  memory {
    dedicated = 8192
    swap      = 4096
  }

  disk {
    datastore_id = local.storage
    size         = 136
  }

  network_interface {
    name     = "eth0"
    bridge   = "vmbr0"
    firewall = true
  }

  initialization {
    hostname = "inference"

    dns {
      servers = ["192.168.50.2", "9.9.9.9"]
    }

    ip_config {
      ipv4 {
        address = "dhcp"
      }
    }
  }

  console {
    enabled   = true
    tty_count = 2
    type      = "tty"
  }

  lifecycle {
    ignore_changes = [
      operating_system,
      description,
    ]
  }
}

# =============================================================================
# CT 111 — immich  (PRIVILEGED)
# =============================================================================
resource "proxmox_virtual_environment_container" "immich" {
  node_name    = local.node
  vm_id        = 111
  tags         = ["docker", "immich", "photos"]
  unprivileged = false
  started      = true

  operating_system {
    template_file_id = "local:vztmpl/ubuntu-24.04-standard_24.04-2_amd64.tar.zst"
    type             = "ubuntu"
  }

  cpu {
    cores = 4
  }

  memory {
    dedicated = 8192
    swap      = 1024
  }

  disk {
    datastore_id = local.storage
    size         = 32
  }

  network_interface {
    name   = "eth0"
    bridge = "vmbr0"
  }

  initialization {
    hostname = "immich"

    dns {
      servers = ["192.168.50.2", "9.9.9.9"]
    }

    ip_config {
      ipv4 {
        address = "dhcp"
      }
    }
  }

  lifecycle {
    ignore_changes = [
      operating_system,
      description,
    ]
  }
}

# =============================================================================
# CT 110 — ocsirb-web
# =============================================================================
resource "proxmox_virtual_environment_container" "ocsirb_web" {
  node_name    = local.node
  vm_id        = 110
  unprivileged = true
  started      = true

  operating_system {
    template_file_id = "local:vztmpl/debian-12-standard_12.7-1_amd64.tar.zst"
    type             = "debian"
  }

  cpu {
    cores = 1
  }

  memory {
    dedicated = 256
    swap      = 256
  }

  disk {
    datastore_id = local.storage
    size         = 2
  }

  network_interface {
    name   = "eth0"
    bridge = "vmbr0"
  }

  initialization {
    hostname = "ocsirb-web"

    dns {
      servers = ["192.168.50.2", "9.9.9.9"]
    }

    ip_config {
      ipv4 {
        address = "dhcp"
      }
    }
  }

  console {
    enabled   = true
    tty_count = 2
    type      = "tty"
  }

  lifecycle {
    ignore_changes = [
      operating_system,
      description,
    ]
  }
}

# =============================================================================
# CT 112 — ocsirb-staging
# =============================================================================
resource "proxmox_virtual_environment_container" "ocsirb_staging" {
  node_name    = local.node
  vm_id        = 112
  tags         = ["ocsirb", "staging", "website"]
  unprivileged = true
  started      = true

  operating_system {
    template_file_id = "local:vztmpl/ubuntu-24.04-standard_24.04-2_amd64.tar.zst"
    type             = "ubuntu"
  }

  cpu {
    cores = 1
  }

  memory {
    dedicated = 1024
    swap      = 0
  }

  disk {
    datastore_id = local.storage
    size         = 8
  }

  network_interface {
    name   = "eth0"
    bridge = "vmbr0"
  }

  initialization {
    hostname = "ocsirb-staging"

    dns {
      servers = ["192.168.50.2", "9.9.9.9"]
    }

    ip_config {
      ipv4 {
        address = "dhcp"
      }
    }
  }

  lifecycle {
    ignore_changes = [
      operating_system,
      description,
    ]
  }
}

# =============================================================================
# CT 922 — preview-site
# =============================================================================
resource "proxmox_virtual_environment_container" "preview_site" {
  node_name    = local.node
  vm_id        = 922
  tags         = ["preview-site", "website"]
  unprivileged = true
  started      = true

  operating_system {
    template_file_id = "local:vztmpl/ubuntu-24.04-standard_24.04-2_amd64.tar.zst"
    type             = "ubuntu"
  }

  cpu {
    cores = 1
  }

  memory {
    dedicated = 1024
    swap      = 0
  }

  disk {
    datastore_id = local.storage
    size         = 8
  }

  mount_point {
    volume = "/mnt/truenas"
    path   = "/mnt/nas"
    backup = false
  }

  network_interface {
    name   = "eth0"
    bridge = "vmbr0"
  }

  initialization {
    hostname = "preview-site"

    dns {
      servers = ["192.168.50.2", "9.9.9.9"]
    }

    ip_config {
      ipv4 {
        address = "dhcp"
      }
    }
  }

  lifecycle {
    ignore_changes = [
      operating_system,
      description,
    ]
  }
}

# =============================================================================
# CT 997 — production-site
# =============================================================================
resource "proxmox_virtual_environment_container" "production_site" {
  node_name    = local.node
  vm_id        = 997
  tags         = ["production-site", "website"]
  unprivileged = true
  started      = true

  operating_system {
    template_file_id = "local:vztmpl/ubuntu-24.04-standard_24.04-2_amd64.tar.zst"
    type             = "ubuntu"
  }

  cpu {
    cores = 1
  }

  memory {
    dedicated = 1024
    swap      = 0
  }

  disk {
    datastore_id = local.storage
    size         = 8
  }

  mount_point {
    volume = "/mnt/truenas"
    path   = "/mnt/nas"
    backup = false
  }

  network_interface {
    name   = "eth0"
    bridge = "vmbr0"
  }

  initialization {
    hostname = "production-site"

    dns {
      servers = ["192.168.50.2", "9.9.9.9"]
    }

    ip_config {
      ipv4 {
        address = "dhcp"
      }
    }
  }

  lifecycle {
    ignore_changes = [
      operating_system,
      description,
    ]
  }
}

# =============================================================================
# CT 113 — k3s-server  (PRIVILEGED)
# =============================================================================
resource "proxmox_virtual_environment_container" "k3s_server" {
  node_name    = local.node
  vm_id        = 113
  unprivileged = false
  started      = true

  operating_system {
    template_file_id = "local:vztmpl/ubuntu-24.04-standard_24.04-2_amd64.tar.zst"
    type             = "ubuntu"
  }

  cpu {
    cores = 2
  }

  memory {
    dedicated = 2048
    swap      = 0
  }

  disk {
    datastore_id = local.storage
    size         = 12
  }

  network_interface {
    name   = "eth0"
    bridge = "vmbr0"
  }

  initialization {
    hostname = "k3s-server"

    dns {
      servers = ["192.168.50.2", "9.9.9.9"]
    }

    ip_config {
      ipv4 {
        address = "dhcp"
      }
    }
  }

  lifecycle {
    ignore_changes = [
      operating_system,
      description,
    ]
  }
}

# =============================================================================
# CT 114 — k3s-agent-1  (PRIVILEGED)
# =============================================================================
resource "proxmox_virtual_environment_container" "k3s_agent_1" {
  node_name    = local.node
  vm_id        = 114
  unprivileged = false
  started      = true

  operating_system {
    template_file_id = "local:vztmpl/ubuntu-24.04-standard_24.04-2_amd64.tar.zst"
    type             = "ubuntu"
  }

  cpu {
    cores = 2
  }

  memory {
    dedicated = 2048
    swap      = 0
  }

  disk {
    datastore_id = local.storage
    size         = 12
  }

  network_interface {
    name   = "eth0"
    bridge = "vmbr0"
  }

  initialization {
    hostname = "k3s-agent-1"

    dns {
      servers = ["192.168.50.2", "9.9.9.9"]
    }

    ip_config {
      ipv4 {
        address = "dhcp"
      }
    }
  }

  lifecycle {
    ignore_changes = [
      operating_system,
      description,
    ]
  }
}

# =============================================================================
# CT 115 — k3s-agent-2  (PRIVILEGED)
# =============================================================================
resource "proxmox_virtual_environment_container" "k3s_agent_2" {
  node_name    = local.node
  vm_id        = 115
  unprivileged = false
  started      = true

  operating_system {
    template_file_id = "local:vztmpl/ubuntu-24.04-standard_24.04-2_amd64.tar.zst"
    type             = "ubuntu"
  }

  cpu {
    cores = 2
  }

  memory {
    dedicated = 2048
    swap      = 0
  }

  disk {
    datastore_id = local.storage
    size         = 12
  }

  network_interface {
    name   = "eth0"
    bridge = "vmbr0"
  }

  initialization {
    hostname = "k3s-agent-2"

    dns {
      servers = ["192.168.50.2", "9.9.9.9"]
    }

    ip_config {
      ipv4 {
        address = "dhcp"
      }
    }
  }

  lifecycle {
    ignore_changes = [
      operating_system,
      description,
    ]
  }
}

# =============================================================================
# Cloudflare — ocsirb staging tunnel
# =============================================================================

resource "random_password" "ocsirb_tunnel_secret" {
  length  = 32
  special = false
}

resource "cloudflare_zero_trust_tunnel_cloudflared" "ocsirb_staging" {
  account_id = var.cloudflare_account_id
  name       = "ocsirb-staging"
  secret     = base64sha256(random_password.ocsirb_tunnel_secret.result)

  lifecycle {
    ignore_changes = [secret]
  }
}

resource "cloudflare_zero_trust_tunnel_cloudflared_config" "ocsirb_staging" {
  account_id = var.cloudflare_account_id
  tunnel_id  = cloudflare_zero_trust_tunnel_cloudflared.ocsirb_staging.id

  config {
    ingress_rule {
      hostname = "staging.${var.ocsirb_domain}"
      service  = "http://localhost:80"
    }
    ingress_rule {
      service = "http_status:404"
    }
  }
}

resource "cloudflare_record" "ocsirb_staging" {
  zone_id = var.ocsirb_zone_id
  name    = "staging"
  type    = "CNAME"
  content = "${cloudflare_zero_trust_tunnel_cloudflared.ocsirb_staging.id}.cfargotunnel.com"
  proxied = true
  comment = "ocsirb staging tunnel"
}

# =============================================================================
# Cloudflare — TBS preview tunnel
# =============================================================================

resource "random_password" "tbs_preview_tunnel_secret" {
  length  = 32
  special = false
}

resource "cloudflare_zero_trust_tunnel_cloudflared" "tbs_preview" {
  account_id = var.cloudflare_account_id
  name       = "preview-site"
  secret     = base64sha256(random_password.tbs_preview_tunnel_secret.result)

  lifecycle {
    ignore_changes = [secret]
  }
}

resource "cloudflare_zero_trust_tunnel_cloudflared_config" "tbs_preview" {
  account_id = var.cloudflare_account_id
  tunnel_id  = cloudflare_zero_trust_tunnel_cloudflared.tbs_preview.id

  config {
    ingress_rule {
      hostname = "preview.${var.tbs_domain}"
      service  = "http://localhost:3000"
    }
    ingress_rule {
      service = "http_status:404"
    }
  }
}

resource "cloudflare_record" "tbs_preview" {
  zone_id = var.tbs_zone_id
  name    = "preview"
  type    = "CNAME"
  content = "${cloudflare_zero_trust_tunnel_cloudflared.tbs_preview.id}.cfargotunnel.com"
  proxied = true
  comment = "TBS preview tunnel"
}

# =============================================================================
# Cloudflare — TBS production tunnel
# =============================================================================

resource "random_password" "tbs_production_tunnel_secret" {
  length  = 32
  special = false
}

resource "cloudflare_zero_trust_tunnel_cloudflared" "tbs_production" {
  account_id = var.cloudflare_account_id
  name       = "production-site"
  secret     = base64sha256(random_password.tbs_production_tunnel_secret.result)

  lifecycle {
    ignore_changes = [secret]
  }
}

resource "cloudflare_zero_trust_tunnel_cloudflared_config" "tbs_production" {
  account_id = var.cloudflare_account_id
  tunnel_id  = cloudflare_zero_trust_tunnel_cloudflared.tbs_production.id

  config {
    ingress_rule {
      hostname = var.tbs_domain
      service  = "http://localhost:3000"
    }
    ingress_rule {
      hostname = "www.${var.tbs_domain}"
      service  = "http://localhost:3000"
    }
    ingress_rule {
      service = "http_status:404"
    }
  }
}

resource "cloudflare_record" "tbs_production_www" {
  zone_id = var.tbs_zone_id
  name    = "www"
  type    = "CNAME"
  content = "${cloudflare_zero_trust_tunnel_cloudflared.tbs_production.id}.cfargotunnel.com"
  proxied = true
  comment = "TBS production www tunnel"
}

resource "cloudflare_record" "tbs_production_apex" {
  zone_id = var.tbs_zone_id
  name    = "theteablendstudio.com"
  type    = "CNAME"
  content = "${cloudflare_zero_trust_tunnel_cloudflared.tbs_production.id}.cfargotunnel.com"
  proxied = true
  comment = "TBS production apex tunnel"
}
