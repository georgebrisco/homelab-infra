#!/bin/bash
# bootstrap-mgmt-lxc.sh
# ──────────────────────────────────────────────────────────────────────────────
# Run this once inside a fresh Ubuntu 22.04 LXC to set up your management node.
# Installs: Terraform, Ansible, Git, and a few useful extras (jq, ssh client).
#
# Usage (paste into the Proxmox LXC console):
#   curl -fsSL https://raw.githubusercontent.com/your-repo/bootstrap-mgmt-lxc.sh | bash
# Or if you copy-paste it directly:
#   bash bootstrap-mgmt-lxc.sh
# ──────────────────────────────────────────────────────────────────────────────

set -euo pipefail  # Exit on error, undefined var, or failed pipe

# Colour helpers for readable output
GREEN='\033[0;32m'; BLUE='\033[0;34m'; NC='\033[0m'
info()    { echo -e "${BLUE}[→]${NC} $1"; }
success() { echo -e "${GREEN}[✓]${NC} $1"; }

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Management LXC Bootstrap"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

###############################################################################
# 1. System update
###############################################################################
info "Updating system packages..."
apt-get update -qq && apt-get upgrade -y -qq
success "System up to date"

###############################################################################
# 2. Essential tools
###############################################################################
info "Installing essential tools (git, curl, jq, unzip, ssh)..."
# jq is great for working with Terraform JSON output
apt-get install -y -qq \
  git \
  curl \
  wget \
  jq \
  unzip \
  openssh-client \
  ca-certificates \
  gnupg \
  lsb-release
success "Essential tools installed"

###############################################################################
# 3. Terraform
###############################################################################
info "Installing Terraform..."

# Add HashiCorp's official GPG key and apt repo
wget -O- https://apt.releases.hashicorp.com/gpg \
  | gpg --dearmor \
  | tee /usr/share/keyrings/hashicorp-archive-keyring.gpg > /dev/null

echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] \
https://apt.releases.hashicorp.com $(lsb_release -cs) main" \
  | tee /etc/apt/sources.list.d/hashicorp.list > /dev/null

apt-get update -qq && apt-get install -y -qq terraform
success "Terraform $(terraform version -json | jq -r '.terraform_version') installed"

###############################################################################
# 4. Ansible
###############################################################################
info "Installing Ansible..."
apt-get install -y -qq software-properties-common
add-apt-repository --yes --update ppa:ansible/ansible 2>/dev/null || true
apt-get install -y -qq ansible
success "Ansible $(ansible --version | head -1 | awk '{print $2}') installed"

###############################################################################
# 5. Project directory structure
###############################################################################
info "Creating project directory structure..."
mkdir -p ~/projects
success "Directory ~/projects created"

###############################################################################
# 6. Clone the website-infra repo (optional — uncomment and edit if you have one)
###############################################################################
# info "Cloning website-infra repo..."
# git clone https://github.com/YOUR-USERNAME/website-infra.git ~/projects/website-infra
# success "Repo cloned to ~/projects/website-infra"

###############################################################################
# 7. SSH key (optional — generate one so this node can SSH into managed containers)
###############################################################################
if [ ! -f ~/.ssh/id_ed25519 ]; then
  info "Generating SSH key pair for this management node..."
  ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N "" -C "mgmt-lxc"
  success "SSH key generated"
else
  info "SSH key already exists — skipping"
fi

###############################################################################
# Done
###############################################################################
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}  Bootstrap complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Installed:"
echo "  terraform  $(terraform version -json | jq -r '.terraform_version')"
echo "  ansible    $(ansible --version | head -1 | awk '{print $2}')"
echo "  git        $(git --version | awk '{print $3}')"
echo ""
echo "Next steps:"
echo "  1. Copy your SSH public key to use in terraform.tfvars:"
echo "     cat ~/.ssh/id_ed25519.pub"
echo ""
echo "  2. Create your tfvars file:"
echo "     cd ~/projects/website-infra"
echo "     cp terraform.tfvars.example terraform.tfvars"
echo "     nano terraform.tfvars"
echo ""
echo "  3. Run your first deployment:"
echo "     terraform init && terraform apply"
echo ""
