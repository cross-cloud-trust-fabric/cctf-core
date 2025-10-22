# Cross-Cloud Trust Fabric (CCTF) – Architecture Overview

## System Layers
| Layer | Purpose | Example Technologies |
|--------|----------|-----------------------|
| **Resolver Quorum Engine** | Prevents split-horizon DNS errors using majority vote | AWS Route 53, Azure DNS, Google Cloud DNS |
| **Identity Federation Layer** | Normalizes cloud IAM and SPIFFE/SPIRE identity tokens into unified claims | SPIFFE, OIDC, OAuth2 |
| **Trust Negotiator** | Core FastAPI service deciding if ≥ 2 of 3 trust paths validate | FastAPI, Pydantic |
| **AI Policy Engine** | Detects anomalies, applies safe-mode | LangChain, rule-based logic |
| **Crypto-Agility Layer** | Enables hybrid post-quantum + classical key exchange | Open Quantum Safe (liboqs) |
| **Telemetry Layer** | Observes trust-health metrics and logs | OpenTelemetry, Grafana |

## MVP Flow
1. DNS resolutions collected from multiple resolvers.  
2. Quorum engine computes 3-of-5 majority.  
3. Trust Negotiator checks DNSSEC + mTLS + OIDC (≥ 2 of 3).  
4. Decision returned as **green/yellow/red** with reason.  
5. LKG cache retains last-known-good trust during outage.

## Data Contracts
| Component | Input | Output | Notes |
|------------|--------|---------|-------|
| Resolver | Hostname | Answers[], dnssec_valid | Independent per provider |
| Negotiator | Hostname | Decision, Reason | Combines identity + DNS results |
| Identity | Tokens, Certs | spiffe_ok, oidc_ok | Optional in MVP |

_Status: Draft v0.1_
