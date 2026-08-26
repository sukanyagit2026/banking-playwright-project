import pytest
from faker import Faker
from pages.login_page import LoginPage, RegisterPage
from pages.accounts_page import AccountsOverviewPage

fake = Faker()

# ParaBank's public, well-known demo account. It's intentionally shared
# and designed by Parasoft for exactly this kind of automation practice,
# so it's safe to use for READ-ONLY checks (login works, dashboard loads).
# We deliberately do NOT use it for anything that changes balances
# (transfers, bill pay, loans), since many people worldwide run
# automated tests against it at the same time - a fresh, unique
# customer per test avoids any race conditions or shared-state flakiness.
DEMO_USERNAME = "john"
DEMO_PASSWORD = "demo"


@pytest.fixture
def login_page(page):
    lp = LoginPage(page)
    lp.load()
    return lp


@pytest.fixture
def demo_login(page):
    """
    Logs in with ParaBank's public demo account. Use this ONLY for
    tests that just read data (accounts overview, find transactions)
    and never modify balances.
    """
    lp = LoginPage(page)
    lp.load()
    lp.login(DEMO_USERNAME, DEMO_PASSWORD)
    page.wait_for_selector("#leftPanel")
    return page


@pytest.fixture
def random_customer():
    """
    Generates a brand-new fake customer's registration details. A
    fresh customer every run avoids the 'username already exists'
    error and keeps every stateful test (transfers, loans, bill pay)
    fully isolated from every other test run, worldwide.
    """
    return {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "street": fake.street_address(),
        "city": fake.city(),
        "state": fake.state_abbr(),
        "zip_code": fake.postcode(),
        "phone": fake.numerify("##########"),
        "ssn": fake.numerify("###-##-####"),
        "username": f"{fake.user_name()}{fake.random_int(1000, 9999)}",
        "password": fake.password(length=10, special_chars=False),
    }


@pytest.fixture
def registered_customer(page, random_customer):
    """
    Registers a fresh customer through the real UI (there's no simple
    public REST endpoint for account creation on ParaBank, unlike the
    e-commerce project's API-based fixture) and leaves them logged in,
    with one auto-created CHECKING account ready to use. This is the
    fixture most stateful tests (transfer, bill pay, loan, open
    account) depend on.
    """
    register_page = RegisterPage(page)
    register_page.load()
    register_page.register(random_customer)
    page.wait_for_selector(register_page.SUCCESS_TEXT)
    return random_customer


@pytest.fixture
def first_account_id(page, registered_customer):
    """
    Returns the account number of the single CHECKING account that
    ParaBank automatically creates when a new customer registers.
    Several tests (transfer, bill pay, loan) need a valid 'from'
    account, so this fixture saves every test from re-navigating to
    the overview page just to read one number.
    """
    overview = AccountsOverviewPage(page)
    overview.load()
    ids = overview.get_account_ids()
    return ids[0]


@pytest.fixture
def random_payee():
    """Generates fake external payee details for Bill Pay tests."""
    return {
        "name": fake.company(),
        "street": fake.street_address(),
        "city": fake.city(),
        "state": fake.state_abbr(),
        "zip_code": fake.postcode(),
        "phone": fake.numerify("##########"),
        "account_number": fake.numerify("########"),
        "amount": 25.00,
    }
