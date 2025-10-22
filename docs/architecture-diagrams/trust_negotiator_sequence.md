# 🧠 Trust Negotiator Decision Pipeline (≥2 of 3 Validation)
**Diagram Type:** Flowchart  
**Purpose:** Show how the CCTF trust negotiator decides outcomes.

---

```mermaid
flowchart TD
    A[Start Request<br/>/trust/resolve?host=H] --> Q[Resolver Quorum Engine]
    Q -->|majority| QOK{Quorum OK?}
    Q -->|no majority| LKGCHK[LKG available & valid?]
    LKGCHK -->|yes| DEGRADED[🟡 Decision: Degraded<br/>Use LKG; alert]
    LKGCHK -->|no| RED[🔴 Decision: Red<br/>Block & log alert]
    QOK --> IDF[Identity Federation Checks<br/>(SPIFFE / OIDC)]
    QOK --> DNSSEC[DNSSEC validation?]
    IDF --> SCORE[Count successful trust paths]
    DNSSEC --> SCORE
    SCORE -->|≥2 of 3| GREEN[🟢 Decision: Green<br/>Trust satisfied]
    SCORE -->|<2 of 3| DEGRADED
    GREEN --> OUT[Return JSON Decision Object<br/>{hostname, decision, reason}]
    DEGRADED --> OUT
    RED --> OUT

    style GREEN fill:#e6ffe6,stroke:#6a6
    style DEGRADED fill:#fff5cc,stroke:#cc9
    style RED fill:#ffe6e6,stroke:#c66
