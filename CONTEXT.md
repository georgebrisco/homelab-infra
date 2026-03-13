# homelab-infra — Project Context

> Feed this file to an LLM to resume work on this project.
> Last updated: 2026-03-13 (after gardener integration, all Phase 3 complete).

## Overview

Single Git repository managing a homelab running on one Proxmox VE host (`steam`, 192.168.50.12). All infrastructure is defined as code: Terraform provisions LXC containers and Cloudflare tunnels; Ansible configures the router, DNS, and all services. A dynamic inventory script bridges the two — it reads `terraform output -json` directly (no cache file) and merges in physical devices from `devices.yml`.

**Manager node**: 192.168.50.28 (LXC container `manager`, CT 107). All Terraform and Ansible runs happen here. The repo lives at `/root/projects/homelab-infra`.

**GitHub**: https://github.com/georgebrisco/homelab-infra (private). Push with `git push origin HEAD:main` (local branch is `master`, remote is `main`).

## Architecture Principles

1. **Single source of truth**: The `local.containers` map in `main.tf` defines every Proxmox container. `devices.yml` defines non-Proxmox devices. Everything else is derived.
2. **Dependency chain**: Edit locals → `terraform apply` → `ansible-playbook -i scripts/terraform_inventory.py <playbook>`. The inventory script calls Terraform state directly — no intermediate cache.
3. **DNS-first**: All inter-service communication uses `hostname.homelab` names resolved by AdGuard Home (192.168.50.2). Applications should never hardcode IPs.
4. **Convention over configuration**: Naming conventions and standardisation are preferred over mapping tables, complex scripts, or extra config. If two things need to relate to each other, they should share the same name (e.g., tunnel resource names match container keys, role names = service identity not category).
5. **Role-based grouping**: Each container has a `roles` list. The inventory script auto-generates Ansible groups from these (e.g., role `immich` → group `immich_hosts`). Special roles `k3s_server`, `k3s_agent`, and `tunnel` map to dedicated groups.
6. **Shared variables for cross-cutting concerns**: Config that spans multiple services (e.g., MQTT broker) lives in `group_vars/all/` and is loaded via `vars_files` in playbooks. Change once, reconfigure everywhere.

## Network

- Subnet: 192.168.50.0/24
- Gateway/Router: 192.168.50.1 (TP-Link ER707-M2, managed via Omada Controller at 192.168.50.27:8043)
- DNS: AdGuard Home at 192.168.50.2 (CT 116, static IP)
- NFS: TrueNAS at 192.168.50.44 (physical, path `/mnt/MainPool/local_data/k8s`)
- IoT subnet: 192.168.20.0/24 via static route to Linksys at 192.168.50.32

## Git History

```
9216178 Gardener integration: rtl433 + moisture-proxy roles with shared MQTT config
6b22533 Full monitoring coverage: node_exporter on all 21 hosts
f287453 Deploy node_exporter to Proxmox host, fix backup NFS mkdir
11e70d3 3.6 + 3.7: k8s manifest automation, backup strategy, Makefile
cd33cb8 Add detailed README with architecture, usage, and DR guide
c992cf7 3.5: Service roles + per-service Terraform role names
dfe236f 3.4: Uptime Kuma deployment role
2a5c854 3.9: lxc-prep derives container IDs from inventory group
6fc57d1 3.8: Remove legacy ansible-k3s/inventory.ini
04fbb4d Update CONTEXT.md with full roadmap (Phases 2-4)
e90bf07 Update CONTEXT.md with Phase 3.2-3.3 progress
f83849f Phase 3.3: Prometheus + Grafana monitoring stack role
f7cbb49 Phase 3.2: node_exporter baseline + convention-over-config principle
318a2b4 Rename tunnel resources to match container keys
d449bc5 Phase 3.1: cloudflared deployment role
a2fc04b Phase 3.0: Fix SSH access — deploy manager key to all containers
e8c410a Add LLM context file for project continuity
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
├── secrets.auto.tfvars              # [gitignored] passwords + cloudflare_api_token
├── secrets.auto.tfvars.example      # Template for secrets
├── devices.yml                      # Non-Proxmox devices (steam, HA, TrueNAS, gardener, WAPs)
├── group_vars/
│   └── all/
│       └── mqtt.yml                 # Shared MQTT broker config (consumed via vars_files)
├── CONTEXT.md                       # This file
├── README.md                        # User-facing README with architecture + DR guide
├── Makefile                         # Convenience targets: make help for full list
├── scripts/
│   └── terraform_inventory.py       # Dynamic Ansible inventory (reads TF state + devices.yml)
├── ansible-common/
│   ├── configure.yml                # node_exporter on all containers + physical devices
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
│   ├── configure.yml                # Omada Controller on omada_hosts (config-only)
│   └── roles/omada/{tasks,handlers}/
├── ansible-gardener/
│   ├── configure.yml                # rtl433 + moisture-proxy on gardener_hosts
│   └── roles/
│       ├── rtl433/{tasks,templates,handlers,defaults}/
│       │   # templates: rtl_433.conf.j2, rtl433.service.j2, logrotate.j2
│       └── moisture-proxy/{tasks,templates,handlers,defaults}/
│           # templates: moisture_proxy.py.j2, moisture_proxy.service.j2
├── ansible-dns/
│   ├── configure.yml                # AdGuard DNS rewrites
│   └── roles/adguard-dns/tasks/
├── ansible-router/
│   ├── configure.yml                # DHCP reservations, static routes, DNS
│   ├── inventory.ini                # Static inventory (localhost only)
│   ├── group_vars/all/{main.yml,secrets.yml}
│   └── roles/omada-router/{defaults,tasks}/
├── ansible-k3s/
│   ├── apply-manifests.yml          # Apply k8s manifests in dependency order
│   ├── provision.yml                # Full k3s cluster bootstrap (7 plays)
│   ├── inventory.ini.example
│   ├── group_vars/all/{main.yml,vault.yml}
│   └── roles/{lxc-prep,base,k3s-server,k3s-agent,nfs-storage,kubeconfig}/
├── ansible-backup/
│   ├── backup.yml                   # Proxmox vzdump to TrueNAS + retention
│   └── roles/proxmox-backup/{tasks,templates}/
└── manifests/                       # k8s manifests (applied via make k8s)
    ├── namespaces/portfolio.yaml
    ├── portfolio/{Dockerfile,cronjob-email.yaml,deployment-prices.yaml,secret.yaml.example}
    └── storage/pvc-portfolio-db.yaml
```

## Containers (17 total)

All defined in `local.containers` in `main.tf`. Roles use per-service identity names (not categories).

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
| inference | 106 | inference | .31 | inference | Placeholder for ML serving |
| immich | 111 | immich | .20 | immich | Immich :2283 (Docker Compose) |
| ocsirb_web | 110 | ocsirb-web | .10 | ocsirb_web | Nginx: ocsirb :80 + React :8080 |
| ocsirb_staging | 112 | ocsirb-staging | .13 | ocsirb_staging, tunnel | Nginx + cloudflared (staging.ocsirb.com) |
| preview_site | 922 | preview-site | .22 | web, tunnel | Nginx + cloudflared (preview.theteablendstudio.com) |
| production_site | 997 | production-site | .24 | web, tunnel | Nginx + cloudflared (theteablendstudio.com) |
| k3s_server | 113 | k3s-server | .14 | k3s, k3s_server | k3s control plane |
| k3s_agent_1 | 114 | k3s-agent-1 | .15 | k3s, k3s_agent | k3s worker |
| k3s_agent_2 | 115 | k3s-agent-2 | .16 | k3s, k3s_agent | k3s worker |

## Physical Devices (from devices.yml)

**Managed** (get DHCP + DNS + Ansible inventory):

| Name | IP | MAC | User | Roles | Notes |
|------|----|-----|------|-------|-------|
| steam | .12 | 58:47:ca:77:85:fd | root | proxmox_host | Proxmox 8 hypervisor |
| homeassistant | .11 | d8:3a:dd:cd:a8:b6 | hassio | iot, homeautomation | HA OS (s6 init, not systemd) |
| truenas | .44 | bc:24:11:00:35:85 | root | storage | Immutable /usr, node_exporter at /root/bin/ |
| gardener | .53 | 2c:cf:67:81:f4:03 | root | iot, gardener | Raspberry Pi, USB SDR, rtl_433 + moisture_proxy |

**Non-managed** (get DHCP + DNS only):

| Name | IP | MAC |
|------|----|-----|
| xt8-wap | .3 | 7c:10:c9:e4:a9:90 |
| linksys-iot | .32 | 60:38:e0:d0:65:78 |

### Physical Device Quirks

- **HomeAssistant**: Uses `hassio` user (not root). Runs s6-svscan init (Alpine-based, not systemd). node_exporter deployed as s6 longrun service at `/etc/s6-overlay/s6-rc.d/node-exporter/`.
- **TrueNAS**: Immutable `/usr` filesystem. node_exporter installed to `/root/bin/` instead of `/usr/local/bin/`.
- **Steam (Proxmox)**: PVE firewall requires explicit port rules for node_exporter. Rule in `/etc/pve/local/host.fw`: `IN ACCEPT -source 192.168.50.0/24 -p tcp -dport 9100`.
- **Gardener**: Raspberry Pi OS Bookworm (aarch64). USB RTL-SDR dongle. rtl_433 binary pre-compiled. Logrotate with `copytruncate` to handle open file handles. SD card — watch disk usage.

## Gardener (192.168.50.53)

Raspberry Pi running two services that bridge RF sensors to Home Assistant via MQTT:

**rtl_433**: Listens on 915MHz via USB SDR, decodes Ecowitt/LaCrosse/etc RF signals, publishes to MQTT topics `rtl_433/gardener/devices/...` and `rtl_433/gardener/events`. Config at `/etc/rtl_433/rtl_433.conf`, logs to `/var/log/rtl_433/`. Logrotate configured with `copytruncate` (7 daily, max 100M each) to prevent disk fill.

**moisture_proxy**: Python script that subscribes to rtl_433 MQTT topics, filters Ecowitt WH51 soil moisture sensors, and publishes Home Assistant MQTT auto-discovery messages. Runs as `moistureproxy` user, installed at `/opt/moisture_proxy/`. MQTT config passed via systemd `Environment=` variables.

**Shared MQTT config**: `group_vars/all/mqtt.yml` defines `mqtt_broker`, `mqtt_port`, `mqtt_user`, `mqtt_pass`. All gardener templates reference these vars. Changing the MQTT broker = edit one file + `make gardener`. The playbook loads this via `vars_files` (dynamic inventory doesn't auto-load group_vars).

## Monitoring

**22 Prometheus targets, all up** (17 containers + 4 physical devices + Prometheus self-scrape):

node_exporter (:9100) on all containers and physical devices. Prometheus scrape config is generated from inventory by the monitoring role — new hosts auto-appear when added to inventory and the monitoring role is re-run.

**Grafana**: http://monitoring.homelab:3000

## Dynamic Inventory Groups

Generated by `scripts/terraform_inventory.py`:

- **containers** → all 17 container hostnames (children: k3s_cluster, tunnel_hosts)
- **physical_devices** → steam, homeassistant, truenas, gardener
- **k3s_cluster** → k3s_server, k3s_agents
- **tunnel_hosts** → ocsirb-staging, preview-site, production-site
- **proxmox_host** → steam
- Per-service groups: dns_hosts, management_hosts, development_hosts, monitoring_hosts, uptime_kuma_hosts, omada_hosts, photoprism_hosts, jupyter_hosts, inference_hosts, immich_hosts, ocsirb_web_hosts, ocsirb_staging_hosts, web_hosts, k3s_hosts, storage_hosts, iot_hosts, homeautomation_hosts, gardener_hosts

## Cloudflare Tunnels

| Tunnel resource | Container | Domain | Backend |
|----------------|-----------|--------|---------|
| ocsirb_staging | ocsirb-staging (.13) | staging.ocsirb.com | http://localhost:80 |
| preview_site | preview-site (.22) | preview.theteablendstudio.com | http://localhost:3000 |
| production_site | production-site (.24) | theteablendstudio.com + www | http://localhost:3000 |

Convention: tunnel resource name = container key → cloudflared token lookup is `tunnel_tokens[container_key]`.

## Backup Strategy

**Proxmox vzdump** (deployed via `ansible-backup/backup.yml` targeting `proxmox_host`):
- Daily vzdump of all containers at 02:30 → `/mnt/truenas/backups/proxmox/`
- Retention script at 03:30: 3 daily, 2 weekly, 1 monthly
- Storage: TrueNAS NFS mount on the Proxmox host

## Playbook Usage

All playbooks run from `/root/projects/homelab-infra` on the manager. Use `make help` for full target list.

```bash
# Quick reference — most common operations:
make plan                # Terraform plan
make apply               # Terraform apply
make common              # node_exporter on all hosts
make monitoring          # Prometheus + Grafana
make gardener            # rtl433 + moisture-proxy on gardener Pi
make all-services        # Deploy all service roles
make backup              # Proxmox vzdump cron
make status              # Show all Prometheus targets

# Router (uses its own static inventory):
make router              # DHCP + DNS + static routes
```

## Secrets (gitignored)

| File | Contents |
|------|----------|
| secrets.auto.tfvars | proxmox_password, container_root_password, cloudflare_api_token |
| ansible-router/group_vars/all/secrets.yml | omada_username, omada_password |
| ansible-k3s/group_vars/all/vault.yml | proxmox_password, ansible_ssh_pass |
| group_vars/all/mqtt.yml | mqtt_user, mqtt_pass (**not gitignored — should be**) |

All Proxmox/container/Omada credentials currently use the same password. Phase 2 will address rotation and ansible-vault.

## SSH Key

Manager key (deployed to all 17 containers + all 4 physical devices):
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJ6fA0xsXu+YMANF/JwmrfrzvRV7b7f8H6qWJF93hKLp george@IvorTheEngine
```

## Roadmap

### Phase 3 — Reproducibility ✅ COMPLETE

All items done:
- 3.0: SSH key deployment to all containers + Proxmox host + HA + TrueNAS + gardener
- 3.1: cloudflared role (convention-based: tunnel resource name = container key)
- 3.2: node_exporter baseline on all hosts (22 targets, all up)
- 3.3: Prometheus + Grafana monitoring stack (scrape targets from inventory)
- 3.4: Uptime Kuma deployment role
- 3.5: Service roles for all remaining containers (Immich, PhotoPrism, Jupyter, ocsirb-web, ocsirb-staging, Omada) + per-service Terraform role names
- 3.6: k8s manifest apply playbook (apply-manifests.yml, dependency-ordered)
- 3.7: Proxmox backup to TrueNAS (daily vzdump + retention: 3d/2w/1m)
- 3.8: Deleted legacy ansible-k3s/inventory.ini
- 3.9: lxc-prep role derives container IDs from inventory group
- Gardener integration: rtl433 + moisture-proxy with shared MQTT config
- Makefile with all operations
- README with architecture + DR guide

### Phase 2 — Security Hardening (deferred)

Orthogonal to Phase 3. The longer deferred, the more plaintext credentials accumulate.

- 2.1: Per-service passwords (replace single shared password)
- 2.2: ansible-vault encryption for all secrets files
- 2.3: Move inline credentials (AdGuard, Grafana, MQTT) to vault files
- 2.4: Proxmox API TLS (remove insecure=true)
- 2.5: (Rejected) Remote Terraform backend — DR via git + known vm_ids

### Phase 4 — Maturity (future)

- CI/CD pipeline (tflint, ansible-lint, GitHub Actions or local Drone)
- Auto-generated network diagram from inventory
- Prometheus alertmanager (container down, disk full, high CPU)
- Multi-host Proxmox support (add node field to locals map)
- Router playbook: add gardener DHCP reservation + DNS entry (gardener.homelab)

## Known Issues / Technical Debt

1. **MQTT credentials not gitignored**: `group_vars/all/mqtt.yml` contains MQTT password in plaintext and is committed. Should be encrypted or gitignored.
2. **Password reuse**: Single password across Proxmox, containers, and Omada. Needs rotation + per-service passwords.
3. **No encryption at rest**: secrets.auto.tfvars, vault.yml, mqtt.yml are plaintext. Should use ansible-vault and consider SOPS/age.
4. **Proxmox API over HTTP with insecure=true**: Should configure TLS properly.
5. **AdGuard credentials in plaintext**: adguard_user/password are inline in ansible-dns/configure.yml.
6. **Grafana credentials in plaintext**: Inline in monitoring role defaults.
7. **gardener not in DHCP reservations**: Router playbook hasn't been run to add gardener's reservation. Currently uses existing DHCP lease.
8. **Prometheus scrape config needs re-run**: `make monitoring` needs to be run to pick up gardener as a scrape target (currently working because it was added manually or auto-discovered).

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
- Uptime Kuma: latest (GitHub)
- Omada Controller: TP-Link .deb
