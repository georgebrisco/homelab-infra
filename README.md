# homelab-infra

Infrastructure as Code for a single-node Proxmox homelab. Terraform provisions LXC containers and Cloudflare tunnels; Ansible configures every service from DNS to monitoring to photo management. A dynamic inventory script bridges the two tools — no static inventory files, no manual IP tracking.

## Quick Start

Everything runs from the **manager** container (192.168.50.28):

```bash
cd /root/projects/homelab-infra

# Provision or update containers
terraform plan
terraform apply

# Deploy a service (e.g. monitoring stack)
ansible-playbook -i scripts/terraform_inventory.py ansible-monitoring/configure.yml
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Proxmox VE Host (steam, 192.168.50.12)                     │
│                                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ adguard  │ │ manager  │ │monitoring│ │  immich  │  ...   │
│  │  DNS     │ │  TF/Ans  │ │ Prom+Graf│ │  Docker  │       │
│  │  .2      │ │  .28     │ │  .25     │ │  .20     │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│                                                              │
│  17 LXC containers total, all defined in main.tf             │
└─────────────────────────────────────────────────────────────┘
         │
    ┌────┴────┐
    │ Gateway │  192.168.50.1 (TP-Link ER707-M2)
    └────┬────┘
         │
    ┌────┴────┐
    │ TrueNAS │  192.168.50.44 (NFS storage)
    └─────────┘
```

## How It Works

### Single Source of Truth

The `local.containers` map in `main.tf` defines every LXC container — hostname, IP, resources, roles, mounts. Physical devices live in `devices.yml`. Everything downstream is derived from these two sources.

### Dependency Chain

```
Edit main.tf  →  terraform apply  →  ansible-playbook -i scripts/terraform_inventory.py <playbook>
```

The dynamic inventory script (`scripts/terraform_inventory.py`) reads Terraform state directly on every run. No cached inventory, no intermediate files.

### Convention Over Configuration

Naming conventions replace mapping tables wherever possible:

- Terraform tunnel resource names match container keys → cloudflared token lookup is `tunnel_tokens[container_key]`
- Container `roles` list auto-generates Ansible host groups → role `immich` creates group `immich_hosts`
- Each playbook targets its service group → `ansible-immich/configure.yml` targets `immich_hosts`

## Containers

| Container | IP | Service | Port |
|-----------|-----|---------|------|
| adguard | .2 | AdGuard Home DNS | 53, 3000 |
| manager | .28 | Terraform + Ansible control | — |
| devbox | .23 | Development environment | — |
| monitoring | .25 | Prometheus + Grafana | 9090, 3000 |
| uptime-kuma | .26 | Uptime Kuma | 3001 |
| omada | .27 | TP-Link Omada Controller | 8043 |
| photoprism | .29 | PhotoPrism (photos) | 2342 |
| jupyter | .30 | Jupyter Notebook | 8888 |
| inference | .31 | ML serving (placeholder) | — |
| immich | .20 | Immich (photos, Docker) | 2283 |
| ocsirb-web | .10 | Nginx static sites | 80, 8080 |
| ocsirb-staging | .13 | Staging site + Cloudflare tunnel | 80 |
| preview-site | .22 | Preview site + Cloudflare tunnel | 3000 |
| production-site | .24 | Production site + Cloudflare tunnel | 3000 |
| k3s-server | .14 | k3s control plane | 6443 |
| k3s-agent-1 | .15 | k3s worker | — |
| k3s-agent-2 | .16 | k3s worker | — |

All containers get node_exporter on :9100, scraped by Prometheus.

## Playbooks

Each service has its own playbook directory with an Ansible role. All use the dynamic inventory:

```bash
# Baseline (node_exporter on all containers)
ansible-playbook -i scripts/terraform_inventory.py ansible-common/configure.yml

# Cloudflared tunnels
ansible-playbook -i scripts/terraform_inventory.py ansible-tunnel/configure.yml

# Per-service playbooks
ansible-playbook -i scripts/terraform_inventory.py ansible-monitoring/configure.yml
ansible-playbook -i scripts/terraform_inventory.py ansible-uptime-kuma/configure.yml
ansible-playbook -i scripts/terraform_inventory.py ansible-immich/configure.yml
ansible-playbook -i scripts/terraform_inventory.py ansible-photoprism/configure.yml
ansible-playbook -i scripts/terraform_inventory.py ansible-jupyter/configure.yml
ansible-playbook -i scripts/terraform_inventory.py ansible-ocsirb-web/configure.yml
ansible-playbook -i scripts/terraform_inventory.py ansible-ocsirb-staging/configure.yml
ansible-playbook -i scripts/terraform_inventory.py ansible-omada/configure.yml
ansible-playbook -i scripts/terraform_inventory.py ansible-dns/configure.yml

# Router (uses its own static inventory — runs against localhost + Omada API)
ansible-playbook -i ansible-router/inventory.ini ansible-router/configure.yml

# k3s cluster (full bootstrap: lxc-prep → base → server → agents → NFS → kubeconfig)
ansible-playbook -i scripts/terraform_inventory.py ansible-k3s/provision.yml
```

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

## Cloudflare Tunnels

Three Zero Trust tunnels expose services to the internet:

| Domain | Container | Backend |
|--------|-----------|---------|
| staging.ocsirb.com | ocsirb-staging | http://localhost:80 |
| preview.theteablendstudio.com | preview-site | http://localhost:3000 |
| theteablendstudio.com | production-site | http://localhost:3000 |

Tunnel tokens are stored as a sensitive Terraform output and injected into cloudflared by the tunnel playbook.

## Network

- **Subnet**: 192.168.50.0/24
- **Gateway**: 192.168.50.1 (TP-Link ER707-M2, managed by Omada Controller)
- **DNS**: AdGuard Home at 192.168.50.2 — all containers resolve `hostname.homelab` locally
- **NFS**: TrueNAS at 192.168.50.44
- **IoT**: 192.168.20.0/24 via static route to Linksys at 192.168.50.32

## Disaster Recovery

No remote Terraform backend by design — keeping DR simple. Recovery plan:

1. Reinstall Proxmox, restore TrueNAS from ZFS
2. `git clone` this repo onto a fresh manager container
3. Populate `secrets.auto.tfvars` (passwords + Cloudflare token)
4. `terraform import` each container using the vm_ids listed in `main.tf`
5. Run playbooks to converge all service config

The `CONTEXT.md` file contains full project state for LLM-assisted recovery.

## Project Structure

```
homelab-infra/
├── main.tf                     # All 17 containers + 3 Cloudflare tunnels
├── outputs.tf                  # Outputs consumed by Ansible inventory
├── variables.tf                # Variable declarations
├── *.auto.tfvars               # Proxmox, Cloudflare, and secret values
├── devices.yml                 # Physical devices (Proxmox host, TrueNAS, HA)
├── CONTEXT.md                  # Full project context for LLM continuity
├── scripts/
│   └── terraform_inventory.py  # Dynamic Ansible inventory from TF state
├── ansible-common/             # node_exporter on all containers
├── ansible-tunnel/             # cloudflared on tunnel containers
├── ansible-monitoring/         # Prometheus + Grafana
├── ansible-uptime-kuma/        # Uptime Kuma
├── ansible-immich/             # Immich (Docker Compose)
├── ansible-photoprism/         # PhotoPrism
├── ansible-jupyter/            # Jupyter Notebook
├── ansible-ocsirb-web/         # Nginx static sites
├── ansible-ocsirb-staging/     # Nginx staging site
├── ansible-omada/              # TP-Link Omada Controller
├── ansible-dns/                # AdGuard Home DNS rewrites
├── ansible-router/             # Router DHCP, DNS, static routes
├── ansible-k3s/                # k3s cluster bootstrap
└── manifests/                  # Kubernetes manifests (applied manually)
```

## Requirements

- Terraform >= 1.5
- Ansible (with Python3 + PyYAML on manager)
- SSH key access to all containers
- Proxmox VE 8.x
- Providers: bpg/proxmox ~> 0.98, cloudflare/cloudflare ~> 4.0
