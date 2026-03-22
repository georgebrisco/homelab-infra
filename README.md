# homelab-infra

Infrastructure as Code for a single-node Proxmox homelab. Terraform provisions LXC containers and Cloudflare tunnels; Ansible configures every service from DNS to monitoring to photo management. A dynamic inventory script bridges the two tools — no static inventory files, no manual IP tracking.

## Quick Start

Everything runs from the **manager** container (192.168.50.28):

```bash
cd /root/projects/homelab-infra

# Provision or update containers
make plan
make apply

# Deploy a service (e.g. monitoring stack)
make monitoring

# Deploy everything
make all-services

# See all available targets
make help
```

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│  Proxmox VE 8 Host (steam, 192.168.50.12)                           │
│                                                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ adguard  │ │ manager  │ │monitoring│ │  immich  │ │ openclaw │  │
│  │  DNS .2  │ │  TF/Ans  │ │ Prom+Graf│ │  Docker  │ │ AI GW    │  │
│  │  CT 116  │ │  .28     │ │  .25     │ │  .20     │ │  .35     │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
│                                                                      │
│  20 LXC containers total, all defined in local.containers in main.tf │
│  + 5 physical devices defined in devices.yml                         │
└──────────────────────────────────────────────────────────────────────┘
         │
    ┌────┴────┐
    │ Gateway │  192.168.50.1 (TP-Link ER707-M2, managed via Omada at .27)
    └────┬────┘
         │
    ┌────┴────┐
    │ TrueNAS │  192.168.50.44 (NFS storage for backups, media, k8s PVCs)
    └─────────┘
```

## How It Works

### Single Source of Truth

The `local.containers` map in `main.tf` defines every LXC container — hostname, IP, resources, MAC, roles, mounts. Physical devices (Proxmox host, TrueNAS, Home Assistant, Raspberry Pis) live in `devices.yml`. Everything downstream is derived from these two sources.

### Dependency Chain

```
Edit main.tf / devices.yml  →  terraform apply  →  make <service>
```

The dynamic inventory script (`scripts/terraform_inventory.py`) reads Terraform state and `devices.yml` directly on every Ansible run. No cached inventory, no intermediate files. Container `roles` lists auto-generate Ansible host groups (e.g., role `immich` → group `immich_hosts`).

### Convention Over Configuration

Naming conventions replace mapping tables wherever possible:

- Terraform tunnel resource names match container keys → cloudflared token lookup is `tunnel_tokens[container_key]`
- Each playbook targets its service group → `ansible-immich/configure.yml` targets `immich_hosts`
- Shared config that spans multiple services (MQTT, HA tokens, Migadu API) lives in `group_vars/all/` — change once, reconfigure everywhere

## Containers

| Container | CT ID | IP | Service | Port |
|-----------|-------|-----|---------|------|
| adguard | 116 | .2 | AdGuard Home DNS | 53, 3000 |
| manager | 107 | .28 | Terraform + Ansible control | — |
| devbox | 104 | .23 | Dev environment, portfolio tracker | — |
| monitoring | 103 | .25 | Prometheus + Grafana | 9090, 3000 |
| uptime-kuma | 108 | .26 | Uptime Kuma | 3001 |
| omada | 109 | .27 | TP-Link Omada Controller | 8043 |
| photoprism | 100 | .29 | PhotoPrism (photos) | 2342 |
| jupyter | 105 | .30 | Jupyter Notebook | 8888 |
| inference | 106 | .31 | Marina Watch (YOLOv8 detection) | 8080 |
| immich | 111 | .20 | Immich (photos, Docker Compose) | 2283 |
| ocsirb-web | 110 | .10 | OCSIRB Nginx static sites | 80, 8080 |
| ocsirb-staging | 112 | .13 | OCSIRB staging + Cloudflare tunnel | 80 |
| dolphin | 117 | .34 | Dolphin React app + Cloudflare tunnel | 80 |
| preview-site | 922 | .22 | TBS preview + Cloudflare tunnel | 80 |
| production-site | 997 | .24 | TBS production + Cloudflare tunnel | 80 |
| k3s-server | 113 | .14 | k3s control plane | 6443 |
| k3s-agent-1 | 114 | .15 | k3s worker | — |
| k3s-agent-2 | 115 | .16 | k3s worker | — |
| openclaw | 118 | .35 | OpenClaw AI gateway | 443 |
| florida-ai | 918 | .36 | Florida AI website (not yet deployed) | 80 |

All containers get node_exporter on :9100, scraped by Prometheus.

### Physical Devices

| Device | IP | Role |
|--------|-----|------|
| steam (Proxmox host) | .12 | Hypervisor |
| homeassistant | .5 | Home Assistant Yellow |
| truenas | .44 | NFS storage |
| gardener | .53 | Raspberry Pi, RTL-SDR soil sensors |
| panoptes | .61 | Raspberry Pi, RTSP camera |
| hemera | .33 | Raspberry Pi 5, dual cameras, Hailo-8 AI |

## Playbooks

Each service has its own Ansible role and a `make` target. Run `make help` for the full list. Common examples:

```bash
make plan              # Terraform plan
make apply             # Terraform apply
make common            # Base packages + node_exporter on all hosts
make tunnel            # Cloudflared on tunnel containers
make monitoring        # Prometheus + Grafana
make homeassistant     # HA YAML config + add-ons + backup sync
make tbs               # Tea Blend Studio (preview + production)
make gardener          # rtl433 + moisture-proxy on gardener Pi
make panoptes          # RTSP camera streaming + timelapse
make openclaw          # OpenClaw AI gateway (Node.js + nginx TLS)
make router            # Router DHCP/DNS/routes (uses own static inventory)
make k3s               # k3s cluster provision
make all-services      # Deploy all service roles
make backup            # Proxmox vzdump all containers
make status            # Show Prometheus targets status
```

## Cloudflare Tunnels

Five Zero Trust tunnels expose services to the internet:

| Domain | Container | Backend |
|--------|-----------|---------|
| staging.ocsirb.com | ocsirb-staging | http://localhost:80 |
| preview.theteablendstudio.com | preview-site | http://localhost:80 |
| theteablendstudio.com (+ www) | production-site | http://localhost:80 |
| brisco.org.uk/marie | dolphin | http://localhost:80 |
| TBD (domain not purchased) | florida-ai | http://localhost:80 |

Tunnel tokens are stored as a sensitive Terraform output and injected into cloudflared by the tunnel playbook.

## Network

- **Subnet**: 192.168.50.0/24
- **Gateway**: 192.168.50.1 (TP-Link ER707-M2, managed by Omada Controller at .27:8043)
- **DNS**: AdGuard Home at 192.168.50.2 — all containers resolve `hostname.homelab` locally
- **NFS**: TrueNAS at 192.168.50.44
- **IoT**: 192.168.20.0/24 via static route to Linksys at 192.168.50.32

## Git Workflow

The repo exists in three locations:

1. **Manager** (canonical): `/root/projects/homelab-infra` on 192.168.50.28 — where Terraform and Ansible actually run
2. **GitHub** (offsite backup): https://github.com/georgebrisco/homelab-infra (private)
3. **Workstation** (local clone): for editing and pushing changes

The manager repo is a non-bare repository with `receive.denyCurrentBranch = updateInstead`, so pushes automatically update the working tree.

**Remote clone (from a workstation):**

```bash
git clone ssh://root@192.168.50.28/root/projects/homelab-infra
cd homelab-infra
```

**Day-to-day workflow:**

```bash
# Edit files locally or on the manager
git add <files>
git commit -m "description of change"
git push origin master
```

Pushing to `origin master` updates the manager's working copy in-place. You can then SSH to the manager and run `make apply` / `make <service>` to deploy.

**GitHub mirror** (private): https://github.com/georgebrisco/homelab-infra. Push with `git push github master` if a github remote is configured, or push from the manager.

**Tea Blend Studio deployment** uses a separate push-to-deploy workflow. Roseanna pushes to a bare repo on the devbox (`/srv/git/the-site.git`), and a post-receive hook SSHes to the manager to run the TBS Ansible playbook. Pushing to `master` deploys to preview; pushing to `production` deploys to production.

## Secrets

Sensitive files are gitignored. Copy the examples and fill in values:

```bash
cp secrets.auto.tfvars.example secrets.auto.tfvars
# Edit: proxmox_password, container_root_password, cloudflare_api_token

cp ansible-router/group_vars/all/secrets.yml.example ansible-router/group_vars/all/secrets.yml
# Edit: omada_username, omada_password

cp ansible-k3s/group_vars/all/main.yml.example ansible-k3s/group_vars/all/vault.yml
# Edit: proxmox_password, ansible_ssh_pass
```

Ansible vault is used for Home Assistant and Migadu API tokens (`group_vars/all/homeassistant_vault.yml`, `group_vars/all/migadu_vault.yml`). The vault password file is `.vault_pass` (gitignored), referenced in `ansible.cfg`.

## Disaster Recovery

### If a single container is lost

Terraform still has the container definition in state. Re-create it and run the service playbook:

```bash
terraform apply                    # Recreates the container
make <service>                     # Converges all service config
```

For containers with persistent data (Immich, PhotoPrism, devbox), data lives on TrueNAS NFS mounts and survives container recreation.

### If the Proxmox host is lost

1. **Reinstall Proxmox VE 8** on the host, restore the hostname `steam` and IP 192.168.50.12.
2. **Restore TrueNAS** from ZFS (data is on a separate physical device).
3. **Mount NFS shares** on the Proxmox host:
   - `/mnt/truenas` → `192.168.50.44:/mnt/MainPool/local_data`
   - `/mnt/truenas-media` → `192.168.50.44:/mnt/MainPool/media`
4. **Download LXC templates** — Ubuntu 22.04 and 24.04 via the Proxmox UI.
5. **Bootstrap a manager LXC** (CT 107):
   - Create an Ubuntu 22.04 container manually via Proxmox UI with IP 192.168.50.28.
   - Run `bootstrap-mgmt-lxc.sh` inside it to install Terraform, Ansible, and Git.
   - Clone the repo from GitHub (the offsite backup):
     ```bash
     git clone https://github.com/georgebrisco/homelab-infra /root/projects/homelab-infra
     ```
6. **Populate secrets** on the manager:
   ```bash
   cd /root/projects/homelab-infra
   cp secrets.auto.tfvars.example secrets.auto.tfvars    # fill in passwords + CF token
   cp ansible-router/group_vars/all/secrets.yml.example ansible-router/group_vars/all/secrets.yml
   echo "your-vault-password" > .vault_pass
   ```
7. **Import existing containers** or create fresh ones:
   ```bash
   terraform init
   terraform apply                    # Creates all 20 containers
   ```
8. **Deploy all services**:
   ```bash
   make common                        # Base packages + node_exporter
   make all-services                  # All service roles
   make router                        # DHCP reservations + DNS
   make backup                        # Re-enable vzdump cron
   ```

### Backups

Proxmox vzdump runs daily at 02:30 (deployed via `make backup`). All containers are backed up to `/mnt/truenas/backups/proxmox/` on TrueNAS NFS. A retention script at 03:30 keeps 3 daily, 2 weekly, and 1 monthly backup.

Offsite backup (Backblaze B2 + restic) is planned but not yet implemented.

### Recovery context

The `CONTEXT.md` file contains comprehensive project state — network layout, container details, service configuration, credentials, and operational notes. It is designed to be fed to an LLM for assisted recovery or onboarding.

## Project Structure

```
homelab-infra/
├── main.tf                          # All 20 containers + 5 Cloudflare tunnels
├── outputs.tf                       # Outputs consumed by Ansible inventory
├── variables.tf                     # Variable declarations
├── *.auto.tfvars                    # Proxmox, Cloudflare, and secret values
├── devices.yml                      # Physical devices (Proxmox host, TrueNAS, HA, Pis)
├── CONTEXT.md                       # Full project context for LLM continuity
├── bootstrap-mgmt-lxc.sh           # One-time manager container setup script
├── homelab-infra-audit.md          # Infrastructure audit and remediation roadmap
├── Makefile                         # Convenience targets (make help for full list)
├── ansible.cfg                      # vault_password_file = .vault_pass
├── scripts/
│   └── terraform_inventory.py       # Dynamic Ansible inventory from TF state + devices.yml
├── group_vars/all/                  # Shared vars: MQTT, HA tokens, Migadu API key
├── ansible-common/                  # Base packages + node_exporter on all hosts
├── ansible-tunnel/                  # Cloudflared on tunnel containers
├── ansible-monitoring/              # Prometheus + Grafana
├── ansible-uptime-kuma/             # Uptime Kuma
├── ansible-immich/                  # Immich (Docker Compose)
├── ansible-photoprism/              # PhotoPrism
├── ansible-jupyter/                 # Jupyter Notebook
├── ansible-inference/               # Marina Watch (YOLOv8 detection dashboard)
├── ansible-ocsirb-web/              # OCSIRB Nginx static sites
├── ansible-ocsirb-staging/          # OCSIRB staging site
├── ansible-dolphin/                 # Dolphin React app
├── ansible-tbs/                     # Tea Blend Studio (preview + production)
├── ansible-openclaw/                # OpenClaw AI gateway (Node.js + nginx TLS)
├── ansible-florida-ai/              # Florida AI site (React/Vite + nginx)
├── ansible-hemera/                  # Hemera Pi 5 (dual cameras + Hailo-8 detection)
├── ansible-panoptes/                # RTSP camera streaming + timelapse
├── ansible-gardener/                # rtl433 + moisture-proxy (Raspberry Pi)
├── ansible-homeassistant/           # Home Assistant YAML config + add-ons + backup
├── ansible-migadu/                  # Migadu email (mailboxes, aliases, rewrites)
├── ansible-omada/                   # TP-Link Omada Controller
├── ansible-dns/                     # AdGuard Home DNS rewrites
├── ansible-router/                  # Router DHCP, DNS, static routes (own inventory)
├── ansible-k3s/                     # k3s cluster bootstrap (7-play provision)
├── ansible-k8s/                     # k8s manifest application
├── ansible-backup/                  # Proxmox vzdump to TrueNAS
├── florida-ai-site/                 # Florida AI website source (React/Vite)
└── manifests/                       # Kubernetes manifests (namespaces, deployments, PVCs)
```

## Requirements

- Terraform >= 1.5
- Ansible (with Python3 + PyYAML on manager)
- SSH key access from manager to all containers and physical devices
- Proxmox VE 8.x
- Providers: bpg/proxmox ~> 0.98, cloudflare/cloudflare ~> 4.0, hashicorp/random ~> 3.0
