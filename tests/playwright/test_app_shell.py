"""Smoke tests for the Streamlit UI using Playwright."""

from __future__ import annotations

import pytest


@pytest.mark.e2e
@pytest.mark.playwright
def test_app_title_contains_brand(app_page):
    page = app_page
    expected_keyword = "日本株価分析"
    # Streamlit 初期ロードではタイトルが一時的に "Streamlit" の場合があるため待機
    page.wait_for_function(
        f"document.title.includes('{expected_keyword}')",
        timeout=15000,
    )
    assert expected_keyword in page.title(), f"ページタイトルに{expected_keyword}が含まれていません"


@pytest.mark.e2e
@pytest.mark.playwright
def test_navigation_links_render(app_page):
    page = app_page
    nav_labels = [
        "🏠 ダッシュボード",
        "⚡ リアルタイム",
        "📰 ニュース分析",
    ]

    for label in nav_labels:
        locator = page.get_by_text(label, exact=True)
        locator.first.wait_for(state="visible", timeout=15000)
        assert locator.first.is_visible(), f"ナビゲーション項目 {label} が表示されていません"
