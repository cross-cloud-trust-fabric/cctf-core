from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Optional

from cctf.trust_negotiator import TrustDecision, negotiate_trust

app = FastAPI(
    title="CCTF Trust Negotiator (MVP)",
    description="Resolver quorum + LKG fallback demo for Cross-Cloud Trust Fabric",
    version="0.1.0",
)

class VoteOut(BaseModel):
    resolver: str
    success: bool
    answers: List[str]
    dnssec_valid: Optional[bool] = None
    error: Optional[str] = None

class QuorumOut(BaseModel):
    hostname: str
    votes: List[VoteOut]
    agreed: bool
    majority_answers: List[str]
    confidence: float

class IdentityOut(BaseModel):
    spiffe_ok: Optional[bool]
    oidc_ok: Optional[bool]
    details: dict

class DecisionOut(BaseModel):
    hostname: str
    decision: str
    reason: str
    used_lkg: bool
    quorum: QuorumOut
    identity: IdentityOut

@app.get("/health")
def health():
    return {"status": "ok", "service": "cctf-trust-negotiator", "version": "0.1.0"}

@app.get("/trust/resolve", response_model=DecisionOut)
def resolve(host: str = Query(..., description="Hostname to validate (A record)")):
    td: TrustDecision = negotiate_trust(host)
    return DecisionOut(
        hostname=td.hostname,
        decision=td.decision,
        reason=td.reason,
        used_lkg=td.used_lkg,
        quorum=QuorumOut(
            hostname=td.quorum.hostname,
            votes=[VoteOut(**v.__dict__) for v in td.quorum.votes],
            agreed=td.quorum.agreed,
            majority_answers=td.quorum.majority_answers,
            confidence=td.quorum.confidence,
        ),
        identity=IdentityOut(
            spiffe_ok=td.identity.spiffe_ok,
            oidc_ok=td.identity.oidc_ok,
            details=td.identity.details,
        ),
    )
