import pytest
from playwright.sync_api import expect
from pages.accounts_page import AccountsOverviewPage, OpenNewAccountPage


@pytest.mark.ui
class TestAccountsOverview:

    def test_overview_shows_at_least_one_account(self, demo_login):
        overview = AccountsOverviewPage(demo_login)
        overview.load()
        assert overview.account_count() >= 1

    def test_overview_lists_valid_account_ids(self, demo_login):
        overview = AccountsOverviewPage(demo_login)
        overview.load()
        ids = overview.get_account_ids()
        # Every ParaBank account number is purely numeric - this is a
        # good sanity check that we parsed the table correctly
        assert all(acc_id.isdigit() for acc_id in ids)


@pytest.mark.ui
class TestOpenNewAccount:

    @pytest.mark.parametrize("account_type", ["SAVINGS", "CHECKING"])
    def test_open_new_account(self, page, registered_customer, first_account_id, account_type):
        """
        Data-driven test: opens both a SAVINGS and a CHECKING account,
        funded from the customer's original auto-created account.
        """
        open_account_page = OpenNewAccountPage(page)
        open_account_page.load()
        open_account_page.open_account(account_type, from_account_id=first_account_id)

        expect(page.locator(open_account_page.RESULT_TEXT)).to_be_visible()
        new_id = open_account_page.get_new_account_id()
        assert new_id.isdigit()

        # Confirm the newly opened account genuinely appears back on
        # the overview page - this closes the loop rather than trusting
        # the confirmation message alone
        overview = AccountsOverviewPage(page)
        overview.load()
        assert new_id in overview.get_account_ids()
