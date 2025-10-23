"""
Trading-related models for cheapNPC.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class TradeItem(BaseModel):
    """Represents an item to be traded."""
    name: str = Field(description="Name of the item")
    quantity: int = Field(description="Quantity to trade")
    price: float = Field(description="Price per unit")


class TradeOffer(BaseModel):
    """Represents a trade offer from one NPC to another."""
    item_name: str = Field(description="Name of the item being offered")
    quantity: int = Field(description="Quantity of the item")
    price_per_unit: float = Field(description="Price per unit in silver pieces")
    quality: str = Field(description="Quality of the item")
    reasoning: str = Field(description="Why this NPC wants to trade this item")


class TradeResponse(BaseModel):
    """Represents an NPC's response to a trade offer."""
    accepts: bool = Field(description="Whether the NPC accepts the trade")
    counter_offer: Optional[TradeOffer] = Field(description="Counter offer if rejecting the original", default=None)
    reasoning: str = Field(description="Reasoning for acceptance or rejection")


class NPCPairing(BaseModel):
    """Represents a simple pairing between two NPCs."""
    buyer_name: str = Field(description="Name of the NPC who will buy items")
    seller_name: str = Field(description="Name of the NPC who will sell items")


class TradingPair(BaseModel):
    """Represents a trading pair between two NPCs."""
    buyer_name: str = Field(description="Name of the NPC who will buy items")
    seller_name: str = Field(description="Name of the NPC who will sell items")
    items_to_trade: List[TradeItem] = Field(description="List of items to trade with quantity and price")
    reasoning: str = Field(description="Explanation for why this trading pair makes sense")


class TradingPlan(BaseModel):
    """Represents a complete trading plan with multiple pairs."""
    pairings: List[NPCPairing] = Field(description="List of NPC pairings for trading")
    trading_pairs: List[TradingPair] = Field(description="List of trading pairs for this round", default=[])
    total_expected_value: float = Field(description="Total expected value of all trades", default=0.0)
    plan_summary: str = Field(description="Summary of the trading plan", default="")


class NegotiationResult(BaseModel):
    """Represents the final result of NPC negotiations."""
    buyer_name: str = Field(description="Name of the buyer NPC")
    seller_name: str = Field(description="Name of the seller NPC")
    final_item: Optional[str] = Field(description="Item that was agreed upon", default=None)
    final_quantity: Optional[int] = Field(description="Quantity agreed upon", default=None)
    final_price: Optional[float] = Field(description="Final price per unit", default=None)
    final_quality: Optional[str] = Field(description="Quality of the item", default=None)
    success: bool = Field(description="Whether the negotiation was successful")
    negotiation_log: List[str] = Field(description="Log of the negotiation process")


class TradeResult(BaseModel):
    """Represents the result of a single trade."""
    buyer_name: str = Field(description="Name of the buyer NPC")
    seller_name: str = Field(description="Name of the seller NPC")
    items_traded: List[TradeItem] = Field(description="Items that were successfully traded")
    total_cost: float = Field(description="Total cost of the trade")
    success: bool = Field(description="Whether the trade was successful")
    failure_reason: str = Field(description="Reason for failure if unsuccessful", default="")


class TradingExecutionResult(BaseModel):
    """Represents the result of executing all trades."""
    successful_trades: List[TradeResult] = Field(description="List of successful trades")
    failed_trades: List[TradeResult] = Field(description="List of failed trades")
    total_value_traded: float = Field(description="Total value of successful trades")
    execution_summary: str = Field(description="Summary of the trading execution")
