# ParaBank - Full Banking Test Automation Framework (Playwright + Python)

A comprehensive Playwright + pytest project testing [ParaBank](https://parabank.parasoft.com/parabank/index.htm) - a real banking demo application built by Parasoft specifically for test automation practice (it is explicitly *not* a real bank, and is designed to be hammered by automated tests from all over the world).

## Why ParaBank instead of an e-commerce site

If you've already built the `big-playwright-project` (automationexercise.com), this project is its banking-domain companion. ParaBank gives you real banking modules that a shopping site simply can't: account balances, fund transfers, bill payments, loan approval logic, and a proper REST API - all designed for exactly this kind of practice.

## Project structure

```
banking-playwright-project/
├── pages/
│   ├── base_page.py              # Shared base class + left-nav menu helper
│   ├── login_page.py             # LoginPage, RegisterPage
│   ├── accounts_page.py          # AccountsOverviewPage, OpenNewAccountPage
│   ├── transfer_billpay_page.py  # TransferFundsPage, BillPayPage
│   └── misc_pages.py             # FindTransactionsPage, UpdateContactInfoPage, RequestLoanPage
├── tests/
│   ├── conftest.py                    # Fixtures: random_customer, registered_customer, first_account_id, random_payee, demo_login
│   ├── test_login_registration.py     # Login (demo account + negative) and new customer registration
│   ├── test_accounts.py               # Accounts Overview + Open New Account (data-driven: SAVINGS/CHECKING)
│   ├── test_transfer_funds.py         # Full transfer flow with real balance verification
│   ├── test_bill_pay.py               # Bill payment + negative mismatched-account test
│   ├── test_find_transactions.py      # Search by amount, including a "no results" case
│   ├── test_update_contact_info.py    # Profile update with persistence verification
│   ├── test_request_loan.py           # Loan approval and denial logic
│   ├── test_api.py                    # REST API tests - login, accounts, transactions
│   └── test_visual.py                 # Visual regression on login box and accounts table
├── .github/workflows/playwright.yml   # CI/CD - sequential cross-browser matrix
├── pytest.ini
├── requirements.txt
└── .gitignore
```

## Banking modules covered

| Module | What's tested |
|---|---|
| **Login** | Demo account login, invalid credentials |
| **Registration** | New customer signup, duplicate username rejection |
| **Accounts Overview** | Account listing, balance parsing |
| **Open New Account** | SAVINGS and CHECKING account creation (data-driven) |
| **Transfer Funds** | Full money-movement flow with real balance math verification |
| **Bill Pay** | Successful payment + account-verification mismatch rejection |
| **Find Transactions** | Search by amount, including a genuine "no results" case |
| **Update Contact Info** | Profile field update with reload-and-verify persistence check |
| **Request Loan** | Approval and denial logic based on down payment vs. available funds |
| **REST API** | Login, account retrieval, transaction retrieval - no browser involved |
| **Visual Regression** | Login box and accounts table, pixel-compared per browser/OS |

## A key design decision: demo login vs. fresh registration

ParaBank's public demo login (`john` / `demo`) is shared by test suites from all over the world running simultaneously. This project uses that demo account **only for read-only tests** (login works, accounts overview loads) via the `demo_login` fixture.

**Every test that changes state** (opening accounts, transferring money, paying bills, requesting loans, updating a profile) instead uses the `registered_customer` fixture, which registers a **brand-new, unique customer** through the real UI first. This avoids any race conditions with other people's automated tests running against the same shared demo account at the same moment - a lesson learned from testing against shared, public, uncontrolled demo instances.

## Setup

```
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
playwright install
```

## Running tests

```
pytest                          # run everything
pytest -m ui                    # only browser/UI tests
pytest -m api                   # only API tests (fast, no browser)
pytest -m smoke                 # quick smoke subset
pytest tests/test_transfer_funds.py
pytest --headed --slowmo 500    # watch the browser slowly
```

## Visual regression - first-run behavior

The first time you run `pytest tests/test_visual.py`, it will **fail** and create baseline images (this is expected - see the comment block at the top of `test_visual.py`). Baselines are named per-browser-per-OS (e.g. `login_box-chromium-windows.png`) to avoid the cross-platform/cross-browser pixel mismatches documented in the companion e-commerce project.

## Playwright/pytest concepts demonstrated

- **Page Object Model** across 8 page classes
- **Fixtures with dependencies on other fixtures** (`registered_customer` → `first_account_id`)
- **`yield`-free vs. UI-driven setup** - contrasts with the e-commerce project's API-driven `registered_user` fixture, since ParaBank has no public customer-creation REST endpoint
- **Data-driven testing** (`@pytest.mark.parametrize` for SAVINGS/CHECKING account types)
- **Web-first assertions** (`expect(...).to_be_visible()`, `to_have_value()`)
- **Dropdown handling** (`select_option` by label for account selectors)
- **Real numeric assertions**, not just "success message appeared" (balance math verification after transfers/bill pay)
- **REST API testing** with `requests`, including dynamic ID lookup instead of hardcoded values
- **Visual regression testing**, browser-and-OS-aware baselines
- **Cross-browser CI** via a sequential GitHub Actions matrix

## Concepts intentionally NOT forced into this project

ParaBank doesn't naturally have file uploads, native JS dialogs, or iframe-based flows in its core screens, so those aren't included here - they're already covered in the companion `big-playwright-project` (automationexercise.com). Together, the two projects cover the full breadth of common Playwright testing scenarios.

## A note on locator accuracy

ParaBank's HTML structure has been stable for well over a decade (it's a mature, unmaintained-by-design demo app), and the locators here reflect that long-documented structure. If any locator doesn't match (e.g., after a rare Parasoft update), open the relevant page in a browser, right-click → Inspect, and update the constant at the top of the relevant page object - the rest of the test logic won't need to change.

## Ideas for extending this project

1. **SOAP API testing** - ParaBank also exposes a SOAP endpoint (`/services/ParaBank?wsdl`); try testing it with `zeep` alongside the REST tests
2. **Find Transactions by date range** - only "by amount" is implemented here; add the date-based search modes
3. **Admin panel testing** - ParaBank has a separate `/admin.htm` page for configuring the demo app's behavior (response time, error simulation)
4. **Parallel execution** - add `pytest-xdist` and compare runtime with `-n auto`
5. **Allure reporting** - richer visual reports than the built-in HTML report
