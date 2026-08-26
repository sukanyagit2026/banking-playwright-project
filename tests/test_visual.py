import platform
import pytest


def _platform_name():
    return platform.system().lower()


@pytest.mark.ui
class TestVisualRegression:
    """
    Visual regression on the login box and account table header - both
    genuinely static elements of this app, unlike ParaBank's
    e-commerce counterpart, this app is not ad-supported so full-page
    screenshots are actually far more stable here. We still keep
    baselines separated by browser AND operating system though, since
    that difference is real regardless of which site is under test
    (see the e-commerce project's test_visual.py for the full story
    on why this matters).
    """

    def test_login_box_visual_snapshot(self, page, assert_snapshot, browser_name):
        page.goto("index.htm")
        login_box = page.locator("#loginPanel").first
        login_box.wait_for(state="visible")
        assert_snapshot(
            login_box.screenshot(),
            name=f"login_box-{browser_name}-{_platform_name()}.png",
        )

    def test_accounts_table_header_visual_snapshot(self, demo_login, assert_snapshot, browser_name):
        demo_login.goto("overview.htm")
        table = demo_login.locator("#accountTable").first
        table.wait_for(state="visible")
        assert_snapshot(
            table.screenshot(),
            name=f"accounts_table-{browser_name}-{_platform_name()}.png",
        )
