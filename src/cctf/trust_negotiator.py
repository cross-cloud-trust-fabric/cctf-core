"""
Cross-Cloud Trust Fabric (CCTF) – MVP Trust Negotiator

- Quorum voting across multiple resolvers (3 of 5)
- DNSSEC-aware when DoH returns the AD flag
- Signed, short-lived Last-Known-Good (LKG) cache
- Stubs for SPIFFE/OIDC (wired later)

This MVP uses public DoH + system DNS for a local demo.
"""

from __future__ import annotations
import base64, hashlib, hmac, json, os, time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import dns.resolver
import requests

# ---- Policy ----
QUORUM_SIZE = 5
QUORUM_REQUIRED = 3
LKG_TTL_SECONDS = 15 * 60  # 15 minutes
HMAC_SECRET = os.environ.get("CCTF_LKG_HMAC", "dev-only-change-me")

# ---- Models ----
@dataclass
class Vote:
    resolver: str
    success: bool
    answers: List[str] = field(default_factory=list)
    dnssec_valid: Optional[bool] = None
    error: Optional[str] = None

@dataclass
class QuorumResult:
    hostname: str
    votes: List[Vote]
    agreed: bool
    majority_answers: List[str]
    confidence: float  # 0..1

@dataclass
class IdentityResult:
    spiffe_ok: Optional[bool] = None
    oidc_ok: Optional[bool] = None
    details: Dict[str, str] = field(default_factory=dict)

@dataclass
class TrustDecision:
    hostname: str
    quorum: QuorumResult
    identity: IdentityResult
    used_lkg: bool
    decision: str  # "green" | "degraded" | "red"
    reason: str

# ---- Resolvers ----
class Resolver:
    name = "base"
    def resolve_a(self, hostname: str) -> Vote:  # pragma: no cover
        raise NotImplementedError

class SystemResolver(Resolver):
    name = "system-dns"
    def resolve_a(self, hostname: str) -> Vote:
        try:
            answers = dns.resolver.resolve(hostname, "A", lifetime=2.0)
            ips = sorted({a.to_text() for a in answers})
            return Vote(self.name, True, ips, None, None)
        except Exception as e:
            return Vote(self.name, False, [], None, str(e))

class DoHResolver(Resolver):
    def __init__(self, name: str, endpoint: str):
        self.name = name
        self.endpoint = endpoint
    def resolve_a(self, hostname: str) -> Vote:
        try:
            params = {"name": hostname, "type": "A"}
            headers = {"accept": "application/dns-json"}
            r = requests.get(self.endpoint, params=params, headers=headers, timeout=2.0)
            r.raise_for_status()
            data = r.json()
            answers = []
            for rr in data.get("Answer", []) or []:
                if rr.get("type") == 1:
                    answers.append(rr.get("data"))
            answers = sorted(set(answers))
            ad = data.get("AD")  # Authenticated Data (DNSSEC)
            ok = len(answers) > 0
            return Vote(self.name, ok, answers, bool(ad), None if ok else "no A answers")
        except Exception as e:
            return Vote(self.name, False, [], None, str(e))

VOTERS: List[Resolver] = [
    SystemResolver(),
    DoHResolver("cloudflare-doh", "https://cloudflare-dns.com/dns-query"),
    DoHResolver("google-doh", "https://dns.google/resolve"),
    SystemResolver(),  # alt system attempt (simple diversity for MVP)
    DoHResolver("cloudflare-doh-2", "https://cloudflare-dns.com/dns-query"),
]

# ---- Quorum engine ----
def quorum_vote(hostname: str) -> QuorumResult:
    votes: List[Vote] = [voter.resolve_a(hostname) for voter in VOTERS]

    signature_counts: Dict[str, int] = {}
    for v in votes:
        sig = ",".join(v.answers) if v.success else "FAIL"
        signature_counts[sig] = signature_counts.get(sig, 0) + 1

    majority_sig, majority_count = "", 0
    for sig, count in signature_counts.items():
        if sig == "FAIL":
            continue
        if count > majority_count:
            majority_sig, majority_count = sig, count

    majority_answers = majority_sig.split(",") if majority_sig else []
    agreed = majority_count >= QUORUM_REQUIRED and len(majority_answers) > 0

    total_votes = sum(c for s, c in signature_counts.items() if s != "FAIL") or 1
    confidence = round(majority_count / total_votes, 3)

    return QuorumResult(
        hostname=hostname,
        votes=votes,
        agreed=agreed,
        majority_answers=majority_answers,
        confidence=confidence,
    )

# ---- Identity stubs ----
def verify_spiffe_stub(hostname: str) -> Tuple[bool, str]:
    return (False, "SPIFFE not configured in MVP")

def verify_oidc_stub(hostname: str) -> Tuple[bool, str]:
    return (False, "OIDC not configured in MVP")

# ---- LKG (signed) ----
def _sign(payload: dict) -> str:
    blob = json.dumps(payload, sort_keys=True).encode()
    mac = hmac.new(HMAC_SECRET.encode(), blob, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(mac).decode().rstrip("=")

_LKG: Dict[str, dict] = {}

def lkg_get(hostname: str) -> Optional[dict]:
    entry = _LKG.get(hostname)
    if not entry:
        return None
    if time.time() > entry["exp"]:
        _LKG.pop(hostname, None)
        return None
    if _sign(entry["data"]) != entry["sig"]:
        return None
    return entry

def lkg_put(hostname: str, answers: List[str]) -> None:
    data = {"answers": sorted(answers), "ts": int(time.time())}
    _LKG[hostname] = {"data": data, "sig": _sign(data), "exp": time.time() + LKG_TTL_SECONDS}

# ---- Main negotiation ----
def negotiate_trust(hostname: str) -> TrustDecision:
    q = quorum_vote(hostname)

    spiffe_ok, spiffe_msg = verify_spiffe_stub(hostname)
    oidc_ok, oidc_msg  = verify_oidc_stub(hostname)
    identity = IdentityResult(spiffe_ok=spiffe_ok, oidc_ok=oidc_ok,
                              details={"spiffe": spiffe_msg, "oidc": oidc_msg})

    if q.agreed:
        if q.majority_answers:
            lkg_put(hostname, q.majority_answers)
        return TrustDecision(hostname, q, identity, False, "green",
                             "DNS quorum satisfied; MVP identity optional.")

    lkg = lkg_get(hostname)
    if lkg:
        return TrustDecision(hostname, q, identity, True, "degraded",
                             "DNS quorum failed; using signed Last-Known-Good within TTL.")

    return TrustDecision(hostname, q, identity, False, "red",
                         "DNS quorum failed and no valid LKG entry.")
