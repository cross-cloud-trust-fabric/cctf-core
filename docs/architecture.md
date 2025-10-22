# 🧭 Cross-Cloud Trust Fabric (CCTF) – Architecture Overview

**Tagline:** “Trust Is the New Uptime.”  
**Author:** Braden Hamm — Rio Communities, NM  
**Status:** Draft v0.1  

---

## 1. System Layers

| Layer | Purpose | Example Technologies |
|--------|----------|-----------------------|
| **Client Layer** | Workloads, APIs, or services that request trust validation through the fabric. | Any cloud or hybrid service |
| **Resolver Quorum Engine (RQE)** | Prevents split-horizon DNS errors using a 3-of-5 voting model. | AWS Route 53, Azure DNS, Google Cloud DNS, Cloudflare, System DNS |
| **Identity Federation Layer (IDF)** | Normalizes cloud IAM and SPIFFE/SPIRE tokens into unified identity claims. | SPIFFE, OIDC, OAuth2 |
| **Trust Negotiator (TN)** | Core FastAPI service deciding if ≥ 2 of 3 trust paths (DNSSEC, mTLS, OIDC) validate. | Python, FastAPI, Pydantic |
| **AI Policy Engine** | Detects anomalies, triggers “safe mode,” and logs telemetry events. | LangChain, rule-based logic |
| **Crypto-Agility Layer (CAL)** | Enables hybrid post-quantum + classical key exchange for crypto migration. | Open Quantum Safe (liboqs) |
| **Telemetry Layer** | Observes and records trust-health metrics across clouds. | OpenTelemetry, Grafana |

---

## 2. MVP Flow

1. **Resolver Quorum Engine** queries 3–5 independent DNS resolvers.  
2. **Quorum computation** determines majority agreement (≥ 3 matching responses).  
3. **Trust Negotiator** validates ≥ 2 of 3 trust signals:  
   - ✅ DNSSEC  
   - ✅ mTLS / SPIFFE identity  
   - ✅ OIDC discovery  
4. Decision returned as **🟢 Green**, **🟡 Degraded**, or **🔴 Red**, with human-readable reason.  
5. **Last-Known-Good (LKG)** cache retains signed trust data to survive outages.  
6. **AI Policy Engine** audits and learns from anomalies to strengthen resilience.  

---

## 3. Data Contracts

| Component | Input | Output | Notes |
|------------|--------|---------|-------|
| **Resolver** | `hostname` | `answers[]`, `dnssec_valid` | One per provider; validated in parallel |
| **Negotiator** | `hostname` | `decision`, `reason` | Combines identity, DNS, and crypto results |
| **Identity** | `tokens`, `certs` | `spiffe_ok`, `oidc_ok` | Optional in MVP; expands in later phases |
| **Cache (LKG)** | Signed JSON blob | TTL-limited revalidation | Prevents total trust collapse on DNS loss |

---

## 4. Architecture Diagram References

| Diagram | Description |
|----------|--------------|
| [🧭 **Architecture Overview**](architecture-diagrams/cctf_architecture_overview.md) | High-level system layers and cloud interactions. |
| [⚙️ **Resolver Quorum Flow**](architecture-diagrams/resolver_quorum_flow.md) | Step-by-step DNS quorum consensus and cache fallback. |
| [🧠 **Trust Negotiator Sequence**](architecture-diagrams/trust_negotiator_sequence.md) | Validation pipeline showing ≥ 2-of-3 trust decision logic. |

---

## 5. Data Flow Summary

```mermaid
flowchart LR
    A[Client Service] --> B[Trust Negotiator]
    B --> C[Resolver Quorum Engine]
    B --> D[Identity Federation Layer]
    B --> E[Crypto-Agility Layer]
    C -->|vote results| B
    D -->|identity claims| B
    E -->|key validation| B
    B -->|Decision JSON (green/degraded/red)| A
