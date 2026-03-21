# homelab-infra — Audit Findings & Remediation Plan

> **Date:** March 2026 | **Scope:** Full project audit of `homelab-infra` (commit `6385c78`)
> **Owner:** George Brisco | **Infra:** Proxmox VE 8, Cloudflare Zero Trust, k3s, TP-Link Omada

---

## Project Context

The `homelab-infra` repository is a unified IaC project managing:

- **17 Proxmox LXC containers** via Terraform (`bpg/proxmox` provider v0.98)
- **13 Cloudflare resources** (3 tunnels, 3 tunnel configs, 4 DNS records, 3 random_passwords) via Terraform (`cloudflare/cloudflare` ~> 4.0)
- **3-node k3s cluster** (v1.34.5+k3s1) provisioned via Ansible (`ansible-k3s/`)
- **22 DHCP reservations** on TP-Link Omada router via Ansible (`ansible-router/`)
- **k8s manifests** (not yet deployed) in `manifests/`

Key infrastructure details:
- Proxmox host: `steam` at 192.168.50.12
- Manager LXC: 192.168.50.28 (runs Terraform and Ansible)
- AdGuard Home: 192.168.50.2 (static IP, local DNS resolver)
- k3s nodes: server .14, agents .15 and .16 (privileged LXC, native snapshotter)
- NFS storage: TrueNAS at 192.168.50.44 (`/mnt/MainPool/local_data/k8s`)
- Tailscale on Proxmox host injects 100.100.100.100 MagicDNS into containers
- Cloudflare tunnels serve ocsirb.com (staging) and theteablendstudio.com (preview + production)

### File Layout

```
homelab-infra/
├── main.tf                          # 17 containers + 13 Cloudflare resources (~1,200 lines)
├── variables.tf                     # Proxmox + Cloudflare variable declarations
├── proxmox.auto.tfvars              # Committed: endpoint, SSH key (stale header comments)
├── cloudflare.auto.tfvars           # Committed: zone IDs, account ID, domain names
├── secrets.auto.tfvars              # GITIGNORED: all passwords + Cloudflare API token (plaintext)
├── .gitignore
├── ansible-k3s/
│   ├── provision.yml                # 7-play k3s provisioning playbook
│   ├── inventory.ini                # GITIGNORED: static inventory with plaintext passwords
│   ├── group_vars/all/
│   │   └── main.yml                 # GITIGNORED: mixed config + secrets
│   └── roles/
│       ├── lxc-prep/                # Proxmox host-level LXC config + sysctls
│       ├── base/                    # /dev/kmsg symlink, packages, SSH config
│       ├── k3s-server/              # k3s server install + config template
│       ├── k3s-agent/               # k3s agent install + config template
│       ├── nfs-storage/             # NFS subdir external provisioner
│       └── kubeconfig/              # Fetch kubeconfig to manager
├── ansible-router/
│   ├── configure.yml                # Omada router DHCP/DNS automation
│   ├── group_vars/all/
│   │   ├── main.yml                 # Committed: 22 DHCP reservations, DNS, static routes
│   │   └── secrets.yml              # GITIGNORED: Omada credentials
│   └── roles/omada-router/
│       └── tasks/                   # auth, dhcp_reservations, static_routes, dns_servers, logout
└── manifests/
    └── portfolio/                   # Namespace, deployment, cronjob, PVC, Dockerfile, secret example
```

---

## 1. Security Findings

### 1.1 CRITICAL — Single shared password
`iSIhac1919!` is the Proxmox root password, every container's root password, and the Omada controller password. The Cloudflare API token is in the same secrets file. A single compromise exposes the entire infrastructure.

**Recommendation:** Rotate immediately. Generate unique per-service passwords. Store in Ansible Vault or SOPS.

### 1.2 CRITICAL — Plaintext secrets on disk
The k3s `inventory.ini` has `ansible_ssh_pass=iSIhac1919!` in plain text. The router `secrets.yml` has it in plain text. `secrets.auto.tfvars` has all passwords and the Cloudflare API token in plain text. Terraform state (`.tfstate`) contains Cloudflare tokens, tunnel secrets, and random_password values in plain text. None of this uses Ansible Vault, SOPS, or any encryption at rest.

**Recommendation:** Encrypt with ansible-vault or SOPS. Move Terraform state to an encrypted remote backend.

### 1.3 CRITICAL — SSH key mismatch
`proxmox.auto.tfvars` deploys the `mgmt-lxc` SSH key into every container, but the manager's actual key is `george@IvorTheEngine`. The Terraform-deployed key is useless. All access relies on the shared password.

**Recommendation:** Update `proxmox.auto.tfvars` with the manager's actual public key. Redeploy containers.

### 1.4 HIGH — PermitRootLogin yes baked in
The base Ansible role permanently enables root password login on every k3s node (`/etc/ssh/sshd_config.d/99-permit-root.conf`) as a workaround for the SSH key bug (1.3).

**Recommendation:** Fix the SSH key first (1.3), then remove password auth and use key-only.

### 1.5 HIGH — insecure = true on Proxmox provider
TLS certificate verification is disabled for the Proxmox API connection. A MITM on the LAN could intercept the Proxmox root password.

**Recommendation:** Generate a proper CA cert for Proxmox or pin the self-signed cert.

### 1.6 HIGH — Unencrypted local Terraform state
The `.tfstate` file on the manager contains all secrets in plain text. No encryption, versioning, locking, or backup.

**Recommendation:** Move to S3-compatible backend with encryption (e.g., MinIO on TrueNAS). See Phase 2.5.

---

## 2. Multiple Sources of Truth

This is the highest-impact structural problem. Every duplicated data point is a future inconsistency.

### 2.1 IP addresses defined in 4 places

| Location | What |
|----------|------|
| `main.tf` | AdGuard static IP (192.168.50.2) |
| `ansible-router/group_vars/all/main.yml` | All 22 DHCP reservations with IPs |
| `ansible-k3s/inventory.ini` | k3s node IPs hardcoded |
| `ansible-k3s/group_vars/all/main.yml` | `k3s_server_ip`, `nfs_server`, `proxmox_host_ip`, `manager_ip` |

Changing a DHCP reservation IP requires manually updating 2-4 files. Nothing enforces consistency.

### 2.2 Container IDs in 2 places
- `main.tf`: `vm_id` per resource
- `ansible-k3s/group_vars/all/main.yml`: `k3s_container_ids: [113, 114, 115]`

### 2.3 DNS servers in 3 places
- `main.tf`: `dns { servers = ["192.168.50.2", "9.9.9.9"] }` repeated in 16 container blocks
- `ansible-router/group_vars/all/main.yml`: `lan_primary_dns: "192.168.50.2"`
- AdGuard upstream config: `["1.1.1.1", "8.8.8.8"]`

### 2.4 Stale comments
`proxmox.auto.tfvars` header still references symlinks to deleted projects (`mgmt-infra/`, `monitoring-infra/`, `website-infra/`).

### Proposed Architecture: Single Inventory
The solution is a `locals { containers = { ... } }` map in Terraform defining every container's name, VM ID, template, cores, memory, disk, IP, MAC, and role tags. A single `for_each` resource iterates over this map. DNS servers become a local variable referenced once.

Terraform outputs export container IPs, IDs, and computed values as structured JSON. Ansible reads this via a dynamic inventory script (`terraform output -json | jq`). The k3s inventory and router DHCP reservations are both *derived* from the same map. Changing an IP = editing one line + `terraform apply` + `ansible-playbook`.

---

## 3. Terraform Structure

### 3.1 HIGH — 1,200-line monolithic main.tf
17 containers are hand-written individual resources with nearly identical boilerplate. No `for_each`, modules, or locals. The DNS block alone is repeated 16 times. Adding a container requires copying ~60 lines.

**Recommendation:** Refactor to locals map + `for_each`. Extract Cloudflare into a module.

### 3.2 HIGH — No Terraform outputs
Zero `output` blocks. Container IPs, tunnel tokens, and computed values are inaccessible without `terraform state show`. Makes Ansible integration impossible without manual steps.

**Recommendation:** Add outputs for all container IPs, k3s node IPs, tunnel tokens, and Cloudflare record IDs.

### 3.3 MODERATE — No remote state backend
State is a local file on the manager's disk. No locking, versioning, or backup.

**Recommendation:** Move to S3-compatible backend (MinIO on TrueNAS) with encryption.

### 3.4 MODERATE — lifecycle ignore_changes tech debt
- `ignore_changes = [operating_system, description]` on every container (import artefacts)
- `ignore_changes = [secret]` on tunnels (write-only attribute workaround)
- `random_password` resources are orphaned — their values aren't actually used by the tunnels

**Recommendation:** Clean up OS/description ignores. Document tunnel secret limitation. Remove unused `random_passwords` if tunnels are stable.

### 3.5 MODERATE — No required_version
The `terraform {}` block constrains provider versions but not the Terraform binary version.

**Recommendation:** Add `required_version = "~> 1.5"` (or current version).

### 3.6 LOW — Three .auto.tfvars with no clear pattern
`proxmox.auto.tfvars`, `cloudflare.auto.tfvars`, and `secrets.auto.tfvars` split config by provider but secrets overlap. The Omada password isn't here at all.

**Recommendation:** Consolidate to two files: committed config vars and gitignored secrets.

---

## 4. Ansible Gaps

### 4.1 HIGH — No unified inventory
k3s and router playbooks have completely separate inventories. No shared view of all hosts. Cannot run cross-cutting operations.

**Recommendation:** Create a single dynamic inventory derived from Terraform outputs.

### 4.2 HIGH — 12 of 17 containers unmanaged
Terraform creates empty shells. Nothing installs software in photoprism, immich, monitoring, jupyter, inference, devbox, etc. Loss of any container = full manual rebuild.

**Recommendation:** Create Ansible roles for each service, starting with the most critical (monitoring, Immich).

### 4.3 HIGH — Not idempotent from scratch
Fresh containers need manual `pct exec` for SSH access and password setup before Ansible can connect. Chicken-and-egg problem not addressed in any playbook.

**Recommendation:** Use Terraform provisioners or cloud-init to bootstrap SSH access on container creation.

### 4.4 MODERATE — kubeconfig role ordering bug
Play 7 creates `/root/.kube` directory but Play 4 (`k3s-server` role) writes the kubeconfig file there. First run on fresh provision fails.

**Recommendation:** Move directory creation into the `k3s-server` role before the file write.

### 4.5 MODERATE — group_vars mixes secrets and config
`ansible-k3s/group_vars/all/main.yml` contains both IPs/versions (should be tracked in git) and passwords (should be encrypted). The entire file is gitignored, so a fresh clone requires recreating it from the `.example` file.

**Recommendation:** Split into `main.yml` (committed: IPs, versions, paths) and `vault.yml` (encrypted with ansible-vault, committed).

### 4.6 LOW — Dead package installs
`fuse-overlayfs` is installed in the base role but unused (snapshotter changed to `native`).

**Recommendation:** Remove from base role package list.

### 4.7 LOW — NFS requires manual TrueNAS step
The NFS provisioner role has a `debug` task saying to SSH into TrueNAS and run `mkdir`. Not automated.

**Recommendation:** Add a TrueNAS API call or delegated task to create the NFS export.

---

## 5. Reproducibility Gaps

### 5.1 CRITICAL — Containers are pets, not cattle
Terraform recreates empty shells. Everything inside (installed software, configs, running services, data) is invisible to IaC. Any container loss = full manual rebuild of the service.

**Recommendation:** Create Ansible roles for each service. Document data directories for backup.

### 5.2 HIGH — No backup or recovery plan
Terraform state, Ansible files, and secrets all live on a single manager container. No documentation or automation for "manager is dead, how do I recover?"

**Recommendation:** Back up state to TrueNAS. Document bootstrap procedure. Store encrypted secrets in git.

### 5.3 HIGH — cloudflared not provisioned
Terraform defines tunnels in Cloudflare but nothing installs or configures the `cloudflared` daemon inside the tunnel containers (ocsirb-staging, preview-site, production-site).

**Recommendation:** Create an Ansible role that installs cloudflared, writes the credentials file, and starts the systemd service.

### 5.4 MODERATE — DHCP reservations one-way
Router playbook creates missing reservations but never removes stale ones. Omada controller drifts over time.

**Recommendation:** Add a reconciliation mode that removes reservations not in the config (with `--check` safety).

### 5.5 MODERATE — k8s manifests not applied
`manifests/` directory has namespace, deployment, CronJob, PVC but no automation applies them. Deployment references a placeholder image that doesn't exist.

**Recommendation:** Add a playbook step or ArgoCD to apply manifests. Set up a container registry for builds.

### 5.6 LOW — No documentation
No README explaining project structure, bootstrap order, or manual prerequisites.

**Recommendation:** Add a README with architecture diagram and bootstrap steps.

---

## 6. Remediation Roadmap

### Phase 1: Inventory & Datastore (Weeks 1–2)

**Goal:** Single source of truth for all infrastructure data, consumed by both Terraform and Ansible.

| Step | Action | Details | Effort | Deps |
|------|--------|---------|--------|------|
| 1.1 | Create locals container map | Define `locals { containers = { ... } }` in `main.tf` with name, vm_id, template, cores, memory, disk, ip, mac, role tags for all 17 containers. | 2–3 hrs | None |
| 1.2 | Refactor to for_each | Replace 17 hand-written `proxmox_virtual_environment_container` resources with a single `for_each` over the locals map. Move DNS servers to a local variable. | 3–4 hrs | 1.1 |
| 1.3 | Add Terraform outputs | Export container IPs, IDs, k3s node details, Cloudflare tunnel tokens, and all computed values as structured JSON. | 1 hr | 1.2 |
| 1.4 | Dynamic Ansible inventory | Write a script that calls `terraform output -json` and produces a valid Ansible inventory. Replace both static inventory files. | 2 hrs | 1.3 |
| 1.5 | Unify DHCP reservations | Derive router DHCP reservation list from the Terraform locals map (via outputs). Eliminate the manual list in router `group_vars`. | 1–2 hrs | 1.3 |
| 1.6 | Split group_vars | Separate k3s `group_vars` into committed config (`main.yml`: IPs, versions, paths) and encrypted `vault.yml` (passwords). Update `.gitignore`. | 1 hr | None |
| 1.7 | Clean stale comments | Remove obsolete symlink references from `proxmox.auto.tfvars` header. Add `required_version` to terraform block. | 15 min | None |

### Phase 2: Security Hardening (Weeks 2–3)

**Goal:** Eliminate the single-password problem and establish encrypted secret management.

| Step | Action | Details | Effort | Deps |
|------|--------|---------|--------|------|
| 2.1 | Fix SSH key deployment | Update `proxmox.auto.tfvars` with the manager's actual `george@IvorTheEngine` public key. Redeploy to all containers. | 30 min | Phase 1 |
| 2.2 | Remove PermitRootLogin yes | Once key auth works, remove the `99-permit-root.conf` creation from the base role. Deploy. | 30 min | 2.1 |
| 2.3 | Rotate passwords | Generate unique passwords for Proxmox, each service container, and Omada. Update all references. | 1–2 hrs | 2.1 |
| 2.4 | Encrypt all secrets | Move to ansible-vault for Ansible secrets and SOPS for Terraform. Remove plaintext secrets from disk. | 2 hrs | 2.3 |
| 2.5 | Remote Terraform backend | Set up MinIO on TrueNAS as S3-compatible backend. Migrate state with `terraform init -migrate-state`. | 2–3 hrs | 2.4 |
| 2.6 | Proxmox TLS | Generate a proper CA cert for Proxmox or pin the self-signed cert. Remove `insecure = true`. | 1 hr | None |

### Phase 3: Reproducibility & Maturity (Weeks 3–6)

**Goal:** Make every service reproducible from code and add operational tooling.

| Step | Action | Details | Effort | Deps |
|------|--------|---------|--------|------|
| 3.1 | Ansible role: cloudflared | Install cloudflared, write credentials, configure tunnel, start systemd service. Apply to tunnel containers. | 2–3 hrs | Phase 1 |
| 3.2 | Ansible roles: remaining services | Create roles for monitoring (Grafana/Prometheus), Immich, Photoprism, Jupyter, Inference, etc. Prioritise by criticality. | 2–4 hrs each | Phase 1 |
| 3.3 | Fix kubeconfig bug | Move `/root/.kube` directory creation into the `k3s-server` role, before the kubeconfig file write. | 15 min | None |
| 3.4 | Bootstrap automation | Use Terraform provisioners or cloud-init to set up SSH access on container creation. Eliminate `pct exec` manual steps. | 2–3 hrs | Phase 1 |
| 3.5 | k8s manifest deployment | Add ArgoCD or a playbook step that applies `manifests/`. Set up a container registry for builds. | 3–4 hrs | Phase 1 |
| 3.6 | Backup & recovery | Automate TrueNAS backup of Terraform state and critical container data directories. Document full bootstrap procedure. | 2–3 hrs | Phase 2 |
| 3.7 | CI/CD & linting | Add pre-commit hooks for `terraform validate`, `terraform fmt`, `ansible-lint`, `tflint`. | 1–2 hrs | None |
| 3.8 | README & documentation | Write a comprehensive README with architecture diagram, bootstrap steps, and manual prerequisites. | 2 hrs | Phase 1 |
| 3.9 | Clean up lifecycle ignores | Remove `ignore_changes` on `operating_system` and `description`. Document tunnel secret limitation. Evaluate removing orphaned `random_password` resources. | 1 hr | Phase 1 |

---

## Severity Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 6 |
| HIGH | 9 |
| MODERATE | 8 |
| LOW | 4 |

---

## Known Workarounds in Current State

These are workarounds applied during initial setup that should be revisited:

1. **`lifecycle { ignore_changes = [secret] }` on tunnels** — Imported tunnels don't have the write-only `secret` attribute in state. The `secret` value in HCL doesn't match reality.
2. **`lifecycle { ignore_changes = [operating_system, description] }` on containers** — Import drift artefact. OS template changes will be silently ignored.
3. **`random_password` resources** — Exist in state and config but their values aren't used by tunnels (because of `ignore_changes`). Orphaned dead weight.
4. **TBS production apex DNS uses `name = "theteablendstudio.com"`** — Cloudflare stores the full domain name in state, not `@`. Using `@` forces replacement.
5. **`terraform state push`** was used for `random_password` imports — These resources have `id = "none"` and can't be imported normally. State JSON was manually edited.
6. **Host-level sysctls for k3s** — `vm.overcommit_memory=1`, `kernel.panic=10`, `kernel.panic_on_oops=1` set on PVE host via `/etc/sysctl.d/99-k3s.conf`. Required because LXC containers have read-only `/proc/sys`.
7. **`/dev/kmsg` symlink** — Kubelet requires `/dev/kmsg` which doesn't exist in LXC. Symlinked to `/dev/console` and persisted via `/etc/rc.local`.
8. **`protect-kernel-defaults: true` in k3s config** — Tells kubelet to validate sysctl values rather than write them (which fails in LXC due to read-only `/proc/sys`).
