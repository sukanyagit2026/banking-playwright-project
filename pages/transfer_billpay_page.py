from pages.base_page import BasePage


class TransferFundsPage(BasePage):
    """Represents /transfer.htm - moving money between the customer's own accounts."""

    AMOUNT_INPUT = "#amount"
    FROM_ACCOUNT_SELECT = "#fromAccountId"
    TO_ACCOUNT_SELECT = "#toAccountId"
    TRANSFER_BUTTON = "input[value='Transfer']"
    RESULT_TEXT = "#showResult"
    CONFIRMATION_TEXT = "text=Transfer Complete!"

    def load(self):
        self.go_to("transfer.htm")

    def transfer(self, amount, from_account_id, to_account_id):
        self.page.fill(self.AMOUNT_INPUT, f"{float(amount):.2f}")
        self.page.select_option(self.FROM_ACCOUNT_SELECT, label=from_account_id)
        self.page.select_option(self.TO_ACCOUNT_SELECT, label=to_account_id)
        self.page.click(self.TRANSFER_BUTTON)

    def is_transfer_successful(self):
        return self.page.locator(self.CONFIRMATION_TEXT).is_visible()


class BillPayPage(BasePage):
    """Represents /billpay.htm - paying an external payee from an account."""

    PAYEE_NAME = "input[name='payee.name']"
    PAYEE_STREET = "input[name='payee.address.street']"
    PAYEE_CITY = "input[name='payee.address.city']"
    PAYEE_STATE = "input[name='payee.address.state']"
    PAYEE_ZIP = "input[name='payee.address.zipCode']"
    PAYEE_PHONE = "input[name='payee.phoneNumber']"
    PAYEE_ACCOUNT = "input[name='payee.accountNumber']"
    VERIFY_ACCOUNT = "input[name='verifyAccount']"
    AMOUNT = "input[name='amount']"
    FROM_ACCOUNT_SELECT = "select[name='fromAccountId']"
    SEND_PAYMENT_BUTTON = "input[value='Send Payment']"
    SUCCESS_TEXT = "text=Bill Payment Complete"

    def load(self):
        self.go_to("billpay.htm")

    def pay_bill(self, payee, from_account_id):
        """
        'payee' is a dictionary with name/address/phone/account_number/
        amount - built by the random_payee fixture, mirroring the same
        dictionary-driven form-fill pattern used across both projects.
        """
        self.page.fill(self.PAYEE_NAME, payee["name"])
        self.page.fill(self.PAYEE_STREET, payee["street"])
        self.page.fill(self.PAYEE_CITY, payee["city"])
        self.page.fill(self.PAYEE_STATE, payee["state"])
        self.page.fill(self.PAYEE_ZIP, payee["zip_code"])
        self.page.fill(self.PAYEE_PHONE, payee["phone"])
        self.page.fill(self.PAYEE_ACCOUNT, payee["account_number"])
        self.page.fill(self.VERIFY_ACCOUNT, payee["account_number"])
        # Format as a proper 2-decimal string for the same reason as
        # FindTransactionsPage.find_by_amount - keeping the exact same
        # decimal scale on both the payment and the later search avoids
        # a BigDecimal scale mismatch on the backend.
        self.page.fill(self.AMOUNT, f"{float(payee['amount']):.2f}")
        self.page.select_option(self.FROM_ACCOUNT_SELECT, label=from_account_id)
        self.page.click(self.SEND_PAYMENT_BUTTON)

    def is_payment_successful(self):
        return self.page.locator(self.SUCCESS_TEXT).is_visible()
