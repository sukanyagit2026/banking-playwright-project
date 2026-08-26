import pytest
from playwright.sync_api import expect
from pages.transfer_billpay_page import BillPayPage
from pages.misc_pages import FindTransactionsPage


@pytest.mark.ui
class TestFindTransactions:

    def test_find_transaction_by_amount_after_a_payment(
        self, page, registered_customer, first_account_id, random_payee
    ):
        """
        A realistic end-to-end search: make a real bill payment first
        (so we know a transaction with a specific amount genuinely
        exists), then search for it by that exact amount and confirm
        it's found.

        NOTE: Find Transactions is a standalone page with its OWN
        account dropdown - you select which account to search from
        directly on this page, rather than reaching it by clicking
        into a specific account first.
        """
        bill_pay_page = BillPayPage(page)
        bill_pay_page.load()
        bill_pay_page.pay_bill(random_payee, first_account_id)
        expect(page.locator(bill_pay_page.SUCCESS_TEXT)).to_be_visible()

        find_page = FindTransactionsPage(page)
        find_page.load()
        find_page.select_account(first_account_id)
        find_page.find_by_amount(random_payee["amount"])

        assert find_page.result_count() >= 1

    def test_find_transaction_by_nonexistent_amount_returns_nothing(
        self, page, registered_customer, first_account_id
    ):
        """
        Confirmed via manual inspection: this app shows no "No
        transactions found" message - a search with zero matches just
        renders an empty results table. So the correct assertion is
        zero rows, not a nonexistent text message.
        """
        find_page = FindTransactionsPage(page)
        find_page.load()
        find_page.select_account(first_account_id)
        find_page.find_by_amount(999999.99)

        assert find_page.result_count() == 0
