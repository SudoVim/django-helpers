import secrets
from collections.abc import Iterator, Mapping, MutableMapping
from decimal import Decimal
from typing import Any, Callable, cast

from django.contrib.admin.options import BaseModelAdmin
from django.db.models import Model

Filter = Callable[[BaseModelAdmin[Model], Model], Any]
FilterInit = Callable[[str], Filter]
FilterMap = Mapping[str, FilterInit]


def get_val(self: BaseModelAdmin[Model], obj: Model, field_name: str) -> Any:
    if hasattr(self, field_name):
        val = getattr(self, field_name)
        if callable(val):
            return val(obj)

        return val

    if hasattr(obj, field_name):
        val = getattr(obj, field_name)
        if callable(val):
            return val()

        return val

    return None


def dollars_filter(field_name: str) -> Filter:
    def filter(self: BaseModelAdmin[Model], obj: Model) -> Any:
        try:
            val = Decimal(get_val(self, obj, field_name))

        except TypeError:
            return "--"

        quantized = val.quantize(Decimal("0.01"))
        return f"${quantized:,}"

    return filter


def percent_filter(field_name: str) -> Filter:
    def filter(self: BaseModelAdmin[Model], obj: Model) -> Any:
        try:
            val = Decimal(get_val(self, obj, field_name))

        except TypeError:
            return "--"

        return "".join(
            [
                str((val * 100).quantize(Decimal("0.01"))),
                "%",
            ]
        )

    return filter


def number_filter(field_name: str) -> Filter:
    def filter(self: BaseModelAdmin[Model], obj: Model) -> Any:
        try:
            val = Decimal(get_val(self, obj, field_name))

        except TypeError:
            return "--"

        val_str = str(val)
        if val_str.startswith("0E"):
            return "0"
        return str(val).rstrip("0").rstrip(".")

    return filter


def matches_filter(
    filter_map: FilterMap | None, field: str
) -> tuple[str, Filter | None]:
    """
    Check to see if the given *field* matches a filter in the given
    *filter_map*.
    """
    if "|" not in field:
        return field, None

    field_name, filter_str = field.split("|", 1)
    if filter_map is None or filter_str not in filter_map:
        return field_name, None

    field_filter = filter_map[filter_str](field_name)
    field_filter.short_description = field_name  # pyright: ignore[reportFunctionMemberAccess]
    return field_name, field_filter


DEFAULT_FILTER_MAP: FilterMap = {
    "dollars": dollars_filter,
    "percent": percent_filter,
    "number": number_filter,
}


class FilterProcessor:
    filter_map: FilterMap
    field_map: MutableMapping[str, str]

    def __init__(self, filter_map: FilterMap) -> None:
        self.filter_map = filter_map
        self.field_map = {}

    def process_filters(
        self,
        attrs: dict[str, Any],
        field_name: str,
    ) -> None:
        fields = cast(tuple[str] | None, attrs.get(field_name))
        if fields is None:
            return

        def iterate_fields(fields: tuple[str]) -> Iterator[str]:
            for field in fields:
                field_name, field_filter = matches_filter(self.filter_map, field)
                if field_filter is None:
                    yield field_name
                    continue

                if field_name in self.field_map:
                    yield self.field_map[field_name]
                    continue

                filter_fcn_name = f"{field_name}_{secrets.token_hex(4)}"
                self.field_map[field_name] = filter_fcn_name
                attrs[filter_fcn_name] = field_filter
                yield filter_fcn_name

        attrs[field_name] = tuple(iterate_fields(fields))
