"""Shared Playwright test fixtures."""

from __future__ import annotations

import os
from typing import Generator

import pytest


DEFAULT_APP_URL = "http://localhost:8501"


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--app-url",
        action="store",
        default=os.getenv("APP_URL", DEFAULT_APP_URL),
        help="StreamlitアプリのベースURL (例: http://localhost:8501)",
    )


@pytest.fixture(scope="session")
def app_url(pytestconfig: pytest.Config) -> str:
    return str(pytestconfig.getoption("app_url"))


@pytest.fixture()
def app_page(page: "Page", app_url: str):
    page.goto(app_url, wait_until="load")
    yield page
    # Playwrightのpage fixtureが自動クリーンアップ
