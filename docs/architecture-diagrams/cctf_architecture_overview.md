# Cross-Cloud Trust Fabric (CCTF) – Architecture Overview
**Diagram Type:** System Architecture  
**Purpose:** Show how the CCTF layers interact across multi-cloud environments.

---

```mermaid
flowchart LR
  %% ===== Client Layer =====
  subgraph CLIENT["Client Layer — Workloads / Services"]
    A["Service A"]
    B["Service B"]
  end

  A -->|requests trust validation| TN
  B -->|requests trust validation| TN

  %% ===== Fabric Core =====
  subgraph FABRIC["Cross-Cloud Trust Fabric Core"]
    TN["Trust Negotiator\nFastAPI decision engine"]
    RQE["Resolver Quorum Engine\n3-of-5 DNS vote"]
    IDF["Identity Federation\nSPIFFE / OIDC"]
    LKG["Last-Known-Good Cache\nSigned short TTL trust"]
    AI["AI Policy Engine\nAnomaly detection"]
    CRYPTO["Crypto-Agility Layer\nHybrid PQC + classical"]
    O11y["Telemetry\nOpenTelemetry metrics"]
  end

  TN --> RQE
  TN --> IDF
  TN --> CRYPTO
  TN --> AI
  TN --> O11y
  RQE --> LKG
  TN -->|fallback uses| LKG

  %% ===== Resolver Set =====
  subgraph RESOLVERS["Multi-Cloud Resolver Set"]
    R1["System / VPC DNS"]
    R2["Cloudflare DoH"]
    R3["Google DoH"]
    R4["AWS Route 53"]
    R5["Azure DNS"]
  end

  RQE --> R1
  RQE --> R2
  RQE --> R3
  RQE --> R4
  RQE --> R5

  %% ===== Identity Sources =====
  subgraph IDENTITY["Identity Sources"]
    SPIFFE["SPIFFE / SPIRE mTLS"]
    OIDC["OIDC Provider"]
  end

  IDF --> SPIFFE
  IDF --> OIDC
