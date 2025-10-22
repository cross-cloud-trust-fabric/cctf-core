# Trust Negotiator Decision Pipeline (≥2 of 3 Validation)
**Diagram Type:** Flowchart  
**Purpose:** Show how the CCTF Trust Negotiator decides outcomes.

---

```mermaid
flowchart TD
    A["Start Request - /trust/resolve?host=H"] --> Q["Resolver Quorum Engine"]
    Q -->|Majority| QOK{"Quorum OK?"}
    Q -->|No Majority| LKGCHK["LKG available and valid?"]

    LKGCHK -->|Yes| DEGRADED["Decision: Degraded - Use LKG and alert"]
    LKGCHK -->|No| RED["Decision: Red - Block and log alert"]

    QOK --> IDF["Identity Federation Checks (SPIFFE / OIDC)"]
    QOK --> DNSSEC["DNSSEC validation?"]

    IDF --> SCORE["Count successful trust paths"]
    DNSSEC --> SCORE

    SCORE -->|≥2 of 3| GREEN["Decision: Green - Trust satisfied"]
    SCORE -->|<2 of 3| DEGRADED

    GREEN --> OUT["Return JSON Decision Object {hostname, decision, reason}"]
    DEGRADED --> OUT
    RED --> OUT

    style GREEN fill:#e6ffe6,stroke:#6a6
    style DEGRADED fill:#fff5cc,stroke:#cc9
    style RED fill:#ffe6e6,stroke:#c66
