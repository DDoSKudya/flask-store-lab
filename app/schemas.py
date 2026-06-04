from decimal import Decimal

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    """
    Validate input data for creating a new product.

    Defines the required shape and constraints for product creation payloads used by the
    API and service layer.
    """

    name: str = Field(..., min_length=2, max_length=100, description="Product name")
    price: Decimal = Field(..., gt=0, description="Product price")
    description: str | None = Field(None, max_length=1000, description="Product description")
