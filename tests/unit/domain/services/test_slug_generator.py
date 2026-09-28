from __future__ import annotations

import pytest

from urlshort.domain.services.slug_generator import RandomBase62SlugGenerator


def test_gera_slug_no_tamanho_pedido() -> None:
    gen = RandomBase62SlugGenerator(length=8)
    s = gen.generate()
    assert len(s.value) == 8


def test_slugs_sao_diferentes() -> None:
    gen = RandomBase62SlugGenerator()
    a = gen.generate()
    b = gen.generate()
    assert a != b


def test_length_minima() -> None:
    with pytest.raises(ValueError):
        RandomBase62SlugGenerator(length=2)
