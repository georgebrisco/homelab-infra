###############################################################################
# outputs.tf — Structured data for Ansible and scripts
###############################################################################

output "containers" {
  description = "All container data keyed by map name"
  value = {
    for k, v in local.containers : k => {
      vm_id       = v.vm_id
      hostname    = v.hostname
      reserved_ip = v.reserved_ip
      mac         = v.mac
      roles       = v.roles
      privileged  = v.privileged
    }
  }
}

output "dhcp_reservations" {
  description = "DHCP reservations for all containers (for router playbook)"
  value = [
    for k, v in local.containers : {
      name = v.hostname
      mac  = v.mac
      ip   = v.reserved_ip
    }
  ]
}

output "k3s_server_ip" {
  description = "IP of the k3s server node"
  value       = local.k3s_server_entry.reserved_ip
}

output "k3s_nodes" {
  description = "All k3s node details"
  value = {
    for k, v in local.k3s_nodes : k => {
      vm_id    = v.vm_id
      hostname = v.hostname
      mac      = v.mac
      role     = contains(v.roles, "k3s_server") ? "server" : "agent"
    }
  }
}

output "k3s_container_ids" {
  description = "Container IDs for k3s nodes (for lxc-prep role)"
  value       = [for k, v in local.k3s_nodes : v.vm_id]
}

output "cloudflare_tunnels" {
  description = "Tunnel IDs for cloudflared configuration"
  value = {
    ocsirb_staging = cloudflare_zero_trust_tunnel_cloudflared.ocsirb_staging.id
    tbs_preview    = cloudflare_zero_trust_tunnel_cloudflared.tbs_preview.id
    tbs_production = cloudflare_zero_trust_tunnel_cloudflared.tbs_production.id
  }
}

output "dns_servers" {
  description = "DNS server list used by containers"
  value       = local.dns_servers_default
}
