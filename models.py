# models.py
from pydantic import BaseModel, Field

class AgentIntent(BaseModel):
    agent_id: str = Field(..., description="Unique Sovereign ID of the requesting agent")
    intent_logic: str = Field(..., description="The raw operational logic or transaction payload")
    target_protocol: str = Field(..., description="The destination smart contract or protocol")
    nonce: int = Field(..., description="Cryptographic nonce to prevent replay attacks")

class NotaryResponse(BaseModel):
    aura_id: str
    status: str
    settlement_fee: str
    treasury_routing: str
    checkpoint: str