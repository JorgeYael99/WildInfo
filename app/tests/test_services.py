import pytest
from app.services.api_ninjas import fetch_animal_data, fetch_sugerencias
from app.services.unsplash import fetch_unsplash_image
from app.services.wikipedia import fetch_wikipedia_resumen


@pytest.mark.asyncio
async def test_fetch_animal_data_lion():
    result = await fetch_animal_data("lion")
    assert result is not None
    assert "lion" in result["name"].lower()


@pytest.mark.asyncio
async def test_fetch_animal_data_no_existe():
    result = await fetch_animal_data("animal_inventado_xyz_123")
    assert result is None


@pytest.mark.asyncio
async def test_fetch_sugerencias():
    result = await fetch_sugerencias("cat")
    assert isinstance(result, list)
    assert len(result) <= 5


@pytest.mark.asyncio
async def test_fetch_unsplash_image():
    result = await fetch_unsplash_image("dog")
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_fetch_wikipedia_resumen():
    result = await fetch_wikipedia_resumen("tiger")
    # Wikipedia puede retornar None si no encuentra el artículo
    assert result is None or isinstance(result, dict)