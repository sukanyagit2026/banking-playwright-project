import os
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


@pytest.fixture(autouse=True)
def increase_timeout_in_ci(page):
    """
    We confirmed via direct comparison that a cluster of tests
    (Transfer Funds, Update Contact Info, Visual Regression) fail with
    element timeouts consistently in GitHub Actions CI, while passing
    instantly and reliably when run locally against the exact same
    live ParaBank server. This points to CI's network path to
    ParaBank's small public demo server being slower/less reliable
    than a typical home connection - not a bug in the test logic
    itself. Rather than guess at the exact network cause, we give
    every action more patience specifically in CI, where
    Playwright's default is 30 seconds.
    """
    if os.environ.get("CI"):
        page.set_default_timeout(60000)


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

    Registration is used by nearly every stateful test, so ParaBank's
    /register.htm endpoint gets hit far more often than any other page
    across a full CI run. Evidence from real CI runs showed this
    specific step failing more consistently than other pages even
    after raising the global CI timeout - so it gets its own targeted
    retry loop here, rather than relying only on pytest re-running the
    entire test (which is slower and less precise, since it also
    re-runs everything else in the test, not just the flaky step).
    """
    register_page = RegisterPage(page)
    last_error = None
    for attempt in range(3):
        try:
            register_page.load()
            register_page.register(random_customer)
            page.wait_for_selector(register_page.SUCCESS_TEXT, timeout=60000)
            return random_customer
        except Exception as error:
            # Honest caveat: if the first attempt actually succeeded
            # server-side but we simply didn't see the confirmation in
            # time, retrying with the same username could hit a
            # "username already exists" error instead of a clean
            # success. This is an acceptable tradeoff for a test
            # fixture (worst case, this fixture fails clearly rather
            # than silently), but worth knowing about.
            last_error = error
    raise last_error


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
