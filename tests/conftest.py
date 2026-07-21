import pytest

from agenticlens.config.live_pricing import DISABLE_ENV_VAR


@pytest.fixture(autouse=True)
def _disable_live_pricing_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep the test suite hermetic: no test should hit the network by default.

    Tests that specifically exercise live pricing mock the network call and
    unset this flag for the duration of the test.
    """
    monkeypatch.setenv(DISABLE_ENV_VAR, "1")
