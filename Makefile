# homelab-infra Makefile — convenience targets for common operations
#
# Usage:
#   make plan              # Terraform plan
#   make apply             # Terraform apply
#   make <service>         # Deploy a service (e.g. make monitoring, make immich)
#   make all-services      # Deploy all service roles
#   make k8s               # Apply k8s manifests

INVENTORY = -i scripts/terraform_inventory.py
ANSIBLE   = ansible-playbook $(INVENTORY)

.PHONY: help plan apply inventory common tunnel monitoring uptime-kuma immich photoprism jupyter ocsirb-web ocsirb-staging omada dns router k3s k8s all-services backup status

help:
	@echo "Terraform:"
	@echo "  make plan           - terraform plan"
	@echo "  make apply          - terraform apply"
	@echo "  make inventory      - show dynamic inventory groups"
	@echo ""
	@echo "Ansible (service roles):"
	@echo "  make common         - node_exporter on all containers"
	@echo "  make tunnel         - cloudflared on tunnel containers"
	@echo "  make monitoring     - Prometheus + Grafana"
	@echo "  make uptime-kuma    - Uptime Kuma"
	@echo "  make immich         - Immich (Docker Compose)"
	@echo "  make photoprism     - PhotoPrism"
	@echo "  make jupyter        - Jupyter Notebook"
	@echo "  make ocsirb-web     - ocsirb-web Nginx sites"
	@echo "  make ocsirb-staging - ocsirb-staging Nginx"
	@echo "  make omada          - Omada Controller"
	@echo "  make dns            - AdGuard DNS rewrites"
	@echo "  make router         - Router DHCP/DNS/routes"
	@echo "  make k3s            - k3s cluster provision"
	@echo "  make k8s            - Apply k8s manifests"
	@echo "  make all-services   - Deploy all service roles"
	@echo ""
	@echo "Ops:"
	@echo "  make backup         - Proxmox vzdump all containers"
	@echo "  make status         - Show Prometheus targets status"

plan:
	terraform plan

apply:
	terraform apply

inventory:
	python3 scripts/terraform_inventory.py --list | python3 -m json.tool

# --- Service roles ---

common:
	$(ANSIBLE) ansible-common/configure.yml

tunnel:
	$(ANSIBLE) ansible-tunnel/configure.yml

monitoring:
	$(ANSIBLE) ansible-monitoring/configure.yml

uptime-kuma:
	$(ANSIBLE) ansible-uptime-kuma/configure.yml

immich:
	$(ANSIBLE) ansible-immich/configure.yml

photoprism:
	$(ANSIBLE) ansible-photoprism/configure.yml

jupyter:
	$(ANSIBLE) ansible-jupyter/configure.yml

ocsirb-web:
	$(ANSIBLE) ansible-ocsirb-web/configure.yml

ocsirb-staging:
	$(ANSIBLE) ansible-ocsirb-staging/configure.yml

omada:
	$(ANSIBLE) ansible-omada/configure.yml

dns:
	$(ANSIBLE) ansible-dns/configure.yml

router:
	ansible-playbook -i ansible-router/inventory.ini ansible-router/configure.yml

k3s:
	$(ANSIBLE) ansible-k3s/provision.yml

k8s:
	ansible-playbook ansible-k3s/apply-manifests.yml

all-services: common tunnel monitoring uptime-kuma immich photoprism jupyter ocsirb-web ocsirb-staging omada dns

# --- Ops ---

backup:
	ansible-playbook ansible-backup/backup.yml

status:
	@curl -s http://monitoring.homelab:9090/api/v1/targets | python3 -c "import json,sys; data=json.load(sys.stdin); [print(f\"  {t['labels'].get('instance','?'):30s} {t['health']}\") for t in data['data']['activeTargets']]" 2>/dev/null || echo "Cannot reach Prometheus"
