import pytest
from playwright.sync_api import expect
from pages.login_page import LoginPage, RegisterPage


@pytest.mark.ui
@pytest.mark.smoke
class TestLogin:

    def test_login_page_loads(self, login_page):
        expect(login_page.page).to_have_url("https://parabank.parasoft.com/parabank/index.htm")

    def test_login_with_demo_account_succeeds(self, demo_login):
        # demo_login fixture already performed the login - this test
        # just confirms the post-login dashboard actually rendered
        expect(demo_login.locator("#leftPanel")).to_be_visible()
        expect(demo_login.get_by_role("heading", name="Accounts Overview")).to_be_visible()
    def test_login_with_invalid_credentials_shows_error(self, login_page):
        login_page.login("not_a_real_user_xyz", "wrongpassword123")
        expect(login_page.page.locator(login_page.LOGIN_ERROR)).to_be_visible()


@pytest.mark.ui
class TestRegistration:

    def test_register_new_customer_succeeds(self, page, random_customer):
        register_page = RegisterPage(page)
        register_page.load()
        register_page.register(random_customer)

        expect(page.locator(register_page.SUCCESS_TEXT)).to_be_visible()
        # A successful registration also logs the customer straight in
        expect(page.locator("#leftPanel")).to_be_visible()

    def test_register_with_duplicate_username_shows_error(self, page, random_customer):
        register_page = RegisterPage(page)
        register_page.load()
        register_page.register(random_customer)
        expect(page.locator(register_page.SUCCESS_TEXT)).to_be_visible()

        # Log out, then try registering a SECOND time with the exact
        # same username to trigger the uniqueness validation
        page.click("text=Log Out")
        register_page.load()
        register_page.register(random_customer)

        expect(page.locator(register_page.ERROR_USERNAME_TAKEN)).to_be_visible()
