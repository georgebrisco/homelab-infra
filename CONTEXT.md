# homelab-infra — Project Context

> Feed this file to an LLM to resume work on this project.
> Last updated: 2026-03-13 (after Phase 3.3 monitoring stack).

## Overview

Single Git repository managing a homelab running on one Proxmox VE host (`steam`, 192.168.50.12). All infrastructure is defined as code: Terraform provisions LXC containers and Cloudflare tunnels; Ansible configures the router, DNS, and k3s cluster. A dynamic inventory script bridges the two — it reads `terraform output -json` directly (no cache file) and merges in physical devices from `devices.yml`.

**Manager node**: 192.168.50.28 (LXC container `manager`, CT 107). All Terraform and Ansible runs happen here. The repo lives at `/root/projects/homelab-infra`.

## Architecture Principles

1. **Single source of truth**: The `local.containers` map in `main.tf` defines every Proxmox container. `devices.yml` defines non-Proxmox devices. Everything else is derived.
2. **Dependency chain**: Edit locals → `terraform apply` → `ansible-playbook -i scripts/terraform_inventory.py <playbook>`. The inventory script calls Terraform state directly — no intermediate cache.
3. **DNS-first**: All inter-service communication uses `hostname.homelab` names resolved by AdGuard Home (192.168.50.2). Applications should never hardcode IPs.
4. **Convention over configuration**: Naming conventions and standardisation are preferred over mapping tables, complex scripts, or extra config. If two things need to relate to each other, they should share the same name (e.g., tunnel resource names match container keys).
5. **Role-based grouping**: Each container has a `roles` list. The inventory script auto-generates Ansible groups from these (e.g., role `media` → group `media_hosts`). Special roles `k3s_server`, `k3s_agent`, and `tunnel` map to dedicated groups.

## Network

- Subnet: 192.168.50.0/24
- Gateway/Router: 192.168.50.1 (TP-Link ER707-M2, managed via Omada Controller at 192.168.50.27:8043)
- DNS: AdGuard Home at 192.168.50.2 (CT 116, static IP)
- NFS: TrueNAS at 192.168.50.44 (physical, path `/mnt/MainPool/local_data/k8s`)
- IoT subnet: 192.168.20.0/24 via static route to Linksys at 192.168.50.32

## Git History

```
f83849f Phase 3.3: Prometheus + Grafana monitoring stack role
318a2b4 Rename tunnel resources to match container keys
d449bc5 Phase 3.1: cloudflared deployment role
a2fc04b Phase 3.0: Fix SSH access - deploy manager key to all containers
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
├── secrets.auto.tfvars              # [gitignored] proxmox_password, container_root_password, cloudflare_api_token
├── secrets.auto.tfvars.example      # Template for secrets
├── devices.yml                      # Non-Proxmox devices (physical hosts + unmanaged network gear)
├── scripts/
│   └── terraform_inventory.py       # Dynamic Ansible inventory (reads TF state + devices.yml)
├── ansible-tunnel/
|   |- configure.yml                # Playbook: deploy cloudflared to tunnel_hosts
|   +- roles/cloudflared/tasks/main.yml
|- ansible-common/
|   |- configure.yml                # Playbook: deploy node_exporter to all containers
|   +- roles/node-exporter/{tasks,handlers}/main.yml
|- ansible-monitoring/
|   |- configure.yml                # Playbook: deploy Prometheus + Grafana
|   +- roles/{prometheus,grafana}/{tasks,handlers,templates}/
|- ansible-dns/
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
| uptime_kuma | 108 | uptime-kuma | .26 | uptime_kuma | |
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
| cloudflare_tunnels | Tunnel IDs for ocsirb_staging, tbs_preview, tbs_production | Reference |
| cloudflare_tunnel_tokens | Tunnel tokens (sensitive) for cloudflared auth | ansible-tunnel playbook |
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

cloudflared is deployed via `ansible-playbook -i scripts/terraform_inventory.py ansible-tunnel/configure.yml`. Tokens come from the `cloudflare_tunnel_tokens` Terraform output.

## Playbook Usage

All playbooks run from `/root/projects/homelab-infra` on the manager:

```bash
# Router: DHCP reservations + DNS servers + static routes
ansible-playbook -i ansible-router/inventory.ini ansible-router/configure.yml

# DNS: Push hostname.homelab rewrites to AdGuard Home
ansible-playbook -i scripts/terraform_inventory.py ansible-dns/configure.yml

# Common baseline: node_exporter on all containers
ansible-playbook -i scripts/terraform_inventory.py ansible-common/configure.yml

# Monitoring: Prometheus + Grafana on monitoring_hosts
ansible-playbook -i scripts/terraform_inventory.py ansible-monitoring/configure.yml

# Tunnels: Deploy/update cloudflared on tunnel containers
ansible-playbook -i scripts/terraform_inventory.py ansible-tunnel/configure.yml

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
7. **cloudflared deployment roles**: ~~DONE~~ ansible-tunnel role deploys and configures cloudflared from Terraform tokens.
8. **Service deployment roles**: Monitoring stack ~~DONE~~ (Prometheus + Grafana). Remaining: Immich, PhotoPrism, Jupyter, Inference, Uptime Kuma — all manually configured.
9. **k8s manifests not in CI/CD**: manifests/ directory exists but isn't applied automatically.
10. **No backup strategy**: No automated backups of Proxmox, TrueNAS, or application data.
11. **lxc-prep role uses hardcoded k3s_container_ids**: Should derive from inventory group membership (k3s_cluster group) instead. Fix when k3s playbook is next run with dynamic inventory.
12. **Legacy ansible-k3s/inventory.ini**: Still exists (gitignored). Delete once dynamic inventory is confirmed working with k3s playbook.

## Roadmap

### Phase 3 — Reproducibility (in progress)

Completed:
- 3.0: SSH key deployment to all containers + Proxmox host
- 3.1: cloudflared role (convention-based: tunnel resource name = container key)
- 3.2: node_exporter baseline on all 17 containers (:9100)
- 3.3: Prometheus + Grafana monitoring stack (scrape targets from inventory)

Remaining:
- **3.4: Uptime Kuma role** — Install and configure Uptime Kuma on the uptime_kuma_hosts group. Low complexity; likely a Docker or direct install with a systemd unit.
- **3.5: Service roles for remaining containers** — Each container that runs a manually-configured service needs an Ansible role so it can be rebuilt from scratch. Priority order by pain-to-rebuild: Immich (Docker-based, needs DB + ML), PhotoPrism (community script, privileged container), Inference (model serving), Jupyter (notebook server). Some of these may be simple "install package + template config" roles; others (Immich) are Docker Compose deployments.
- **3.6: k8s manifest automation** — The manifests/ directory contains portfolio app resources (namespace, deployment, cronjob, PVC, secrets). Currently applied manually with kubectl. Options: (a) Ansible role that runs kubectl apply, (b) Flux/ArgoCD for GitOps, (c) simple script. Flux is likely overkill for one app; a role or Makefile is more appropriate.
- **3.7: Backup strategy** — Automate backups at three levels: (a) Proxmox container snapshots (vzdump on cron), (b) TrueNAS dataset snapshots (already has ZFS snapshots, may just need retention policy), (c) Application-level backups (Grafana dashboards, Immich DB, k8s etcd). A daily cron on the Proxmox host for vzdump, plus an Ansible role to configure snapshot policies.
- **3.8: Delete legacy ansible-k3s/inventory.ini** — Confirm dynamic inventory works with k3s playbook, then remove the old static inventory.
- **3.9: Fix lxc-prep role** — Derive k3s_container_ids from inventory group membership instead of the hardcoded list from Terraform output. The k3s_cluster group already has the right hosts; the role just needs to look up their vm_id host var.

### Phase 2 — Security Hardening (deferred)

Can be done at any time; does not block Phase 3. The longer it's deferred, the more plaintext credentials accumulate in new roles.

- **2.1: Per-service passwords** — Replace single shared password with unique passwords per credential scope (Proxmox root, container root, Omada, AdGuard, Grafana, etc.).
- **2.2: ansible-vault encryption** — Encrypt all vault/secrets files with ansible-vault. Store vault password in ~/.vault_pass outside the repo. Optionally un-gitignore encrypted files for version history.
- **2.3: Move AdGuard + Grafana credentials to vault files** — Currently inline in playbooks. Move to encrypted group_vars.
- **2.4: Proxmox API TLS** — Generate proper cert, install on Proxmox, remove insecure=true from provider config.
- **2.5: (Rejected) Remote Terraform backend** — Decided against. The locals map contains all vm_ids so state is recoverable via terraform import. Keeping DR simple: git + known vm_ids = recovery.

### Phase 4 — Maturity (future)

- **CI/CD pipeline** — Lint Terraform (tflint/terraform validate), lint Ansible (ansible-lint), run on push. Could be a simple GitHub Actions workflow or a local Drone/Gitea CI on the devbox.
- **Documentation** — Auto-generate network diagram from inventory. README with quickstart for new contributors (i.e., future George).
- **Alerting** — Prometheus alertmanager rules for container down, disk full, high CPU. Route to email or push notification.
- **Multi-host Proxmox** — If a second Proxmox node is added, the locals map needs a node field per container. The for_each and inventory script would need minor updates.

### Design Principles

1. **Single source of truth**: local.containers in main.tf for Proxmox resources; devices.yml for everything else. All downstream config is derived.
2. **Dependency chain**: Edit locals -> terraform apply -> ansible-playbook. Inventory reads TF state directly.
3. **DNS-first**: Inter-service communication uses hostname.homelab. No hardcoded IPs in application config.
4. **Convention over configuration**: Naming conventions preferred over mapping tables. If two things relate, they share a name (tunnel resource = container key, role name = inventory group).
5. **Role-based grouping**: Container roles auto-generate Ansible groups. Role name = service identity, not a category.

## Provider Versions

- Terraform: >= 1.5
- bpg/proxmox: ~> 0.98
- cloudflare/cloudflare: ~> 4.0
- hashicorp/random: ~> 3.0
- AdGuard Home: v0.107.73
- Prometheus: 2.53.4
- Grafana: 12.4.1
- node_exporter: 1.8.2
- cloudflared: 2026.3.0
