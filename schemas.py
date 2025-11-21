"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# NEOSERVICE voice calling data models

class CallEvent(BaseModel):
    """A single event within a call, such as a transcript segment or status update"""
    call_id: str = Field(..., description="Associated call id")
    type: str = Field(..., description="event type e.g., transcript, status")
    text: Optional[str] = Field(None, description="Transcript text if type=transcript")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class Call(BaseModel):
    """Represents a voice call session"""
    title: Optional[str] = Field(None, description="Optional call title")
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = Field(None)
    duration_seconds: Optional[int] = Field(None)
    status: str = Field("active", description="active|ended|failed")
    participant: Optional[str] = Field(None, description="Optional participant label")
    events: List[CallEvent] = Field(default_factory=list)

# Add your own schemas here:
# --------------------------------------------------

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
