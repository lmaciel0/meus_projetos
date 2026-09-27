import pytest

import corretor


@pytest.fixture(autouse=True)
def _limpar_cache():
    # Os testes trocam o LanguageTool falso entre si; o cache de parágrafos não pode vazar.
    corretor._cache.clear()
    yield
    corretor._cache.clear()
