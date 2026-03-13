# homelab-infra — Project Context

> Feed this file to an LLM to resume work on this project.
> Last updated: 2026-03-13 (after Phase 3.5 service roles).

## Overview

Single Git repository managing a homelab running on one Proxmox VE host (`steam`, 192.168.50.12). All infrastructure is defined as code: Terraform provisions LXC containers and Cloudflare tunnels; Ansible configures the router, DNS, and all services. A dynamic inventory script bridges the two — it reads `terraform output -json` directly (no cache file) and merges in physical devices from `devices.yml`.

**Manager node**: 192.168.50.28 (LXC container `manager`, CT 107). All Terraform and Ansible runs happen here. The repo lives at `/root/projects/homelab-infra`.

## Architecture Principles

1. **Single source of truth**: The `local.containers` map in `main.tf` defines every Proxmox container. `devices.yml` defines non-Proxmox devices. Everything else is derived.
2. **Dependency chain**: Edit locals → `terraform apply` → `ansible-playbook -i scripts/terraform_inventory.py <playbook>`. The inventory script calls Terraform state directly — no intermediate cache.
3. **DNS-first**: All inter-service communication uses `hostname.homelab` names resolved by AdGuard Home (192.168.50.2). Applications should never hardcode IPs.
4. **Convention over configuration**: Naming conventions and standardisation are preferred over mapping tables, complex scripts, or extra config. If two things need to relate to each other, they should share the same name (e.g., tunnel resource names match container keys, role names = service identity not category).
5. **Role-based grouping**: Each container has a `roles` list. The inventory script auto-generates Ansible groups from these (e.g., role `immich` → group `immich_hosts`). Special roles `k3s_server`, `k3s_agent`, and `tunnel` map to dedicated groups.

## Network

- Subnet: 192.168.50.0/24
- Gateway/Router: 192.168.50.1 (TP-Link ER707-M2, managed via Omada Controller at 192.168.50.27:8043)
- DNS: AdGuard Home at 192.168.50.2 (CT 116, static IP)
- NFS: TrueNAS at 192.168.50.44 (physical, path `/mnt/MainPool/local_data/k8s`)
- IoT subnet: 192.168.20.0/24 via static route to Linksys at 192.168.50.32

## File Tree

```
homelab-infra/
├── main.tf                          # Terraform: all 17 containers + 3 Cloudflare tunnels
├── outputs.tf                       # Terraform outputs consumed by Ansible
├── variables.tf                     # Terraform variable declarations
├── proxmox.auto.tfvars              # Proxmox connection, node, storage, SSH key
├── cloudflare.auto.tfvars           # Cloudflare account/zone IDs and domains
├── secrets.auto.tfvars              # [gitignored] passwords + cloudflare_api_token
├── secrets.auto.tfvars.example      # Template for secrets
├── devices.yml                      # Non-Proxmox devices (physical hosts + unmanaged network gear)
├── CONTEXT.md                       # This file
├── scripts/
│   └── terraform_inventory.py       # Dynamic Ansible inventory (reads TF state + devices.yml)
├── ansible-common/
│   ├── configure.yml                # node_exporter on all containers
│   └── roles/node-exporter/{tasks,handlers}/
├── ansible-tunnel/
│   ├── configure.yml                # cloudflared on tunnel_hosts
│   └── roles/cloudflared/tasks/
├── ansible-monitoring/
│   ├── configure.yml                # Prometheus + Grafana on monitoring_hosts
│   └── roles/{prometheus,grafana}/{tasks,handlers,templates}/
├── ansible-uptime-kuma/
│   ├── configure.yml                # Uptime Kuma on uptime_kuma_hosts
│   └── roles/uptime-kuma/tasks/
├── ansible-immich/
│   ├── configure.yml                # Immich (Docker Compose) on immich_hosts
│   └── roles/immich/{tasks,templates,handlers,defaults}/
├── ansible-photoprism/
│   ├── configure.yml                # PhotoPrism on photoprism_hosts
│   └── roles/photoprism/{tasks,templates,handlers,defaults}/
├── ansible-jupyter/
│   ├── configure.yml                # Jupyter Notebook on jupyter_hosts
│   └── roles/jupyter/{tasks,templates,handlers}/
├── ansible-ocsirb-web/
│   ├── configure.yml                # Nginx static sites on ocsirb_web_hosts
│   └── roles/nginx-sites/{tasks,templates,handlers}/
├── ansible-ocsirb-staging/
│   ├── configure.yml                # Nginx staging on ocsirb_staging_hosts
│   └── roles/nginx-staging/{tasks,templates,handlers}/
├── ansible-omada/
│   ├── configure.yml                # Omada Controller on omada_hosts
│   └── roles/omada/{tasks,handlers}/
├── ansible-dns/
│   ├── configure.yml                # AdGuard DNS rewrites
│   └── roles/adguard-dns/tasks/
├── ansible-router/
│   ├── configure.yml                # DHCP reservations, static routes, DNS
│   ├── inventory.ini                # Static inventory (localhost only)
│   ├── group_vars/all/{main.yml,secrets.yml}
│   └── roles/omada-router/{defaults,tasks}/
├── ansible-k3s/
│   ├── apply-manifests.yml        # Apply k8s manifests in dependency order
│   ├── provision.yml                # Full k3s cluster bootstrap (7 plays)
│   ├── inventory.ini.example
│   ├── group_vars/all/{main.yml,vault.yml}
│   └── roles/{lxc-prep,base,k3s-server,k3s-agent,nfs-storage,kubeconfig}/
├── ansible-backup/
│   ├── backup.yml                  # Proxmox vzdump to TrueNAS + retention
│   └── roles/proxmox-backup/{tasks,templates}/
├── Makefile                        # Convenience targets (make help)
└── manifests/                       # k8s manifests (applied via make k8s)
    ├── namespaces/portfolio.yaml
    ├── portfolio/{Dockerfile,cronjob-email.yaml,deployment-prices.yaml,secret.yaml.example}
    └── storage/pvc-portfolio-db.yaml
```

## Containers (17 total)

All defined in `local.containers` in `main.tf`. Roles now use per-service identity names (not categories).

| Key | VM ID | Hostname | IP | Roles | Service |
|-----|-------|----------|----|-------|---------|
| adguard | 116 | adguard | .2 | dns | AdGuard Home DNS |
| manager | 107 | manager | .28 | management | Terraform/Ansible control node |
| devbox | 104 | devbox | .23 | development | Dev environment, NAS mounts |
| monitoring | 103 | monitoring | .25 | monitoring | Prometheus :9090 + Grafana :3000 |
| uptime_kuma | 108 | uptime-kuma | .26 | uptime_kuma | Uptime Kuma :3001 |
| omada | 109 | omada | .27 | omada | TP-Link Omada Controller :8043 |
| photoprism | 100 | photoprism | .29 | photoprism | PhotoPrism :2342 (native binary, SQLite) |
| jupyter | 105 | jupyter | .30 | jupyter | Jupyter Notebook (virtualenv) |
| inference | 106 | inference | .31 | inference | Empty — placeholder for ML serving |
| immich | 111 | immich | .20 | immich | Immich :2283 (Docker Compose: server + ML + postgres + redis) |
| ocsirb_web | 110 | ocsirb-web | .10 | ocsirb_web | Nginx: ocsirb :80 + React site :8080 |
| ocsirb_staging | 112 | ocsirb-staging | .13 | ocsirb_staging, tunnel | Nginx :80 + cloudflared (staging.ocsirb.com) |
| preview_site | 922 | preview-site | .22 | web, tunnel | Nginx :3000 + cloudflared (preview.theteablendstudio.com) |
| production_site | 997 | production-site | .24 | web, tunnel | Nginx :3000 + cloudflared (theteablendstudio.com) |
| k3s_server | 113 | k3s-server | .14 | k3s, k3s_server | k3s control plane |
| k3s_agent_1 | 114 | k3s-agent-1 | .15 | k3s, k3s_agent | k3s worker |
| k3s_agent_2 | 115 | k3s-agent-2 | .16 | k3s, k3s_agent | k3s worker |

## Physical Devices (from devices.yml)

**Managed**: steam (.12, Proxmox host), homeassistant (.11, HA), truenas (.44, NFS storage)
**Non-managed**: xt8-wap (.3, WiFi AP), linksys-iot (.32, IoT router)

## Dynamic Inventory Groups

Generated by `scripts/terraform_inventory.py`:

- **containers** → all 17 container hostnames (children: k3s_cluster, tunnel_hosts)
- **physical_devices** → steam, homeassistant, truenas
- **k3s_cluster** → k3s_server, k3s_agents
- **tunnel_hosts** → ocsirb-staging, preview-site, production-site
- **proxmox_host** → steam
- Per-service groups: dns_hosts, management_hosts, development_hosts, monitoring_hosts, uptime_kuma_hosts, omada_hosts, photoprism_hosts, jupyter_hosts, inference_hosts, immich_hosts, ocsirb_web_hosts, ocsirb_staging_hosts, web_hosts, k3s_hosts, storage_hosts, iot_hosts, homeautomation_hosts

## Cloudflare Tunnels

| Tunnel resource | Container | Domain | Backend |
|----------------|-----------|--------|---------|
| ocsirb_staging | ocsirb-staging (.13) | staging.ocsirb.com | http://localhost:80 |
| preview_site | preview-site (.22) | preview.theteablendstudio.com | http://localhost:3000 |
| production_site | production-site (.24) | theteablendstudio.com + www | http://localhost:3000 |

Convention: tunnel resource name = container key → cloudflared token lookup is `tunnel_tokens[container_key]`.

## Playbook Usage

All playbooks run from `/root/projects/homelab-infra` on the manager:

```bash
# Baseline: node_exporter on all containers
ansible-playbook -i scripts/terraform_inventory.py ansible-common/configure.yml

# Tunnels: cloudflared on tunnel containers
ansible-playbook -i scripts/terraform_inventory.py ansible-tunnel/configure.yml

# Services (each targets its own _hosts group):
ansible-playbook -i scripts/terraform_inventory.py ansible-monitoring/configure.yml
ansible-playbook -i scripts/terraform_inventory.py ansible-uptime-kuma/configure.yml
ansible-playbook -i scripts/terraform_inventory.py ansible-immich/configure.yml
ansible-playbook -i scripts/terraform_inventory.py ansible-photoprism/configure.yml
ansible-playbook -i scripts/terraform_inventory.py ansible-jupyter/configure.yml
ansible-playbook -i scripts/terraform_inventory.py ansible-ocsirb-web/configure.yml
ansible-playbook -i scripts/terraform_inventory.py ansible-ocsirb-staging/configure.yml
ansible-playbook -i scripts/terraform_inventory.py ansible-omada/configure.yml

# DNS: Push hostname.homelab rewrites to AdGuard Home
ansible-playbook -i scripts/terraform_inventory.py ansible-dns/configure.yml

# Router: DHCP + DNS + static routes (uses its own static inventory)
ansible-playbook -i ansible-router/inventory.ini ansible-router/configure.yml

# k3s: Full cluster provision
ansible-playbook -i scripts/terraform_inventory.py ansible-k3s/provision.yml
```

## Secrets (gitignored)

| File | Contents |
|------|----------|
| secrets.auto.tfvars | proxmox_password, container_root_password, cloudflare_api_token |
| ansible-router/group_vars/all/secrets.yml | omada_username, omada_password |
| ansible-k3s/group_vars/all/vault.yml | proxmox_password, ansible_ssh_pass |

All currently use the same password. Phase 2 will address rotation and ansible-vault.

## SSH Key

Manager key (deployed to all 17 containers + Proxmox host):
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJ6fA0xsXu+YMANF/JwmrfrzvRV7b7f8H6qWJF93hKLp george@IvorTheEngine
```
HomeAssistant (.11) and TrueNAS (.44) still need this key pushed manually.

## Roadmap

### Phase 3 — Reproducibility (in progress)

**Completed:**
- 3.0: SSH key deployment to all containers + Proxmox host
- 3.1: cloudflared role (convention-based: tunnel resource name = container key)
- 3.2: node_exporter baseline on all 17 containers (:9100)
- 3.3: Prometheus + Grafana monitoring stack (scrape targets generated from inventory)
- 3.4: Uptime Kuma deployment role
- 3.5: Service roles for remaining containers:
  - Immich (Docker Compose: Docker install + compose file + env)
  - PhotoPrism (native binary config + systemd service)
  - Jupyter (virtualenv + systemd service)
  - ocsirb-web (nginx with 2 static sites on :80 and :8080)
  - ocsirb-staging (nginx staging site, cloudflared via ansible-tunnel)
  - Omada Controller (Java + MongoDB + TP-Link .deb, config-only role)
  - Terraform roles updated: per-service names (immich, photoprism, jupyter, etc.) instead of categories (media, development, ml)
- 3.8: Deleted legacy ansible-k3s/inventory.ini
- 3.9: lxc-prep role derives container IDs from inventory group

- 3.6: k8s manifest apply playbook (`ansible-k3s/apply-manifests.yml`) — applies namespaces, storage, secrets, apps in order
- 3.7: Proxmox backup to TrueNAS (`ansible-backup/backup.yml`) — daily vzdump cron at 02:30, retention: 3 daily / 2 weekly / 1 monthly
- Makefile with targets for all operations (`make help` for full list)

**Remaining:**
- Deploy backup role to Proxmox host: `make backup` (currently dry-run validated, not yet applied)
- Apply k8s manifests once portfolio Docker image is built and pushed
- Push manager SSH key to HomeAssistant (.11) and TrueNAS (.44) manually
- Deploy node_exporter to physical devices for full Prometheus coverage

### Phase 2 — Security Hardening (deferred)

Orthogonal to Phase 3. The longer deferred, the more plaintext credentials accumulate.

- 2.1: Per-service passwords (replace single shared password)
- 2.2: ansible-vault encryption for all secrets files
- 2.3: Move inline credentials (AdGuard, Grafana) to vault files
- 2.4: Proxmox API TLS (remove insecure=true)
- 2.5: (Rejected) Remote Terraform backend — DR via git + known vm_ids

### Phase 4 — Maturity (future)

- CI/CD pipeline (tflint, ansible-lint, GitHub Actions or local Drone)
- Auto-generated network diagram from inventory
- Prometheus alertmanager (container down, disk full, high CPU)
- Multi-host Proxmox support (add node field to locals map)

## Provider Versions

- Terraform: >= 1.5
- bpg/proxmox: ~> 0.98
- cloudflare/cloudflare: ~> 4.0
- hashicorp/random: ~> 3.0
- AdGuard Home: v0.107.73
- Prometheus: 2.53.4
- Grafana: 12.4.1
- node_exporter: 1.8.2
- cloudflared: latest
- Immich: v2 (Docker)
- PhotoPrism: community script install
- Uptime Kuma: latest (GitHub)
- Omada Controller: TP-Link .deb
