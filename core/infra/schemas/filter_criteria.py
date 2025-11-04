from pydantic import BaseModel, Field


class PriceFilterSchema(BaseModel):
    """Pydantic schema for price filter criteria"""
    price_min: float | None = Field(None, description="Minimum price")
    price_max: float | None = Field(None, description="Maximum price")


class LocationFilterSchema(BaseModel):
    """Pydantic schema for location filter criteria"""
    city: str = Field(..., description="City name")


class ApartmentFilterSchema(BaseModel):
    """Pydantic schema for apartment filter criteria"""
    room_count: int | None = Field(None, description="Number of rooms")
    area_min: float | None = Field(None, description="Minimum area")
    area_max: float | None = Field(None, description="Maximum area")


class FilterCriteriaSchema(BaseModel):
    """Complete filter criteria schema for JSON storage"""
    location: LocationFilterSchema
    price: PriceFilterSchema | None = None
    apartment: ApartmentFilterSchema | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "location": {"city": "Kyiv"},
                "price": {"price_min": 10000, "price_max": 50000},
                "apartment": {"room_count": 2, "area_min": 40.0, "area_max": 80.0}
            }
        }
