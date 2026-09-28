from __future__ import annotations

import pytest

from urlshort.domain.value_objects.slug import Slug


def test_slug_valido() -> None:
    assert Slug("abc123").value == "abc123"
    assert Slug("a-b_c").value == "a-b_c"


@pytest.mark.parametrize(
    "bad",
    ["ab", "a" * 51, "spaces are bad", "with/slash", "with.dot", "ção"],
)
def test_slug_invalido(bad: str) -> None:
    with pytest.raises(ValueError):
        Slug(bad)
