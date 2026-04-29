"""Part 3: search Samuel in PIM, open profile, fill Contact Details."""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from helpers import (
    build_driver,
    login,
    click_side_menu,
    wait_visible,
    wait_clickable,
    safe_click,
    select_oxd_dropdown,
    DEFAULT_TIMEOUT,
)


def search_employee_by_name(driver, name):
    click_side_menu(driver, "PIM")
    wait_visible(driver, (By.CSS_SELECTOR, ".oxd-table-body"))

    name_input = wait_visible(
        driver,
        (
            By.XPATH,
            "//label[normalize-space()='Employee Name']"
            "/ancestor::div[contains(@class,'oxd-input-group')]//input",
        ),
    )
    name_input.clear()
    name_input.send_keys(name)

    option = WebDriverWait(driver, DEFAULT_TIMEOUT).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, ".oxd-autocomplete-option")
        )
    )
    safe_click(driver, option)

    search_btn = wait_clickable(
        driver, (By.XPATH, "//button[@type='submit' and normalize-space()='Search']")
    )
    safe_click(driver, search_btn)


def open_first_result_profile(driver):
    view_btn = wait_clickable(
        driver,
        (
            By.CSS_SELECTOR,
            ".oxd-table-body .oxd-table-card button.oxd-icon-button",
        ),
    )
    safe_click(driver, view_btn)
    WebDriverWait(driver, DEFAULT_TIMEOUT).until(
        EC.url_contains("/pim/viewPersonalDetails/empNumber/")
    )


def go_to_contact_details(driver):
    tab = wait_clickable(
        driver, (By.XPATH, "//a[normalize-space()='Contact Details']")
    )
    safe_click(driver, tab)
    wait_visible(
        driver, (By.XPATH, "//h6[normalize-space()='Contact Details']")
    )


def fill_contact_details(driver):
    inputs = WebDriverWait(driver, DEFAULT_TIMEOUT).until(
        EC.visibility_of_all_elements_located(
            (
                By.XPATH,
                "//h6[normalize-space()='Contact Details']"
                "/ancestor::form//input[@class[contains(., 'oxd-input')]]",
            )
        )
    )
    # The Contact Details form input order in OrangeHRM:
    # 0: Street 1, 1: Street 2, 2: City, 3: State/Province, 4: Zip/Postal Code,
    # then country dropdown (separate), then phones and emails.
    values_in_order = [
        "123 Main Street",        # Street 1
        "Apt 4B",                 # Street 2
        "Kyiv",                   # City
        "Kyiv Oblast",            # State/Province
        "01001",                  # Zip
    ]
    for inp, val in zip(inputs, values_in_order):
        inp.clear()
        inp.send_keys(val)

    select_oxd_dropdown(driver, "Country", "Ukraine")

    phone_emails = {
        "Home": "+380441234567",
        "Mobile": "+380501234567",
        "Work": "+380441112233",
        "Work Email": "samuel.white@example.com",
        "Other Email": "samuel.alt@example.com",
    }
    for label, value in phone_emails.items():
        field = WebDriverWait(driver, DEFAULT_TIMEOUT).until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    f"//label[normalize-space()='{label}']"
                    "/ancestor::div[contains(@class,'oxd-input-group')]//input",
                )
            )
        )
        field.clear()
        field.send_keys(value)

    save_btn = wait_clickable(
        driver,
        (
            By.XPATH,
            "//h6[normalize-space()='Contact Details']"
            "/ancestor::form//button[@type='submit']",
        ),
    )
    safe_click(driver, save_btn)


def main():
    driver = build_driver()
    try:
        login(driver)
        search_employee_by_name(driver, "Samuel")
        open_first_result_profile(driver)
        go_to_contact_details(driver)
        fill_contact_details(driver)
        print("Contact details saved")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
