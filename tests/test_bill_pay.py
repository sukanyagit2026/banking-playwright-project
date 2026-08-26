import pytest
from playwright.sync_api import expect
from pages.accounts_page import AccountsOverviewPage
from pages.transfer_billpay_page import BillPayPage


@pytest.mark.ui
class TestBillPay:

    def test_pay_bill_reduces_account_balance(
        self, page, registered_customer, first_account_id, random_payee
    ):
        overview = AccountsOverviewPage(page)
        overview.load()
        starting_balance = overview.get_balance_for_account(first_account_id)

        bill_pay_page = BillPayPage(page)
        bill_pay_page.load()
        bill_pay_page.pay_bill(random_payee, first_account_id)

        expect(page.locator(bill_pay_page.SUCCESS_TEXT)).to_be_visible()

        overview.load()
        ending_balance = overview.get_balance_for_account(first_account_id)
        assert ending_balance == round(starting_balance - random_payee["amount"], 2)

    def test_pay_bill_with_mismatched_account_verification_is_rejected(
        self, page, registered_customer, first_account_id, random_payee
    ):
        """
        Negative test: the Bill Pay form requires typing the payee's
        account number twice (account number + verify account) as a
        typo-guard. Deliberately mismatching them should block the
        payment rather than silently accepting it.
        """
        bill_pay_page = BillPayPage(page)
        bill_pay_page.load()

        page.fill(bill_pay_page.PAYEE_NAME, random_payee["name"])
        page.fill(bill_pay_page.PAYEE_STREET, random_payee["street"])
        page.fill(bill_pay_page.PAYEE_CITY, random_payee["city"])
        page.fill(bill_pay_page.PAYEE_STATE, random_payee["state"])
        page.fill(bill_pay_page.PAYEE_ZIP, random_payee["zip_code"])
        page.fill(bill_pay_page.PAYEE_PHONE, random_payee["phone"])
        page.fill(bill_pay_page.PAYEE_ACCOUNT, random_payee["account_number"])
        # Deliberately different from the account number above
        page.fill(bill_pay_page.VERIFY_ACCOUNT, "00000000")
        page.fill(bill_pay_page.AMOUNT, f"{float(random_payee['amount']):.2f}")
        page.select_option(bill_pay_page.FROM_ACCOUNT_SELECT, label=first_account_id)
        page.click(bill_pay_page.SEND_PAYMENT_BUTTON)

        expect(page.locator(bill_pay_page.SUCCESS_TEXT)).not_to_be_visible()
