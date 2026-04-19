from pydantic import BaseModel, Field

class AgentIntent(BaseModel):
    agent_id: str = Field(..., description="Unique SHA-256 identifier of the AI agent", max_length=64)
    target_protocol: str = Field(..., description="Destination protocol or data endpoint", max_length=128)
    intent_logic: str = Field(..., description="Raw execution payload from the agent", max_length=2048)
    nonce: int = Field(..., description="Cryptographic nonce to prevent replay attacks")

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "AGENT-9X8F7E6D5C",
                "target_protocol": "Nairobi_Aggregator_V1",
                "intent_logic": "execute_standard_read_query",
                "nonce": 1713456789
            }
        }

class NotaryResponse(BaseModel):
    aura_id: str = Field(..., description="The Sovereign Seal ID")
    status: str = Field(..., description="Authorization status")
    settlement_fee: str = Field(..., description="Fee accrued in ETH")
    treasury_routing: str = Field(..., description="Destination wallet for settlement")
    checkpoint: str = Field(..., description="Geographic location of the verifying node")