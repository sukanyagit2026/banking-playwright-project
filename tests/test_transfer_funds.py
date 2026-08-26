import pytest
from playwright.sync_api import expect
from pages.accounts_page import AccountsOverviewPage, OpenNewAccountPage
from pages.transfer_billpay_page import TransferFundsPage


@pytest.mark.ui
class TestTransferFunds:

    def test_transfer_between_own_accounts_updates_balances(
        self, page, registered_customer, first_account_id
    ):
        """
        Full real-world flow:
        1. Open a second account (so there's somewhere to transfer to)
        2. Record both accounts' starting balances
        3. Transfer a fixed amount from account 1 to account 2
        4. Verify the confirmation message
        5. Verify the balances actually moved by exactly the transferred amount
        """
        # Step 1: open a second account to transfer money into
        open_account_page = OpenNewAccountPage(page)
        open_account_page.load()
        open_account_page.open_account("SAVINGS", from_account_id=first_account_id)
        second_account_id = open_account_page.get_new_account_id()

        # Step 2: record starting balances
        overview = AccountsOverviewPage(page)
        overview.load()
        starting_balance_from = overview.get_balance_for_account(first_account_id)
        starting_balance_to = overview.get_balance_for_account(second_account_id)

        # Step 3: transfer funds
        transfer_amount = 50.00
        transfer_page = TransferFundsPage(page)
        transfer_page.load()
        transfer_page.transfer(transfer_amount, first_account_id, second_account_id)

        # Step 4: verify confirmation
        expect(page.locator(transfer_page.CONFIRMATION_TEXT)).to_be_visible()

        # Step 5: verify the actual balances reflect the transfer -
        # this is the real assertion; a confirmation message alone
        # doesn't prove money actually moved
        overview.load()
        ending_balance_from = overview.get_balance_for_account(first_account_id)
        ending_balance_to = overview.get_balance_for_account(second_account_id)

        assert ending_balance_from == round(starting_balance_from - transfer_amount, 2)
        assert ending_balance_to == round(starting_balance_to + transfer_amount, 2)
