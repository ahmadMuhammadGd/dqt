from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from types import UnionType
from typing import Any, Union, get_args, get_origin
from uuid import UUID

from pydantic import BaseModel
from pyiceberg.schema import Schema
from pyiceberg.types import (
    BinaryType,
    BooleanType,
    DateType,
    DecimalType,
    DoubleType,
    LongType,
    NestedField,
    StringType,
    TimestampType,
    UUIDType,
    MapType,
)


def _unwrap_optional(annotation: Any) -> tuple[Any, bool]:
    origin = get_origin(annotation)

    if origin in (Union, UnionType):
        args = get_args(annotation)

        if len(args) == 2 and type(None) in args:
            actual = next(arg for arg in args if arg is not type(None))
            return actual, False

    return annotation, True


def _iceberg_type(annotation: Any):
    annotation, _ = _unwrap_optional(annotation)

    mapping = {
        str: StringType(),
        int: LongType(),
        float: DoubleType(),
        bool: BooleanType(),
        bytes: BinaryType(),
        UUID: UUIDType(),
        date: DateType(),
        datetime: TimestampType(),
    }

    if annotation in mapping:
        return mapping[annotation]

    if annotation is Decimal:
        # choose a sensible default
        return DecimalType(38, 18)

    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        raise TypeError(f"Nested model '{annotation.__name__}' not yet supported.")

    raise TypeError(f"Unsupported type: {annotation!r}")


def iceberg_schema_from_pydantic(model: type[BaseModel]) -> Schema:
    fields = []

    for field_id, (name, field) in enumerate(
        model.model_fields.items(),
        start=1,
    ):
        annotation, required = _unwrap_optional(field.annotation)

        fields.append(
            NestedField(
                field_id=field_id,
                name=name,
                field_type=_iceberg_type(annotation),
                required=required,
            )
        )

    return Schema(*fields)
