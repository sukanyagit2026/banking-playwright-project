class BasePage:
    """
    Every page object inherits from this. Holds behavior common to
    every page in the app so individual page objects don't repeat it.
    """

    def __init__(self, page):
        self.page = page

    def go_to(self, path=""):
        self.page.goto(path)

    def get_title(self):
        return self.page.title()

    def is_visible(self, locator):
        return self.page.locator(locator).is_visible()

    def left_menu_link(self, text):
        """
        Every logged-in page in ParaBank shares the same left-hand
        navigation menu (Open New Account, Accounts Overview, Transfer
        Funds, Bill Pay, Find Transactions, Update Contact Info,
        Request Loan, Log Out). Centralizing it here means every page
        object gets free navigation without repeating the locator.
        """
        return self.page.locator(f"#leftPanel a:has-text('{text}')")

    def click_menu(self, text):
        self.left_menu_link(text).click()
