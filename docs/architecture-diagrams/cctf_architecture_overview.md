# 🧭 Cross-Cloud Trust Fabric (CCTF) – Architecture Overview
**Diagram Type:** System Architecture  
**Purpose:** Show how the CCTF layers interact across multi-cloud environments.

---

```mermaid
flowchart LR
    subgraph CLIENT["🟢 Client Layer – Workloads / Services"]
      A[Service A]
      B[Service B]
    end

    A -->|requests trust validation| TN
    B -->|requests trust validation| TN

    subgraph FABRIC["🔵 Cross-Cloud Trust Fabric Core"]
      TN[Trust Negotiator\n(FastAPI decision engine)]
      RQE[Resolver Quorum Engine\n(3-of-5 DNS vote)]
      IDF[Identity Federation\n(SPIFFE / OIDC)]
      LKG[(Last-Known-Good Cache\n(Signed short TTL trust))]
      AI[AI Policy Engine\n(anomaly detection)]
      CRYPTO[Crypto-Agility Layer\n(Hybrid PQC + classical)]
      O11y[Telemetry\n(OpenTelemetry metrics)]
    end

    TN --> RQE
    TN --> IDF
    TN --> CRYPTO
    TN --> AI
    TN --> O11y
    RQE <-->|update| LKG
    TN -->|fallback| LKG

    subgraph RESOLVERS["🟣 Multi-Cloud Resolver Set"]
      R1[System / VPC DNS]
      R2[Cloudflare DoH]
      R3[Google DoH]
      R4[AWS Route 53]
      R5[Azure DNS]
    end

    RQE --> R1
    RQE --> R2
    RQE --> R3
    RQE --> R4
    RQE --> R5

    subgraph IDENTITY["🟠 Identity Sources"]
      SPIFFE[SPIFFE/SPIRE mTLS]
      OIDC[OIDC Provider]
    end

    IDF --> SPIFFE
    IDF --> OIDC

    style LKG fill:#e6eaff,stroke:#88a
    style CRYPTO fill:#e6ffe6,stroke:#6a6
    style AI fill:#fff5cc,stroke:#cc9
    style O11y fill:#f5f5f5,stroke:#bbb
