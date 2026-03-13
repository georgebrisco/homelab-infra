# homelab-infra — Project Context

> Feed this file to an LLM to resume work on this project.
> Last updated: 2026-03-13 (after Phase 1 completion).

## Overview

Single Git repository managing a homelab running on one Proxmox VE host (`steam`, 192.168.50.12). All infrastructure is defined as code: Terraform provisions LXC containers and Cloudflare tunnels; Ansible configures the router, DNS, and k3s cluster. A dynamic inventory script bridges the two — it reads `terraform output -json` directly (no cache file) and merges in physical devices from `devices.yml`.

**Manager node**: 192.168.50.28 (LXC container `manager`, CT 107). All Terraform and Ansible runs happen here. The repo lives at `/root/projects/homelab-infra`.

## Architecture Principles

1. **Single source of truth**: The `local.containers` map in `main.tf` defines every Proxmox container. `devices.yml` defines non-Proxmox devices. Everything else is derived.
2. **Dependency chain**: Edit locals → `terraform apply` → `ansible-playbook -i scripts/terraform_inventory.py <playbook>`. The inventory script calls Terraform state directly — no intermediate cache.
3. **DNS-first**: All inter-service communication uses `hostname.homelab` names resolved by AdGuard Home (192.168.50.2). Applications should never hardcode IPs.
4. **Role-based grouping**: Each container has a `roles` list. The inventory script auto-generates Ansible groups from these (e.g., role `media` → group `media_hosts`). Special roles `k3s_server`, `k3s_agent`, and `tunnel` map to dedicated groups.

## Network

- Subnet: 192.168.50.0/24
- Gateway/Router: 192.168.50.1 (TP-Link ER707-M2, managed via Omada Controller at 192.168.50.27:8043)
- DNS: AdGuard Home at 192.168.50.2 (CT 116, static IP)
- NFS: TrueNAS at 192.168.50.44 (physical, path `/mnt/MainPool/local_data/k8s`)
- IoT subnet: 192.168.20.0/24 via static route to Linksys at 192.168.50.32

## Git History

```
40999b6 Update AdGuard DNS credentials and push 22 hostname.homelab rewrites
2604137 Phase 1: Single source of truth for inventory and state
6385c78 Fix k3s provisioning for Proxmox LXC containers
80bbb59 Initial commit: unified homelab infrastructure
```

## File Tree

```
homelab-infra/
├── main.tf                          # Terraform: all 17 containers + 3 Cloudflare tunnels
├── outputs.tf                       # Terraform outputs consumed by Ansible
├── variables.tf                     # Terraform variable declarations
├── proxmox.auto.tfvars              # Proxmox connection, node, storage, SSH key
├── cloudflare.auto.tfvars           # Cloudflare account/zone IDs and domains
├── secrets.auto.tfvars              # [gitignored] proxmox_password, container_root_password, cloudflare_api_token
├── secrets.auto.tfvars.example      # Template for secrets
├── devices.yml                      # Non-Proxmox devices (physical hosts + unmanaged network gear)
├── scripts/
│   └── terraform_inventory.py       # Dynamic Ansible inventory (reads TF state + devices.yml)
├── ansible-dns/
│   ├── configure.yml                # Playbook: push hostname.homelab DNS rewrites to AdGuard
│   └── roles/adguard-dns/tasks/main.yml
├── ansible-router/
│   ├── configure.yml                # Playbook: DHCP reservations, static routes, DNS servers
│   ├── inventory.ini                # Static inventory (localhost only)
│   ├── group_vars/all/
│   │   ├── main.yml                 # Omada URL, DNS settings, static routes
│   │   ├── secrets.yml              # [gitignored] omada_username, omada_password
│   │   └── secrets.yml.example
│   └── roles/omada-router/
│       ├── defaults/main.yml
│       └── tasks/{main,auth,dhcp_reservations,dns_servers,static_routes,logout}.yml
├── ansible-k3s/
│   ├── provision.yml                # Playbook: full k3s cluster bootstrap (7 plays)
│   ├── inventory.ini                # [gitignored] Legacy static inventory — to be deleted
│   ├── inventory.ini.example
│   ├── group_vars/all/
│   │   ├── main.yml                 # k3s_version, nfs_server, nfs_path
│   │   ├── vault.yml                # [gitignored] proxmox_password, ansible_ssh_pass
│   │   └── main.yml.example
│   └── roles/
│       ├── lxc-prep/tasks/main.yml      # Modifies /etc/pve/lxc/<id>.conf on Proxmox host
│       ├── base/{tasks/main.yml, handlers/main.yml}  # apt packages, /dev/kmsg, sshd config
│       ├── k3s-server/{tasks/main.yml, templates/k3s-config.yaml.j2}
│       ├── k3s-agent/{tasks/main.yml, templates/k3s-agent-config.yaml.j2}
│       ├── nfs-storage/{tasks/main.yml, templates/nfs-provisioner.yaml.j2}
│       └── kubeconfig/tasks/main.yml
└── manifests/                       # k8s manifests (applied manually, not yet IaC)
    ├── namespaces/portfolio.yaml
    ├── portfolio/{Dockerfile, cronjob-email.yaml, deployment-prices.yaml, secret.yaml.example}
    └── storage/pvc-portfolio-db.yaml
```

## Containers (17 total)

All defined in `local.containers` in `main.tf`. Key fields: vm_id, hostname, reserved_ip, mac, static (bool), privileged (bool), roles, mounts, dns.

| Key | VM ID | Hostname | IP | Roles | Notes |
|-----|-------|----------|----|-------|-------|
| adguard | 116 | adguard | .2 | dns | Static IP, uses 1.1.1.1/8.8.8.8 as upstream |
| manager | 107 | manager | .28 | management | Runs TF/Ansible |
| devbox | 104 | devbox | .23 | development | NAS + media mounts |
| monitoring | 103 | monitoring | .25 | monitoring | Grafana/Prometheus |
| uptime_kuma | 108 | uptime-kuma | .26 | monitoring | |
| omada | 109 | omada | .27 | network | Omada Controller |
| photoprism | 100 | photoprism | .29 | media | Privileged, Debian, 48GB RAM |
| jupyter | 105 | jupyter | .30 | development | |
| inference | 106 | inference | .31 | ml | |
| immich | 111 | immich | .20 | media | Privileged, Docker |
| ocsirb_web | 110 | ocsirb-web | .10 | web | Debian |
| ocsirb_staging | 112 | ocsirb-staging | .13 | web, tunnel | Cloudflare tunnel |
| preview_site | 922 | preview-site | .22 | web, tunnel | Cloudflare tunnel, NAS mount |
| production_site | 997 | production-site | .24 | web, tunnel | Cloudflare tunnel, NAS mount |
| k3s_server | 113 | k3s-server | .14 | k3s, k3s_server | Privileged |
| k3s_agent_1 | 114 | k3s-agent-1 | .15 | k3s, k3s_agent | Privileged |
| k3s_agent_2 | 115 | k3s-agent-2 | .16 | k3s, k3s_agent | Privileged |

## Physical Devices (from devices.yml)

**Managed** (get DHCP + DNS + Ansible inventory):
- steam: .12, Proxmox host, MAC 58:47:ca:77:85:fd
- homeassistant: .11, iot/homeautomation, MAC d8:3a:dd:cd:a8:b6
- truenas: .44, storage, MAC bc:24:11:00:35:85

**Non-managed** (get DHCP + DNS only):
- xt8-wap: .3, MAC 7c:10:c9:e4:a9:90
- linksys-iot: .32, MAC 60:38:e0:d0:65:78

## Terraform Outputs

| Output | Description | Consumers |
|--------|-------------|-----------|
| containers | Full container map (vm_id, hostname, reserved_ip, mac, roles, privileged) | Inventory script |
| dhcp_reservations | List of {name, mac, ip} for all containers | Router playbook |
| k3s_server_ip | 192.168.50.14 | k3s playbook group vars |
| k3s_nodes | k3s node details with server/agent role | Inventory script |
| k3s_container_ids | [113, 114, 115] | lxc-prep role |
| cloudflare_tunnels | Tunnel IDs for ocsirb_staging, tbs_preview, tbs_production | Future cloudflared roles |
| dns_servers | [192.168.50.2, 9.9.9.9] | Reference |

## Dynamic Inventory Groups

Generated by `scripts/terraform_inventory.py`:

- **all** → containers, physical_devices
- **containers** → k3s_cluster, tunnel_hosts + all 17 container hostnames
- **physical_devices** → steam, homeassistant, truenas
- **k3s_cluster** → k3s_server, k3s_agents (has group vars: k3s_server_ip, k3s_container_ids)
- **k3s_server** → k3s-server
- **k3s_agents** → k3s-agent-1, k3s-agent-2
- **tunnel_hosts** → ocsirb-staging, preview-site, production-site
- **proxmox_host** → steam
- Auto-generated `<role>_hosts` groups: dns_hosts, management_hosts, development_hosts, monitoring_hosts, network_hosts, media_hosts, ml_hosts, web_hosts, storage_hosts, iot_hosts, homeautomation_hosts

## Cloudflare Tunnels

Three Zero Trust tunnels managed by Terraform:

| Tunnel | Container | Domain | Service |
|--------|-----------|--------|---------|
| ocsirb-staging | ocsirb-staging (.13) | staging.ocsirb.com | http://localhost:80 |
| tbs_preview | preview-site (.22) | preview.theteablendstudio.com | http://localhost:3000 |
| tbs_production | production-site (.24) | theteablendstudio.com + www | http://localhost:3000 |

**Note**: cloudflared is not yet deployed to the tunnel containers via Ansible. Tunnel tokens from Terraform output need to be configured on each container. This is a Phase 3 task.

## Playbook Usage

All playbooks run from `/root/projects/homelab-infra` on the manager:

```bash
# Router: DHCP reservations + DNS servers + static routes
ansible-playbook -i ansible-router/inventory.ini ansible-router/configure.yml

# DNS: Push hostname.homelab rewrites to AdGuard Home
ansible-playbook -i scripts/terraform_inventory.py ansible-dns/configure.yml

# k3s: Full cluster provision (lxc-prep → base → server → agents → NFS → kubeconfig)
ansible-playbook -i scripts/terraform_inventory.py ansible-k3s/provision.yml
```

## Secrets (gitignored)

| File | Contents |
|------|----------|
| secrets.auto.tfvars | proxmox_password, container_root_password, cloudflare_api_token |
| ansible-router/group_vars/all/secrets.yml | omada_username, omada_password |
| ansible-k3s/group_vars/all/vault.yml | proxmox_password, ansible_ssh_pass |

All currently use the same password. Phase 2 will address password rotation and ansible-vault encryption.

## SSH Key

Manager's key (deployed to all 17 containers + Proxmox host on 2026-03-13):
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJ6fA0xsXu+YMANF/JwmrfrzvRV7b7f8H6qWJF93hKLp george@IvorTheEngine
```
HomeAssistant (.11) and TrueNAS (.44) still need this key pushed manually.

## Known Issues / Technical Debt

### Security (deferred — do after Phase 3)

> **Decision**: Phase 2 security hardening was deliberately deferred. It is orthogonal to
> Phase 3 reproducibility work and can be done at any time. The only accumulating cost is
> that new roles written in Phase 3 will store credentials in plaintext until vault
> encryption is set up. The Terraform state file is local-only (not backed up), but the
> locals map contains all vm_ids so re-import is mechanical if state is lost.
> Remote backend was rejected in favour of keeping DR simple (git + known vm_ids = recovery).
1. **SSH keys**: ~~DONE~~ Manager key deployed to all containers + Proxmox host. HomeAssistant and TrueNAS still need it manually.
2. **Password reuse**: Single password across Proxmox, containers, and Ansible. Needs rotation + per-service passwords.
3. **No encryption at rest**: secrets.auto.tfvars and vault.yml are plaintext. Should use ansible-vault and consider SOPS/age.
4. **No remote Terraform backend**: State is local on manager. Should move to a remote backend (e.g., Consul, S3, or PostgreSQL on TrueNAS).
5. **Proxmox API over HTTP with insecure=true**: Should configure TLS properly.
6. **AdGuard credentials in plaintext**: adguard_user/password are inline in ansible-dns/configure.yml.

### Reproducibility (Phase 3)
7. **No cloudflared deployment roles**: Tunnel containers don't have cloudflared installed/configured via Ansible.
8. **No service deployment roles**: Monitoring, Immich, PhotoPrism, Jupyter, Inference — all manually configured.
9. **k8s manifests not in CI/CD**: manifests/ directory exists but isn't applied automatically.
10. **No backup strategy**: No automated backups of Proxmox, TrueNAS, or application data.
11. **lxc-prep role uses hardcoded k3s_container_ids**: Should derive from inventory group membership (k3s_cluster group) instead. Fix when k3s playbook is next run with dynamic inventory.
12. **Legacy ansible-k3s/inventory.ini**: Still exists (gitignored). Delete once dynamic inventory is confirmed working with k3s playbook.

## Provider Versions

- Terraform: >= 1.5
- bpg/proxmox: ~> 0.98
- cloudflare/cloudflare: ~> 4.0
- hashicorp/random: ~> 3.0
- AdGuard Home: v0.107.73
