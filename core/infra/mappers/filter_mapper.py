from pydantic import ValidationError

from core.domain.user import Filter
from core.domain.user.value import LocationFilter, PriceFilter, ApartmentFilter
from core.infra.models.user import FilterORM
from core.infra.schemas import (
    FilterCriteriaSchema,
    LocationFilterSchema,
    PriceFilterSchema,
    ApartmentFilterSchema,
)


class FilterMapper:
    """Mapper for converting between Filter domain entity and FilterORM"""

    @staticmethod
    def to_domain(orm: FilterORM) -> Filter:
        """Convert FilterORM to Filter domain entity

        Args:
            orm: ORM model

        Returns:
            Filter domain entity

        Raises:
            ValidationError: If criteria JSON doesn't match expected schema
        """
        # Parse and validate criteria JSON using Pydantic
        criteria_schema = FilterCriteriaSchema.model_validate(orm.criteria)

        # Convert Pydantic schemas to domain value objects
        location_filter = LocationFilter(city=criteria_schema.location.city)

        price_filter = None
        if criteria_schema.price:
            price_filter = PriceFilter(
                price_min=criteria_schema.price.price_min,
                price_max=criteria_schema.price.price_max,
            )

        apartment_filter = None
        if criteria_schema.apartment:
            apartment_filter = ApartmentFilter(
                room_count=criteria_schema.apartment.room_count,
                area_min=criteria_schema.apartment.area_min,
                area_max=criteria_schema.apartment.area_max,
            )

        return Filter(
            user_id=orm.tg_user_id,
            name=orm.name,
            location_filter=location_filter,
            _uuid=orm.id,
            price_filter=price_filter,
            apartment_filter=apartment_filter,
        )

    @staticmethod
    def to_orm(filter_obj: Filter, orm: FilterORM | None = None) -> FilterORM:
        """Convert Filter domain entity to FilterORM

        Args:
            filter_obj: Domain entity
            orm: Existing ORM object to update (optional)
        """
        # Convert domain value objects to Pydantic schemas
        location_schema = LocationFilterSchema(city=filter_obj.location_filter.city)

        price_schema = None
        if filter_obj.price_filter:
            price_schema = PriceFilterSchema(
                price_min=filter_obj.price_filter.price_min,
                price_max=filter_obj.price_filter.price_max,
            )

        apartment_schema = None
        if filter_obj.apartment_filter:
            apartment_schema = ApartmentFilterSchema(
                room_count=filter_obj.apartment_filter.room_count,
                area_min=filter_obj.apartment_filter.area_min,
                area_max=filter_obj.apartment_filter.area_max,
            )

        # Create complete criteria schema
        criteria_schema = FilterCriteriaSchema(
            location=location_schema,
            price=price_schema,
            apartment=apartment_schema,
        )

        # Serialize to dict for JSON storage
        criteria_dict = criteria_schema.model_dump(exclude_none=True)

        if orm is None:
            orm = FilterORM(
                id=filter_obj.id,
                tg_user_id=filter_obj.user_id,
                name=filter_obj.name,
                criteria=criteria_dict,
            )
        else:
            # Update existing ORM
            orm.name = filter_obj.name
            orm.criteria = criteria_dict

        return orm
