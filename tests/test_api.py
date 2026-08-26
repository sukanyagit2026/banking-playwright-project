import pytest
import requests

API_BASE_URL = "https://parabank.parasoft.com/parabank/services/bank"

# NOTE ON THIS FILE: ParaBank's REST API endpoints and parameter names
# are documented via its own WADL at
# https://parabank.parasoft.com/parabank/services/bank?_wadl&_type=xml
# If any of these tests fail with an unexpected 404/400, check that
# URL first - it's the authoritative source of truth for exact
# endpoint paths, since this reflects the live server's own routes.


def _get_demo_customer_id():
    """
    Fetches John's customer id dynamically via the login endpoint,
    rather than hardcoding a guessed id - this keeps the test suite
    correct even if the public demo data ever gets reset or renumbered.
    """
    response = requests.get(
        f"{API_BASE_URL}/login/john/demo",
        headers={"Accept": "application/json"},
    )
    return response.json()["id"]


@pytest.mark.api
class TestLoginAPI:

    def test_login_with_valid_demo_credentials_returns_customer(self):
        # IMPORTANT: ParaBank's login endpoint takes username/password as
        # PATH segments (/login/{username}/{password}), not query
        # parameters - confirmed directly from ParaBank's own source code
        # (ParaBankService.java). This is different from many REST APIs
        # (including the automationexercise.com one from the companion
        # project), which is exactly the kind of assumption worth
        # double-checking rather than copying blindly between projects.
        response = requests.get(
            f"{API_BASE_URL}/login/john/demo",
            headers={"Accept": "application/json"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["firstName"] == "John"

    def test_login_with_invalid_credentials_fails(self):
        response = requests.get(
            f"{API_BASE_URL}/login/not_a_real_user/wrongpass",
            headers={"Accept": "application/json"},
        )
        # ParaBank's API returns a non-200 (typically 500, since it
        # raises ParaBankServiceException server-side) for bad
        # credentials rather than a 200 with an error payload
        assert response.status_code != 200


@pytest.mark.api
class TestCustomerAPI:

    def test_get_customer_details(self):
        customer_id = _get_demo_customer_id()
        response = requests.get(
            f"{API_BASE_URL}/customers/{customer_id}",
            headers={"Accept": "application/json"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["firstName"] == "John"
        assert data["id"] == customer_id


@pytest.mark.api
class TestAccountsAPI:

    def test_get_accounts_for_demo_customer(self):
        customer_id = _get_demo_customer_id()
        response = requests.get(
            f"{API_BASE_URL}/customers/{customer_id}/accounts",
            headers={"Accept": "application/json"},
        )
        assert response.status_code == 200
        accounts = response.json()
        assert len(accounts) > 0
        assert "id" in accounts[0]
        assert "balance" in accounts[0]

    def test_get_single_account_details(self):
        customer_id = _get_demo_customer_id()
        accounts_response = requests.get(
            f"{API_BASE_URL}/customers/{customer_id}/accounts",
            headers={"Accept": "application/json"},
        )
        account_id = accounts_response.json()[0]["id"]

        response = requests.get(
            f"{API_BASE_URL}/accounts/{account_id}",
            headers={"Accept": "application/json"},
        )
        assert response.status_code == 200
        assert response.json()["id"] == account_id

    def test_get_account_with_invalid_id_fails(self):
        response = requests.get(
            f"{API_BASE_URL}/accounts/0",
            headers={"Accept": "application/json"},
        )
        assert response.status_code != 200


@pytest.mark.api
class TestTransactionsAPI:

    def test_get_transactions_for_an_account(self):
        customer_id = _get_demo_customer_id()
        accounts_response = requests.get(
            f"{API_BASE_URL}/customers/{customer_id}/accounts",
            headers={"Accept": "application/json"},
        )
        account_id = accounts_response.json()[0]["id"]

        response = requests.get(
            f"{API_BASE_URL}/accounts/{account_id}/transactions/amount/0",
            headers={"Accept": "application/json"},
        )
        # A 200 with a (possibly empty) list is the expected shape,
        # even if this particular account has no $0 transactions
        assert response.status_code == 200
        assert isinstance(response.json(), list)
