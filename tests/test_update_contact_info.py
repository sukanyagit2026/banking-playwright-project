import pytest
from playwright.sync_api import expect
from pages.misc_pages import UpdateContactInfoPage


@pytest.mark.ui
class TestUpdateContactInfo:

    def test_update_phone_number_succeeds(self, page, registered_customer):
        update_page = UpdateContactInfoPage(page)
        update_page.load()

        new_phone = "5551234567"
        update_page.update_phone_number(new_phone)

        expect(page.locator(update_page.SUCCESS_TEXT)).to_be_visible()

        # Reload the page and confirm the new value actually persisted -
        # this is what separates a real assertion from just trusting
        # a success message
        update_page.load()
        expect(page.locator(update_page.PHONE)).to_have_value(new_phone)
