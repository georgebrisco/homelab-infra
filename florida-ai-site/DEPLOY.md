# Florida AI — Deployment Guide

## Prerequisites
- Domain purchased and added to Cloudflare
- Cloudflare zone ID for the domain
- homelab-infra repo synced to manager

## Step 1: Add Terraform config

Add the following to `main.tf` in the `local.containers` map:

```hcl
    florida_ai = {
      vm_id       = 918
      hostname    = "florida-ai"
      template    = local.ubuntu_template
      os_type     = "ubuntu"
      cores       = 1
      memory      = 512
      swap        = 0
      disk_gb     = 4
      reserved_ip = "192.168.50.36"
      mac         = ""
      static      = false
      privileged  = false
      tags        = ["florida-ai", "website"]
      mounts      = []
      firewall    = false
      console     = false
      dns         = local.dns_servers_default
      roles       = ["florida_ai", "tunnel"]
    }
```

Add to `variables.tf`:

```hcl
variable "florida_ai_domain" {
  description = "Domain for Florida AI"
  type        = string
}

variable "florida_ai_zone_id" {
  description = "Cloudflare zone ID for Florida AI domain"
  type        = string
}
```

Add the tunnel resources to the end of `main.tf` (see terraform-additions.tf in this directory).

Add domain and zone_id to your tfvars.

## Step 2: Terraform apply

```bash
ssh root@192.168.50.28
cd /root/projects/homelab-infra
git pull
terraform plan
terraform apply
```

## Step 3: Provision with Ansible

```bash
# Common base packages
ansible-playbook -i scripts/terraform_inventory.py ansible-common/configure.yml --limit florida_ai_hosts

# Nginx for the site
ansible-playbook -i scripts/terraform_inventory.py florida-ai-infra/ansible/configure.yml

# Cloudflared tunnel
ansible-playbook -i scripts/terraform_inventory.py ansible-tunnel/configure.yml --limit florida_ai_hosts
```

## Step 4: Build and deploy the site

From your Windows machine (or devbox):

```bash
# Build
cd ai-consulting-site
npm run build

# Deploy to container
scp -r build/* root@192.168.50.35:/var/www/florida-ai/
```

## Step 5: Verify

Visit your domain — should show the Florida AI site served via Cloudflare tunnel.

## Redeploying after changes

```bash
npm run build
scp -r build/* root@192.168.50.35:/var/www/florida-ai/
```

Or set up a git push-to-deploy hook (see hooks/ in website-infra for the pattern).
