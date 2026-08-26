from pages.base_page import BasePage


class LoginPage(BasePage):
    """Represents the ParaBank homepage / customer login box at /index.htm."""

    USERNAME_INPUT = "input[name='username']"
    PASSWORD_INPUT = "input[name='password']"
    LOGIN_BUTTON = "input[value='Log In']"
    LOGIN_ERROR = "text=The username and password could not be verified."
    REGISTER_LINK = "a:has-text('Register')"

    def load(self):
        self.go_to("index.htm")

    def login(self, username, password):
        self.page.fill(self.USERNAME_INPUT, username)
        self.page.fill(self.PASSWORD_INPUT, password)
        self.page.click(self.LOGIN_BUTTON)

    def click_register(self):
        self.page.click(self.REGISTER_LINK)

    def has_login_error(self):
        return self.page.locator(self.LOGIN_ERROR).is_visible()


class RegisterPage(BasePage):
    """
    Represents /register.htm - the new customer signup form.
    NOTE: ParaBank's form field names follow a Java/Struts convention
    (e.g. 'customer.firstName') rather than modern data-qa attributes.
    This is common in older enterprise apps, and part of why registering
    a fresh customer per test (rather than reusing a shared login) is
    the safer, more deterministic approach for a banking demo.
    """

    FIRST_NAME = "input[name='customer.firstName']"
    LAST_NAME = "input[name='customer.lastName']"
    ADDRESS_STREET = "input[name='customer.address.street']"
    ADDRESS_CITY = "input[name='customer.address.city']"
    ADDRESS_STATE = "input[name='customer.address.state']"
    ADDRESS_ZIP = "input[name='customer.address.zipCode']"
    PHONE_NUMBER = "input[name='customer.phoneNumber']"
    SSN = "input[name='customer.ssn']"
    USERNAME = "input[name='customer.username']"
    PASSWORD = "input[name='customer.password']"
    CONFIRM_PASSWORD = "input[name='repeatedPassword']"
    REGISTER_BUTTON = "input[value='Register']"
    SUCCESS_TEXT = "text=Your account was created successfully"
    ERROR_USERNAME_TAKEN = "text=This username already exists"

    def load(self):
        self.go_to("register.htm")

    def register(self, user):
        """
        'user' is a dictionary (see the random_customer fixture) so a
        test can build one full registration form fill in one call,
        the same pattern used for the signup form in the e-commerce
        project.
        """
        self.page.fill(self.FIRST_NAME, user["first_name"])
        self.page.fill(self.LAST_NAME, user["last_name"])
        self.page.fill(self.ADDRESS_STREET, user["street"])
        self.page.fill(self.ADDRESS_CITY, user["city"])
        self.page.fill(self.ADDRESS_STATE, user["state"])
        self.page.fill(self.ADDRESS_ZIP, user["zip_code"])
        self.page.fill(self.PHONE_NUMBER, user["phone"])
        self.page.fill(self.SSN, user["ssn"])
        self.page.fill(self.USERNAME, user["username"])
        self.page.fill(self.PASSWORD, user["password"])
        self.page.fill(self.CONFIRM_PASSWORD, user["password"])
        self.page.click(self.REGISTER_BUTTON)

    def is_registration_successful(self):
        return self.page.locator(self.SUCCESS_TEXT).is_visible()
