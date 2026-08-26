from pages.base_page import BasePage


class AccountsOverviewPage(BasePage):
    """Represents /overview.htm - the dashboard listing all of a customer's accounts."""

    ACCOUNT_TABLE = "#accountTable"
    ACCOUNT_ROWS = "#accountTable tbody tr"
    TOTAL_ROW = "#accountTable tfoot tr"

    def load(self):
        self.go_to("overview.htm")
        # .count() does NOT auto-wait the way expect() does - it just
        # checks whatever's in the DOM at that exact instant. Explicitly
        # waiting for at least one row to appear here prevents a race
        # condition where the page hasn't finished rendering yet.
        self.page.wait_for_selector(self.ACCOUNT_ROWS)

    def account_count(self):
        # Counting real accounts by how many rows have a clickable
        # account-number link is more robust than counting raw <tr>
        # elements and guessing whether a "Total" summary row exists -
        # a summary row (if one exists on some pages) has no link, so
        # it's naturally excluded here without needing to subtract 1.
        return len(self.get_account_ids())

    def get_account_ids(self):
        """Returns a list of every account number shown on the overview page."""
        links = self.page.locator(f"{self.ACCOUNT_ROWS} td:first-child a")
        count = links.count()
        return [links.nth(i).inner_text() for i in range(count)]

    def click_account(self, account_id):
        self.page.click(f"a:has-text('{account_id}')")

    def get_balance_for_account(self, account_id):
        row = self.page.locator(f"{self.ACCOUNT_ROWS}:has-text('{account_id}')")
        balance_text = row.locator("td").nth(1).inner_text()
        # Balances render as "$1,234.56" - strip symbols so tests can
        # do real numeric comparisons instead of fragile string checks
        return float(balance_text.replace("$", "").replace(",", ""))


class OpenNewAccountPage(BasePage):
    """Represents /openaccount.htm."""

    ACCOUNT_TYPE_SELECT = "#type"
    FROM_ACCOUNT_SELECT = "#fromAccountId"
    OPEN_BUTTON = "input[value='Open New Account']"
    RESULT_TEXT = "#openAccountResult"
    NEW_ACCOUNT_ID = "#newAccountId"

    def load(self):
        self.go_to("openaccount.htm")

    def open_account(self, account_type, from_account_id=None):
        """
        account_type: 'SAVINGS' or 'CHECKING' - passed through exactly
        as-is to match the dropdown's real option text. An earlier
        version applied .title() to this (producing 'Savings' instead
        of 'SAVINGS'), which caused select_option to time out since
        Playwright's label match is exact, not case-insensitive.
        from_account_id: which existing account funds the new one's
        opening balance. If not given, uses whatever the dropdown
        already has selected (usually the customer's first account).
        """
        self.page.select_option(self.ACCOUNT_TYPE_SELECT, label=account_type)
        if from_account_id:
            self.page.select_option(self.FROM_ACCOUNT_SELECT, label=from_account_id)
        self.page.click(self.OPEN_BUTTON)

    def get_new_account_id(self):
        self.page.wait_for_selector(self.NEW_ACCOUNT_ID)
        return self.page.locator(self.NEW_ACCOUNT_ID).inner_text()

    def is_account_opened(self):
        return self.page.locator(self.RESULT_TEXT).is_visible()
