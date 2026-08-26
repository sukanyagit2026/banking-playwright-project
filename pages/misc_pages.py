from pages.base_page import BasePage


class FindTransactionsPage(BasePage):
    """
    Represents /findtrans.htm - ParaBank offers several independent
    search modes on one page (by transaction ID, by date, by date
    range, by amount). Each mode has its own input(s) and its own
    submit button, which is why this page object exposes several
    small methods instead of one generic 'search' method.

    IMPORTANT: this page has its OWN account selector dropdown
    (#accountId) - it is a standalone page, not something you reach
    by clicking into an account's Activity page first. An earlier
    version of this page object assumed the latter, which was wrong.
    """

    ACCOUNT_SELECT = "#accountId"

    TRANSACTION_ID_INPUT = "#transactionId"
    FIND_BY_ID_BUTTON = "#findById"

    AMOUNT_INPUT = "#amount"
    FIND_BY_AMOUNT_BUTTON = "#findByAmount"

    RESULTS_TABLE = "#transactionTable"
    RESULT_ROWS = "#transactionTable tbody tr"
    NO_RESULTS_TEXT = "text=No transactions found"

    def load(self):
        self.go_to("findtrans.htm")

    def select_account(self, account_id):
        self.page.select_option(self.ACCOUNT_SELECT, value=str(account_id))

    def find_by_transaction_id(self, transaction_id):
        self.page.fill(self.TRANSACTION_ID_INPUT, str(transaction_id))
        self.page.click(self.FIND_BY_ID_BUTTON)
        # Wait for the results page to actually finish rendering before
        # returning control - without this, .click() returns as soon as
        # the click registers, but the resulting page reload may still
        # be in flight. A human naturally waits a beat before looking
        # at results; automated code needs to be told to do the same.
        self.page.wait_for_selector(self.RESULTS_TABLE)

    def find_by_amount(self, amount):
        # Format as a proper 2-decimal string (e.g. "25.00", not "25.0").
        self.page.fill(self.AMOUNT_INPUT, f"{float(amount):.2f}")
        self.page.click(self.FIND_BY_AMOUNT_BUTTON)
        self.page.wait_for_selector(self.RESULTS_TABLE)

    def result_count(self):
        # Confirmed via screenshot: there is NO "No transactions found"
        # message on this app - a search with no matches just shows an
        # empty results table. Counting rows via their transaction
        # description LINK (e.g. "Check # 1211", "Funds Transfer Sent")
        # rather than raw <tr> avoids miscounting the header row,
        # mirroring the same fix applied to AccountsOverviewPage earlier.
        return self.page.locator(f"{self.RESULTS_TABLE} tbody tr td a").count()


class UpdateContactInfoPage(BasePage):
    """Represents /updateprofile.htm."""

    FIRST_NAME = "#customer\\.firstName"
    LAST_NAME = "#customer\\.lastName"
    STREET = "#customer\\.address\\.street"
    CITY = "#customer\\.address\\.city"
    STATE = "#customer\\.address\\.state"
    ZIP_CODE = "#customer\\.address\\.zipCode"
    PHONE = "#customer\\.phoneNumber"
    UPDATE_BUTTON = "input[value='Update Profile']"
    SUCCESS_TEXT = "text=Profile Updated"

    def load(self):
        self.go_to("updateprofile.htm")
        # This page appears to populate its fields with the customer's
        # existing data slightly AFTER the initial page load (rather
        # than having them server-rendered immediately). Filling the
        # phone field too early can race against that repopulation,
        # silently overwriting our typed value back to the original
        # and leaving the form's validation in a broken state. Waiting
        # for the phone field to actually contain a value first avoids
        # fighting that race condition.
        self.page.wait_for_function(
            "document.getElementById('customer.phoneNumber') "
            "&& document.getElementById('customer.phoneNumber').value !== ''"
        )

    def update_phone_number(self, new_phone):
        # A minimal, realistic update: change just one field (phone
        # number) rather than re-filling the whole form, which mirrors
        # how a real customer would use this screen
        self.page.fill(self.PHONE, new_phone)
        self.page.click(self.UPDATE_BUTTON)

    def is_update_successful(self):
        return self.page.locator(self.SUCCESS_TEXT).is_visible()


class RequestLoanPage(BasePage):
    """Represents /requestloan.htm."""

    AMOUNT_INPUT = "#amount"
    DOWN_PAYMENT_INPUT = "#downPayment"
    FROM_ACCOUNT_SELECT = "#fromAccountId"
    APPLY_BUTTON = "input[value='Apply Now']"
    RESULT_PANEL = "#requestLoanResult"
    # Confirmed via screenshot: a dedicated <td id="loanStatus"> holds
    # exactly "Approved" or "Denied" - far more reliable than matching
    # a full sentence of message text, which is more likely to change.
    # Also confirmed: NO iframe is involved in this result panel.
    LOAN_STATUS = "#loanStatus"

    def load(self):
        self.go_to("requestloan.htm")

    def request_loan(self, amount, down_payment, from_account_id):
        self.page.fill(self.AMOUNT_INPUT, f"{float(amount):.2f}")
        self.page.fill(self.DOWN_PAYMENT_INPUT, f"{float(down_payment):.2f}")
        self.page.select_option(self.FROM_ACCOUNT_SELECT, label=from_account_id)
        self.page.click(self.APPLY_BUTTON)
        # The result still renders asynchronously after the click, so
        # wait for the status cell to actually appear before reading it.
        self.page.wait_for_selector(self.LOAN_STATUS)

    def is_approved(self):
        return self.page.locator(self.LOAN_STATUS).inner_text().strip() == "Approved"
