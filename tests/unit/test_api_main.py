import pytest

from src.api.main import app, lifespan


@pytest.mark.asyncio
async def test_lifespan_stores_index_from_build_index(mocker):
    mock_index = object()
    mock_client = object()
    mocker.patch(
        "src.api.main.build_index",
        return_value=(mock_index, mock_client),
    )

    app.state.index = None
    async with lifespan(app):
        pass

    assert app.state.index is mock_index


@pytest.mark.asyncio
async def test_lifespan_keeps_app_alive_when_index_build_fails(mocker):
    mocker.patch(
        "src.api.main.build_index",
        side_effect=RuntimeError("qdrant is down"),
    )

    app.state.index = "sentinel"
    async with lifespan(app):
        pass

    assert app.state.index is None


def test_app_registers_expected_routes():
    paths = {route.path for route in app.routes}
    assert "/health" in paths
    assert "/api/query" in paths
    assert "/api/analyze" in paths
    assert "/api/issue" in paths
