# homelab-infra — Project Context

> Feed this file to an LLM to resume work on this project.
> Last updated: 2026-03-17 (after panoptes camera streaming, HA cameras dashboard, TBS migration).

## Overview

Single Git repository managing a homelab running on one Proxmox VE host (`steam`, 192.168.50.12). All infrastructure is defined as code: Terraform provisions LXC containers and Cloudflare tunnels; Ansible configures the router, DNS, and all services. A dynamic inventory script bridges the two — it reads `terraform output -json` directly (no cache file) and merges in physical devices from `devices.yml`.

**Manager node**: 192.168.50.28 (LXC container `manager`, CT 107). All Terraform and Ansible runs happen here. The repo lives at `/root/projects/homelab-infra`.

**GitHub**: https://github.com/georgebrisco/homelab-infra (private). Push with `git push origin master` (both local and remote branch are `master`).

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

## File Tree

```
homelab-infra/
├── main.tf                          # Terraform: all 18 containers + 4 Cloudflare tunnels
├── outputs.tf                       # Terraform outputs consumed by Ansible
├── variables.tf                     # Terraform variable declarations
├── proxmox.auto.tfvars              # Proxmox connection, node, storage, SSH key
├── cloudflare.auto.tfvars           # Cloudflare account/zone IDs and domains
├── secrets.auto.tfvars              # [gitignored] passwords + cloudflare_api_token
├── secrets.auto.tfvars.example      # Template for secrets
├── devices.yml                      # Non-Proxmox devices (steam, HA, TrueNAS, gardener, panoptes, WAPs)
├── group_vars/
│   └── all/
│       ├── mqtt.yml                 # Shared MQTT broker config
│       ├── homeassistant.yml        # HA non-secret overrides
│       └── homeassistant_vault.yml  # [ansible-vault] HA API token
├── CONTEXT.md                       # This file
├── README.md                        # User-facing README with architecture + DR guide
├── Makefile                         # Convenience targets: make help for full list
├── ansible.cfg                      # vault_password_file = .vault_pass
├── scripts/
│   └── terraform_inventory.py       # Dynamic Ansible inventory (reads TF state + devices.yml)
├── ansible-common/
│   ├── configure.yml                # base-packages + node_exporter on all hosts
│   └── roles/
│       ├── base-packages/{tasks,templates}/  # vim, rsync, curl, unattended-upgrades
│       ├── admin-user/{tasks}/               # Admin user + SSH key + sudoers
│       └── node-exporter/{tasks,handlers}/   # Prometheus node_exporter :9100
├── ansible-tunnel/
│   ├── configure.yml                # cloudflared on tunnel_hosts
│   └── roles/cloudflared/tasks/
├── ansible-monitoring/
│   ├── configure.yml                # Prometheus + Grafana on monitoring_hosts
│   └── roles/{prometheus,grafana}/{tasks,handlers,templates}/
├── ansible-uptime-kuma/
│   ├── configure.yml                # Uptime Kuma on uptime_kuma_hosts
│   └── roles/uptime-kuma/{tasks,defaults,templates,handlers}/
├── ansible-immich/
│   ├── configure.yml                # Immich (Docker Compose) on immich_hosts
│   └── roles/immich/{tasks,templates,handlers,defaults}/
├── ansible-photoprism/
│   ├── configure.yml                # PhotoPrism on photoprism_hosts
│   └── roles/photoprism/{tasks,templates,handlers,defaults}/
├── ansible-jupyter/
│   ├── configure.yml                # Jupyter Notebook on jupyter_hosts
│   └── roles/jupyter/{tasks,templates,handlers}/
├── ansible-dolphin/
│   ├── configure.yml                # Dolphin React app on dolphin_hosts
│   └── roles/dolphin-web/{tasks,templates,handlers}/
├── ansible-tbs/
│   ├── configure.yml                # Tea Blend Studio on preview-site + production-site
│   └── roles/tbs-web/{tasks,defaults}/
├── ansible-panoptes/
│   ├── configure.yml                # RTSP camera streaming on panoptes
│   └── roles/rtsp-camera/{tasks,defaults,templates,handlers}/
├── ansible-homeassistant/
│   ├── configure.yml                # HA YAML config + add-ons + backup sync
│   └── roles/
│       ├── ha-config/{tasks,handlers,defaults,templates}/
│       │   # templates: configuration.yaml.j2, automations.yaml.j2, secrets.yaml.j2
│       │   #   sensors/extras.yaml.j2, sensors/rtl433_wh51.yaml.j2
│       │   #   dashboard-{battery,cameras,climate,internet,moisture,websites}.yaml.j2
│       ├── ha-addons/{tasks}/       # Supervisor API: install, configure, start add-ons
│       └── ha-backup/{tasks}/       # Backup sync to TrueNAS + restore script
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
│       └── moisture-proxy/{tasks,templates,handlers,defaults}/
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

## Containers (18 total)

All defined in `local.containers` in `main.tf`. Roles use per-service identity names (not categories).

| Key | VM ID | Hostname | IP | Roles | Service |
|-----|-------|----------|----|-------|---------|
| adguard | 116 | adguard | .2 | dns | AdGuard Home DNS |
| manager | 107 | manager | .28 | management | Terraform/Ansible control node |
| devbox | 104 | devbox | .23 | development | Dev environment, bare git repos |
| monitoring | 103 | monitoring | .25 | monitoring | Prometheus :9090 + Grafana :3000 |
| uptime_kuma | 108 | uptime-kuma | .26 | uptime_kuma | Uptime Kuma :3001 |
| omada | 109 | omada | .27 | omada | TP-Link Omada Controller :8043 |
| photoprism | 100 | photoprism | .29 | photoprism | PhotoPrism :2342 (native binary, SQLite) |
| jupyter | 105 | jupyter | .30 | jupyter | Jupyter Notebook (virtualenv) |
| inference | 106 | inference | .31 | inference | Placeholder for ML serving |
| immich | 111 | immich | .20 | immich | Immich :2283 (Docker Compose) |
| ocsirb_web | 110 | ocsirb-web | .10 | ocsirb_web | Nginx: ocsirb :80 + React :8080 |
| ocsirb_staging | 112 | ocsirb-staging | .13 | ocsirb_staging, tunnel | Nginx + cloudflared (staging.ocsirb.com) |
| dolphin | 117 | dolphin | .34 | dolphin, tunnel | React app + cloudflared (brisco.org.uk/marie) |
| preview_site | 922 | preview-site | .22 | web, tunnel | PM2/serve + cloudflared (preview.theteablendstudio.com) |
| production_site | 997 | production-site | .24 | web, tunnel | PM2/serve + cloudflared (theteablendstudio.com) |
| k3s_server | 113 | k3s-server | .14 | k3s, k3s_server | k3s control plane |
| k3s_agent_1 | 114 | k3s-agent-1 | .15 | k3s, k3s_agent | k3s worker |
| k3s_agent_2 | 115 | k3s-agent-2 | .16 | k3s, k3s_agent | k3s worker |

## Physical Devices (from devices.yml)

**Managed** (get DHCP + DNS + Ansible inventory):

| Name | IP | MAC | User | Roles | Notes |
|------|----|-----|------|-------|-------|
| steam | .12 | 58:47:ca:77:85:fd | root | proxmox_host | Proxmox 8 hypervisor |
| homeassistant | .5 | d8:3a:dd:cd:a8:b4 | hassio | iot, homeautomation | HA Yellow, HAOS (s6 init) |
| truenas | .44 | bc:24:11:00:35:85 | root | storage | Immutable /usr, node_exporter at /root/bin/ |
| gardener | .53 | 2c:cf:67:81:f4:03 | root | iot, gardener | Raspberry Pi, USB SDR, rtl_433 + moisture_proxy |
| panoptes | .61 | d8:3a:dd:f1:37:21 | root | rpi | Raspberry Pi 4B, Camera Module 3 (IMX708), RTSP streaming |

**Non-managed** (get DHCP + DNS only):

| Name | IP | MAC |
|------|----|-----|
| xt8-wap | .3 | 7c:10:c9:e4:a9:90 |
| linksys-iot | .32 | 60:38:e0:d0:65:78 |

### Physical Device Quirks

- **HomeAssistant**: Uses `hassio` user (not root). Runs s6-svscan init (Alpine-based, not systemd). node_exporter deployed as s6 longrun service at `/etc/s6-overlay/s6-rc.d/node-exporter/`. HA version 2026.3.2. Config managed via `ansible-homeassistant` role (YAML templates + Supervisor API for add-ons). Generic camera integrations must be added via config flow API, not YAML (YAML `camera: platform: generic` removed in modern HA).
- **TrueNAS**: Immutable `/usr` filesystem. node_exporter installed to `/root/bin/` instead of `/usr/local/bin/`.
- **Steam (Proxmox)**: PVE firewall requires explicit port rules for node_exporter. Rule in `/etc/pve/local/host.fw`: `IN ACCEPT -source 192.168.50.0/24 -p tcp -dport 9100`.
- **Gardener**: Raspberry Pi OS Bookworm (aarch64). USB RTL-SDR dongle. rtl_433 binary pre-compiled. Logrotate with `copytruncate` to handle open file handles. SD card — watch disk usage.
- **Panoptes**: Raspberry Pi 4B, Debian 13 (Trixie), aarch64. WiFi only (wlan0). Pi Camera Module 3 (IMX708). Camera mounted upside-down (hflip + vflip enabled). mediamtx v1.16.3 streams 1080p30 H264. PipeWire may grab the camera if a desktop session starts — mediamtx service should be running first.

## Tea Blend Studio (TBS) Deployment

Website for theteablendstudio.com, a Vite/React SPA. Deployed from a bare git repo on devbox, built and served via PM2 + `serve -s dist -l 3000`.

**Architecture**: Wife (Roseanna) pushes from her local machine → bare repo on devbox (`/srv/git/the-site.git`) → post-receive hook SSHes to manager → Ansible deploys to the target container.

**Workflow**:
- `git push origin master` → deploys to **preview-site** (CT 922, 192.168.50.22) → https://preview.theteablendstudio.com
- `git push origin master:production` → deploys to **production-site** (CT 997, 192.168.50.24) → https://theteablendstudio.com

**Post-receive hook** (`/srv/git/the-site.git/hooks/post-receive` on devbox):
- Detects pushes to `refs/heads/master` and `refs/heads/production`
- SSHes to manager and runs: `cd /root/projects/homelab-infra && ansible-playbook -i scripts/terraform_inventory.py ansible-tbs/configure.yml --limit <target> --skip-tags setup`
- Also mirrors to GitHub in parallel

**ansible-tbs role** (`tbs-web`):
- Setup-tagged tasks: NodeSource LTS install, PM2 + serve globally, SSH keypair generation, devbox registration
- Deploy tasks: git clone/pull, npm install, vite build, PM2 start/restart, PM2 save + startup
- `tbs_git_version` variable controls which branch to check out (default: `master`, production override: `production`)

## Panoptes Camera Streaming

Raspberry Pi 4B with Pi Camera Module 3, streaming via mediamtx v1.16.3.

**Streams available**:
- RTSP: `rtsp://192.168.50.61:8554/cam` — for VLC, Home Assistant, Frigate
- WebRTC: `http://192.168.50.61:8889/cam/` — low-latency browser viewing
- HLS: `http://192.168.50.61:8888/cam/` — browser-compatible, higher latency

**Home Assistant integration**: Camera added via config flow API (not YAML). Entity: `camera.panoptes`. Visible on the Cameras dashboard in the HA sidebar.

**ansible-panoptes role** (`rtsp-camera`):
- Installs rpicam-apps, creates mediamtx system user (in `video` group)
- Downloads mediamtx binary from GitHub releases
- Templates `mediamtx.yml` config (resolution, FPS, bitrate, codec, flip settings)
- Systemd service: `/etc/systemd/system/mediamtx.service`
- Defaults: 1920x1080, 30fps, 5Mbps, auto codec, hflip + vflip true (ceiling mount)

## Home Assistant Configuration

Fully Ansible-managed via `ansible-homeassistant`. Three roles:

**ha-config**: Templates YAML configuration files and pushes to HA via SSH. Uses custom Jinja delimiters (`[% %]` for variables, `[# #]` for blocks) to avoid conflict with HA's native `{{ }}` templating. After deploying, validates config via HA API (`/api/config/core/check_config`) then reloads.

**ha-addons**: Manages Supervisor add-ons via the Supervisor REST API — installs, configures, sets boot mode, starts.

**ha-backup**: Syncs HA backups to TrueNAS, deploys restore and trigger scripts.

**Dashboards** (YAML-mode, Ansible-managed, in sidebar):
- Battery Status — all device batteries by category
- Cameras — live RTSP feeds (panoptes)
- Climate — HVAC, temperature sensors, outdoor temp, tides, AC delta-T
- Internet — wired/WiFi ping RTT, packet loss, DNS resolution, jitter, uptime
- Plant Moisture — WH51 soil sensor readings with staleness tracking
- Websites — Tea Blend Studio preview/production status and version info

**Key config entries** (in `ha-config/defaults/main.yml`):
- HVAC scheduling with presence detection (near/far/home thresholds)
- WH51 soil moisture sensors via MQTT (14 sensors, rtl_433 → moisture_proxy → HA)
- Network monitoring via command_line sensors (ping, DNS, jitter, packet loss)
- Template sensors: outdoor temp average, AC delta-T, HVAC target mode, internet uptime
- Light groups, grow lamp automation, blind automation

## Gardener (192.168.50.53)

Raspberry Pi running two services that bridge RF sensors to Home Assistant via MQTT:

**rtl_433**: Listens on 915MHz via USB SDR, decodes Ecowitt/LaCrosse/etc RF signals, publishes to MQTT topics `rtl_433/gardener/devices/...` and `rtl_433/gardener/events`. Config at `/etc/rtl_433/rtl_433.conf`, logs to `/var/log/rtl_433/`. Logrotate configured with `copytruncate` (7 daily, max 100M each) to prevent disk fill.

**moisture_proxy**: Python script that subscribes to rtl_433 MQTT topics, filters Ecowitt WH51 soil moisture sensors, and publishes Home Assistant MQTT auto-discovery messages. Runs as `moistureproxy` user, installed at `/opt/moisture_proxy/`. MQTT config passed via systemd `Environment=` variables.

**Shared MQTT config**: `group_vars/all/mqtt.yml` defines `mqtt_broker`, `mqtt_port`, `mqtt_user`, `mqtt_pass`. All gardener templates reference these vars. Changing the MQTT broker = edit one file + `make gardener`. The playbook loads this via `vars_files` (dynamic inventory doesn't auto-load group_vars).

## Monitoring

**22+ Prometheus targets** (18 containers + 5 physical devices + Prometheus self-scrape):

node_exporter (:9100) on all containers and physical devices. Prometheus scrape config is generated from inventory by the monitoring role — new hosts auto-appear when added to inventory and the monitoring role is re-run.

**Grafana**: http://monitoring.homelab:3000

## Cloudflare Tunnels

| Tunnel resource | Container | Domain | Backend |
|----------------|-----------|--------|---------|
| ocsirb_staging | ocsirb-staging (.13) | staging.ocsirb.com | http://localhost:80 |
| preview_site | preview-site (.22) | preview.theteablendstudio.com | http://localhost:3000 |
| production_site | production-site (.24) | theteablendstudio.com + www | http://localhost:3000 |
| dolphin | dolphin (.34) | brisco.org.uk/marie | http://localhost:80 |

Convention: tunnel resource name = container key → cloudflared token lookup is `tunnel_tokens[container_key]`.

## Backup Strategy

**Proxmox vzdump** (deployed via `ansible-backup/backup.yml` targeting `proxmox_host`):
- Daily vzdump of all containers at 02:30 → `/mnt/truenas/backups/proxmox/`
- Retention script at 03:30: 3 daily, 2 weekly, 1 monthly
- Storage: TrueNAS NFS mount on the Proxmox host

**Offsite backup**: Discussed but not yet implemented. Plan: Backblaze B2 + restic for Immich photos/DB, Terraform state/secrets, container configs. B2 pricing: free ingress, $6/TB/mo storage, free egress up to 3x stored amount.

## Dynamic Inventory Groups

Generated by `scripts/terraform_inventory.py`:

- **containers** → all 18 container hostnames (children: k3s_cluster, tunnel_hosts)
- **physical_devices** → steam, homeassistant, truenas, gardener, panoptes
- **k3s_cluster** → k3s_server, k3s_agents
- **tunnel_hosts** → ocsirb-staging, preview-site, production-site, dolphin
- **proxmox_host** → steam
- Per-service groups: dns_hosts, management_hosts, development_hosts, monitoring_hosts, uptime_kuma_hosts, omada_hosts, photoprism_hosts, jupyter_hosts, inference_hosts, immich_hosts, ocsirb_web_hosts, ocsirb_staging_hosts, dolphin_hosts, web_hosts, k3s_hosts, storage_hosts, iot_hosts, homeautomation_hosts, gardener_hosts, rpi_hosts

## Playbook Usage

All playbooks run from `/root/projects/homelab-infra` on the manager. Use `make help` for full target list.

```bash
# Quick reference — most common operations:
make plan                # Terraform plan
make apply               # Terraform apply
make common              # base-packages + node_exporter on all hosts
make monitoring          # Prometheus + Grafana
make gardener            # rtl433 + moisture-proxy on gardener Pi
make homeassistant       # HA YAML config + add-ons + backup sync
make all-services        # Deploy all service roles
make backup              # Proxmox vzdump cron
make status              # Show all Prometheus targets

# Router (uses its own static inventory):
make router              # DHCP + DNS + static routes

# Roles not yet in Makefile (run manually):
ansible-playbook -i scripts/terraform_inventory.py ansible-dolphin/configure.yml
ansible-playbook -i scripts/terraform_inventory.py ansible-tbs/configure.yml
ansible-playbook -i scripts/terraform_inventory.py ansible-panoptes/configure.yml
```

## Secrets (gitignored)

| File | Contents |
|------|----------|
| secrets.auto.tfvars | proxmox_password, container_root_password, cloudflare_api_token |
| .vault_pass | Ansible vault password (referenced by ansible.cfg) |
| group_vars/all/homeassistant_vault.yml | ha_api_token (ansible-vault encrypted) |
| ansible-router/group_vars/all/secrets.yml | omada_username, omada_password |
| ansible-k3s/group_vars/all/vault.yml | proxmox_password, ansible_ssh_pass |

**Known plaintext credentials** (technical debt):
| File | Contents |
|------|----------|
| group_vars/all/mqtt.yml | mqtt_user, mqtt_pass (committed, should be vaulted) |
| ansible-dns/configure.yml | adguard_user, adguard_password (inline) |
| Monitoring role defaults | Grafana admin credentials (inline) |

## SSH Access

From outside the homelab:
```bash
ssh -i ~/.ssh/homelab root@192.168.50.28   # → manager
```
From manager to any container or device: direct SSH as root (key pre-deployed).

Manager key (deployed to all containers + all physical devices):
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJ6fA0xsXu+YMANF/JwmrfrzvRV7b7f8H6qWJF93hKLp george@IvorTheEngine
```

## Roadmap

### Phase 3 — Reproducibility ✅ COMPLETE

All items done: SSH key deployment, cloudflared role, node_exporter baseline (22+ targets), Prometheus + Grafana, Uptime Kuma, service roles for all containers, k8s manifest automation, Proxmox backup, legacy inventory cleanup, lxc-prep derives IDs from inventory, gardener integration, Makefile, README.

### Phase 2 — Security Hardening (deferred)

Orthogonal to Phase 3. The longer deferred, the more plaintext credentials accumulate.

- 2.1: Per-service passwords (replace single shared password)
- 2.2: ansible-vault encryption for all secrets files
- 2.3: Move inline credentials (AdGuard, Grafana, MQTT) to vault files
- 2.4: Proxmox API TLS (remove insecure=true)

### Phase 4 — Maturity (future)

- CI/CD pipeline (tflint, ansible-lint, GitHub Actions or local Drone)
- Auto-generated network diagram from inventory
- Prometheus alertmanager (container down, disk full, high CPU)
- Multi-host Proxmox support (add node field to locals map)
- Offsite backup with Backblaze B2 + restic

### Outstanding Items

- **Offsite backup** (3.7b): Backblaze B2 + restic role — discussed, approach agreed, not yet implemented
- **AdGuard memory**: Currently 256MB, should be bumped to 512MB in locals.containers (apt installs cause high load)
- **Makefile**: Missing targets for dolphin, tbs, panoptes
- **Panoptes monitoring**: Add to Prometheus scrape targets (`make monitoring`)
- **PipeWire conflict on panoptes**: Desktop sessions may grab the camera from mediamtx

## Provider Versions

- Terraform: >= 1.5
- bpg/proxmox: ~> 0.98
- cloudflare/cloudflare: ~> 4.0
- hashicorp/random: ~> 3.0
- Home Assistant: 2026.3.2
- AdGuard Home: v0.107.73
- Prometheus: 2.53.4
- Grafana: 12.4.1
- node_exporter: 1.8.2
- mediamtx: 1.16.3
- cloudflared: latest
- Immich: v2 (Docker)
- Uptime Kuma: latest (GitHub)
- Omada Controller: TP-Link .deb
