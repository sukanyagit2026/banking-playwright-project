import pytest
from pages.misc_pages import RequestLoanPage


@pytest.mark.ui
class TestRequestLoan:

    def test_loan_within_available_funds_is_approved(
        self, page, registered_customer, first_account_id
    ):
        """
        Confirmed via manual testing: ParaBank compares the LOAN AMOUNT
        itself (not just the down payment) against the funding
        account's available balance - a $5000 loan against a fresh
        account's ~$500 starting balance is correctly denied with
        "We cannot grant a loan in that amount with your available
        funds." A small loan well within a fresh account's typical
        starting balance should be approved instead.
        """
        loan_page = RequestLoanPage(page)
        loan_page.load()
        loan_page.request_loan(amount=100, down_payment=20, from_account_id=first_account_id)

        assert loan_page.is_approved()

    def test_loan_with_down_payment_exceeding_balance_is_denied(
        self, page, registered_customer, first_account_id
    ):
        """
        Requesting a down payment far larger than the account could
        possibly hold should be denied - this is the negative-path
        counterpart to the approval test above.
        """
        loan_page = RequestLoanPage(page)
        loan_page.load()
        loan_page.request_loan(
            amount=100000, down_payment=999999, from_account_id=first_account_id
        )

        assert not loan_page.is_approved()
