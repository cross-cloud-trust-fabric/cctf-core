# ⚙️ Resolver Quorum Flow (3-of-5 Consensus)
**Diagram Type:** Sequence Diagram  
**Purpose:** Show how DNS quorum resolution and LKG fallback operate.

---

```mermaid
sequenceDiagram
    autonumber
    participant APP as 🟢 Client
    participant TN as 🔵 Trust Negotiator
    participant RQE as ⚙️ Resolver Quorum Engine
    participant R1 as AWS Route 53
    participant R2 as Azure DNS
    participant R3 as Google Cloud DNS
    participant R4 as Cloudflare DoH
    participant R5 as System Resolver
    participant LKG as 🟠 LKG Cache

    APP->>TN: /trust/resolve?host=example.com
    TN->>RQE: Begin quorum resolution
    par Parallel DNS lookups
        RQE->>R1: Query A record
        RQE->>R2: Query A record
        RQE->>R3: Query A record
        RQE->>R4: Query A record
        RQE->>R5: Query A record
    end
    R1-->>RQE: Response + AD flag
    R2-->>RQE: Response + AD flag
    R3-->>RQE: Response + AD flag
    R4-->>RQE: Response + AD flag
    R5-->>RQE: Response + AD flag

    RQE->>RQE: Determine majority set (≥3 match)
    alt quorum achieved
        RQE->>LKG: Sign & store LKG (short TTL)
        RQE-->>TN: quorum=true, confidence score
    else quorum failed
        TN->>LKG: Try retrieving previous LKG
        alt valid LKG found
            TN-->>APP: decision=degraded, reason="using cached trust"
        else no LKG
            TN-->>APP: decision=red, reason="no quorum or cache"
        end
    end

    TN-->>APP: Final trust decision (green/yellow/red)
