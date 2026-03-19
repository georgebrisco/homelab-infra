# =============================================================================
# Cloudflare — florida-ai tunnel
# =============================================================================
# Copy these resources into main.tf after purchasing a domain.
# Also add florida_ai_domain and florida_ai_zone_id to variables.tf and tfvars.

resource "random_password" "florida_ai_tunnel_secret" {
  length  = 32
  special = false
}

resource "cloudflare_zero_trust_tunnel_cloudflared" "florida_ai" {
  account_id = var.cloudflare_account_id
  name       = "florida-ai"
  secret     = base64sha256(random_password.florida_ai_tunnel_secret.result)

  lifecycle {
    ignore_changes = [secret]
  }
}

resource "cloudflare_zero_trust_tunnel_cloudflared_config" "florida_ai" {
  account_id = var.cloudflare_account_id
  tunnel_id  = cloudflare_zero_trust_tunnel_cloudflared.florida_ai.id

  config {
    ingress_rule {
      hostname = var.florida_ai_domain
      service  = "http://localhost:80"
    }
    ingress_rule {
      hostname = "www.${var.florida_ai_domain}"
      service  = "http://localhost:80"
    }
    ingress_rule {
      service = "http_status:404"
    }
  }
}

resource "cloudflare_record" "florida_ai_apex" {
  zone_id = var.florida_ai_zone_id
  name    = var.florida_ai_domain
  type    = "CNAME"
  content = "${cloudflare_zero_trust_tunnel_cloudflared.florida_ai.id}.cfargotunnel.com"
  proxied = true
  comment = "florida-ai tunnel"
}

resource "cloudflare_record" "florida_ai_www" {
  zone_id = var.florida_ai_zone_id
  name    = "www"
  type    = "CNAME"
  content = "${cloudflare_zero_trust_tunnel_cloudflared.florida_ai.id}.cfargotunnel.com"
  proxied = true
  comment = "florida-ai www tunnel"
}
