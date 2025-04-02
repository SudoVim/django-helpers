from collections.abc import Iterable

Prefetch = set[str]
Related = Iterable[str]


def join(parts: list[str]) -> str:
    return "__".join([p for p in parts if p])


def prefetch(*prefetch_or_related: str | Related | None) -> Prefetch:
    """
    Create a prefecth set with the given *prefetch_or_related* and/or *related*.
    """
    path: list[str] = []
    related = None
    for por in prefetch_or_related:
        if por is None:
            continue

        if isinstance(por, str):
            path.append(por)
            continue

        related = set(por)

    if len(path) == 0 and related is None:
        raise ValueError("Not enough values given to prefetch")

    prefix = join(path)
    if related is None:
        return set([prefix])

    return set(join([prefix, r]) for r in related or [])
