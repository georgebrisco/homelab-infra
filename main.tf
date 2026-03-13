###############################################################################
# homelab-infra/main.tf — Unified container management
# Generated from terraform state to match actual running containers
###############################################################################

terraform {
  required_version = ">= 1.5"
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
# =============================================================================
# Container inventory — THE single source of truth
# =============================================================================
# Every container is defined here. Terraform for_each iterates this map.
# Ansible dynamic inventory reads it via terraform output.
# Router DHCP reservations are derived from it.
# AdGuard local DNS entries are generated from it.
#
# To add a container: add an entry here, terraform apply, run playbooks.
# To change an IP:    edit reserved_ip here, terraform apply, run playbooks.
# =============================================================================

locals {
  # DNS defaults — referenced once, never duplicated
  dns_servers_default = ["192.168.50.2", "9.9.9.9"]
  dns_servers_adguard = ["1.1.1.1", "8.8.8.8"]

  # OS templates
  ubuntu_template = "local:vztmpl/ubuntu-24.04-standard_24.04-2_amd64.tar.zst"
  debian_template = "local:vztmpl/debian-12-standard_12.7-1_amd64.tar.zst"

  containers = {
    adguard = {
      vm_id       = 116
      hostname    = "adguard"
      template    = local.ubuntu_template
      os_type     = "ubuntu"
      cores       = 1
      memory      = 256
      swap        = 0
      disk_gb     = 4
      reserved_ip = "192.168.50.2"
      mac         = "bc:24:11:c0:12:80"
      static      = true
      privileged  = false
      tags        = []
      mounts      = []
      firewall    = false
      console     = false
      dns         = local.dns_servers_adguard
      roles       = ["dns"]
    }
    manager = {
      vm_id       = 107
      hostname    = "manager"
      template    = local.ubuntu_template
      os_type     = "ubuntu"
      cores       = 2
      memory      = 512
      swap        = 512
      disk_gb     = 8
      reserved_ip = "192.168.50.28"
      mac         = "bc:24:11:3b:8e:78"
      static      = false
      privileged  = false
      tags        = []
      mounts      = []
      firewall    = true
      console     = true
      dns         = local.dns_servers_default
      roles       = ["management"]
    }
    devbox = {
      vm_id       = 104
      hostname    = "devbox"
      template    = local.ubuntu_template
      os_type     = "ubuntu"
      cores       = 2
      memory      = 2048
      swap        = 0
      disk_gb     = 32
      reserved_ip = "192.168.50.23"
      mac         = "bc:24:11:d9:29:3d"
      static      = false
      privileged  = false
      tags        = ["devbox", "infra"]
      mounts = [
        { volume = "/mnt/truenas",       path = "/mnt/nas" },
        { volume = "/mnt/truenas-media", path = "/mnt/media" },
      ]
      firewall = false
      console  = false
      dns      = local.dns_servers_default
      roles    = ["development"]
    }
    monitoring = {
      vm_id       = 103
      hostname    = "monitoring"
      template    = local.ubuntu_template
      os_type     = "ubuntu"
      cores       = 2
      memory      = 2048
      swap        = 512
      disk_gb     = 16
      reserved_ip = "192.168.50.25"
      mac         = "bc:24:11:25:bf:da"
      static      = false
      privileged  = false
      tags        = ["grafana", "monitoring", "prometheus"]
      mounts      = []
      firewall    = false
      console     = false
      dns         = local.dns_servers_default
      roles       = ["monitoring"]
    }
    uptime_kuma = {
      vm_id       = 108
      hostname    = "uptime-kuma"
      template    = local.ubuntu_template
      os_type     = "ubuntu"
      cores       = 1
      memory      = 512
      swap        = 256
      disk_gb     = 8
      reserved_ip = "192.168.50.26"
      mac         = "bc:24:11:10:23:0c"
      static      = false
      privileged  = false
      tags        = ["monitoring", "uptime-kuma"]
      mounts      = []
      firewall    = false
      console     = false
      dns         = local.dns_servers_default
      roles       = ["uptime_kuma"]
    }
    omada = {
      vm_id       = 109
      hostname    = "omada"
      template    = local.ubuntu_template
      os_type     = "ubuntu"
      cores       = 2
      memory      = 4096
      swap        = 1024
      disk_gb     = 16
      reserved_ip = "192.168.50.27"
      mac         = "bc:24:11:f6:9b:27"
      static      = false
      privileged  = false
      tags        = ["monitoring", "network", "omada"]
      mounts      = []
      firewall    = false
      console     = false
      dns         = local.dns_servers_default
      roles       = ["omada"]
    }
    photoprism = {
      vm_id       = 100
      hostname    = "photoprism"
      template    = local.debian_template
      os_type     = "debian"
      cores       = 15
      memory      = 48000
      swap        = 512
      disk_gb     = 32
      reserved_ip = "192.168.50.29"
      mac         = "bc:24:11:41:b4:81"
      static      = false
      privileged  = true
      tags        = ["community-script", "media", "photo"]
      mounts      = []
      firewall    = false
      console     = true
      dns         = local.dns_servers_default
      roles       = ["photoprism"]
    }
    jupyter = {
      vm_id       = 105
      hostname    = "jupyter"
      template    = local.ubuntu_template
      os_type     = "ubuntu"
      cores       = 2
      memory      = 4096
      swap        = 4096
      disk_gb     = 72
      reserved_ip = "192.168.50.30"
      mac         = "bc:24:11:aa:3d:c4"
      static      = false
      privileged  = false
      tags        = []
      mounts      = []
      firewall    = false
      console     = true
      dns         = local.dns_servers_default
      roles       = ["jupyter"]
    }
    inference = {
      vm_id       = 106
      hostname    = "inference"
      template    = local.ubuntu_template
      os_type     = "ubuntu"
      cores       = 2
      memory      = 8192
      swap        = 4096
      disk_gb     = 136
      reserved_ip = "192.168.50.31"
      mac         = "bc:24:11:7e:0a:16"
      static      = false
      privileged  = false
      tags        = []
      mounts      = []
      firewall    = true
      console     = true
      dns         = local.dns_servers_default
      roles       = ["inference"]
    }
    immich = {
      vm_id       = 111
      hostname    = "immich"
      template    = local.ubuntu_template
      os_type     = "ubuntu"
      cores       = 4
      memory      = 8192
      swap        = 1024
      disk_gb     = 32
      reserved_ip = "192.168.50.20"
      mac         = "bc:24:11:f8:2a:48"
      static      = false
      privileged  = true
      tags        = ["docker", "immich", "photos"]
      mounts      = []
      firewall    = false
      console     = false
      dns         = local.dns_servers_default
      roles       = ["immich"]
    }
    ocsirb_web = {
      vm_id       = 110
      hostname    = "ocsirb-web"
      template    = local.debian_template
      os_type     = "debian"
      cores       = 1
      memory      = 256
      swap        = 256
      disk_gb     = 2
      reserved_ip = "192.168.50.10"
      mac         = "bc:24:11:35:82:27"
      static      = false
      privileged  = false
      tags        = []
      mounts      = []
      firewall    = false
      console     = true
      dns         = local.dns_servers_default
      roles       = ["ocsirb_web"]
    }
    ocsirb_staging = {
      vm_id       = 112
      hostname    = "ocsirb-staging"
      template    = local.ubuntu_template
      os_type     = "ubuntu"
      cores       = 1
      memory      = 1024
      swap        = 0
      disk_gb     = 8
      reserved_ip = "192.168.50.13"
      mac         = "bc:24:11:4d:6b:56"
      static      = false
      privileged  = false
      tags        = ["ocsirb", "staging", "website"]
      mounts      = []
      firewall    = false
      console     = false
      dns         = local.dns_servers_default
      roles       = ["ocsirb_staging", "tunnel"]
    }
    preview_site = {
      vm_id       = 922
      hostname    = "preview-site"
      template    = local.ubuntu_template
      os_type     = "ubuntu"
      cores       = 1
      memory      = 1024
      swap        = 0
      disk_gb     = 8
      reserved_ip = "192.168.50.22"
      mac         = "bc:24:11:12:08:02"
      static      = false
      privileged  = false
      tags        = ["preview-site", "website"]
      mounts = [
        { volume = "/mnt/truenas", path = "/mnt/nas" },
      ]
      firewall = false
      console  = false
      dns      = local.dns_servers_default
      roles    = ["web", "tunnel"]
    }
    production_site = {
      vm_id       = 997
      hostname    = "production-site"
      template    = local.ubuntu_template
      os_type     = "ubuntu"
      cores       = 1
      memory      = 1024
      swap        = 0
      disk_gb     = 8
      reserved_ip = "192.168.50.24"
      mac         = "bc:24:11:7b:e6:88"
      static      = false
      privileged  = false
      tags        = ["production-site", "website"]
      mounts = [
        { volume = "/mnt/truenas", path = "/mnt/nas" },
      ]
      firewall = false
      console  = false
      dns      = local.dns_servers_default
      roles    = ["web", "tunnel"]
    }
    k3s_server = {
      vm_id       = 113
      hostname    = "k3s-server"
      template    = local.ubuntu_template
      os_type     = "ubuntu"
      cores       = 2
      memory      = 2048
      swap        = 0
      disk_gb     = 12
      reserved_ip = "192.168.50.14"
      mac         = "bc:24:11:e0:a0:17"
      static      = false
      privileged  = true
      tags        = []
      mounts      = []
      firewall    = false
      console     = false
      dns         = local.dns_servers_default
      roles       = ["k3s", "k3s_server"]
    }
    k3s_agent_1 = {
      vm_id       = 114
      hostname    = "k3s-agent-1"
      template    = local.ubuntu_template
      os_type     = "ubuntu"
      cores       = 2
      memory      = 2048
      swap        = 0
      disk_gb     = 12
      reserved_ip = "192.168.50.15"
      mac         = "bc:24:11:be:d2:fd"
      static      = false
      privileged  = true
      tags        = []
      mounts      = []
      firewall    = false
      console     = false
      dns         = local.dns_servers_default
      roles       = ["k3s", "k3s_agent"]
    }
    k3s_agent_2 = {
      vm_id       = 115
      hostname    = "k3s-agent-2"
      template    = local.ubuntu_template
      os_type     = "ubuntu"
      cores       = 2
      memory      = 2048
      swap        = 0
      disk_gb     = 12
      reserved_ip = "192.168.50.16"
      mac         = "bc:24:11:0c:fe:63"
      static      = false
      privileged  = true
      tags        = []
      mounts      = []
      firewall    = false
      console     = false
      dns         = local.dns_servers_default
      roles       = ["k3s", "k3s_agent"]
    }
  }

  # Derived lookups
  dhcp_containers   = { for k, v in local.containers : k => v if !v.static }
  k3s_nodes         = { for k, v in local.containers : k => v if contains(v.roles, "k3s") }
  k3s_server_entry  = [for k, v in local.containers : v if contains(v.roles, "k3s_server")][0]
  k3s_agent_entries = { for k, v in local.containers : k => v if contains(v.roles, "k3s_agent") }
  tunnel_containers = { for k, v in local.containers : k => v if contains(v.roles, "tunnel") }
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
# Proxmox LXC Containers — single for_each over local.containers
# =============================================================================

resource "proxmox_virtual_environment_container" "ct" {
  for_each = local.containers

  node_name    = local.node
  vm_id        = each.value.vm_id
  unprivileged = !each.value.privileged
  started      = true
  tags         = length(each.value.tags) > 0 ? each.value.tags : null

  operating_system {
    template_file_id = each.value.template
    type             = each.value.os_type
  }

  cpu {
    cores = each.value.cores
  }

  memory {
    dedicated = each.value.memory
    swap      = each.value.swap
  }

  disk {
    datastore_id = local.storage
    size         = each.value.disk_gb
  }

  dynamic "mount_point" {
    for_each = each.value.mounts
    content {
      volume = mount_point.value.volume
      path   = mount_point.value.path
      backup = false
    }
  }

  network_interface {
    name     = "eth0"
    bridge   = "vmbr0"
    firewall = each.value.firewall ? true : null
  }

  initialization {
    hostname = each.value.hostname

    dns {
      servers = each.value.dns
    }

    ip_config {
      ipv4 {
        address = each.value.static ? "${each.value.reserved_ip}/24" : "dhcp"
        gateway = each.value.static ? local.gw : null
      }
    }
  }

  dynamic "console" {
    for_each = each.value.console ? [1] : []
    content {
      enabled   = true
      tty_count = 2
      type      = "tty"
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
# Cloudflare — preview-site tunnel
# =============================================================================

resource "random_password" "preview_site_tunnel_secret" {
  length  = 32
  special = false
}

resource "cloudflare_zero_trust_tunnel_cloudflared" "preview_site" {
  account_id = var.cloudflare_account_id
  name       = "preview-site"
  secret     = base64sha256(random_password.preview_site_tunnel_secret.result)

  lifecycle {
    ignore_changes = [secret]
  }
}

resource "cloudflare_zero_trust_tunnel_cloudflared_config" "preview_site" {
  account_id = var.cloudflare_account_id
  tunnel_id  = cloudflare_zero_trust_tunnel_cloudflared.preview_site.id

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

resource "cloudflare_record" "preview_site" {
  zone_id = var.tbs_zone_id
  name    = "preview"
  type    = "CNAME"
  content = "${cloudflare_zero_trust_tunnel_cloudflared.preview_site.id}.cfargotunnel.com"
  proxied = true
  comment = "preview-site tunnel"
}

# =============================================================================
# Cloudflare — production-site tunnel
# =============================================================================

resource "random_password" "production_site_tunnel_secret" {
  length  = 32
  special = false
}

resource "cloudflare_zero_trust_tunnel_cloudflared" "production_site" {
  account_id = var.cloudflare_account_id
  name       = "production-site"
  secret     = base64sha256(random_password.production_site_tunnel_secret.result)

  lifecycle {
    ignore_changes = [secret]
  }
}

resource "cloudflare_zero_trust_tunnel_cloudflared_config" "production_site" {
  account_id = var.cloudflare_account_id
  tunnel_id  = cloudflare_zero_trust_tunnel_cloudflared.production_site.id

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

resource "cloudflare_record" "production_site_www" {
  zone_id = var.tbs_zone_id
  name    = "www"
  type    = "CNAME"
  content = "${cloudflare_zero_trust_tunnel_cloudflared.production_site.id}.cfargotunnel.com"
  proxied = true
  comment = "production-site www tunnel"
}

resource "cloudflare_record" "production_site_apex" {
  zone_id = var.tbs_zone_id
  name    = "theteablendstudio.com"
  type    = "CNAME"
  content = "${cloudflare_zero_trust_tunnel_cloudflared.production_site.id}.cfargotunnel.com"
  proxied = true
  comment = "production-site apex tunnel"
}
