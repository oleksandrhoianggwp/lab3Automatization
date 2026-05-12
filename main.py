"""Combined Selenium lab script for all three OrangeHRM tasks."""
import json
import os
import random

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers import (
    DEFAULT_TIMEOUT,
    build_driver,
    click_side_menu,
    fill_input_by_label,
    login,
    read_records_found,
    safe_click,
    select_oxd_dropdown,
    wait_clickable,
    wait_visible,
)

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "employees.json")
SAVE_TIMEOUT = 60


def make_employee_id():
    return str(random.randint(10000000, 99999999))


def collect_validation_messages(driver):
    return [
        item.text.strip()
        for item in driver.find_elements(By.CSS_SELECTOR, ".oxd-input-field-error-message")
        if item.text.strip()
    ]


def load_employees():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def wait_for_table(driver):
    return wait_visible(driver, (By.CSS_SELECTOR, ".oxd-table-body"))


def count_admin_roles(driver):
    click_side_menu(driver, "Admin")
    WebDriverWait(driver, DEFAULT_TIMEOUT).until(
        EC.url_contains("/admin/viewSystemUsers")
    )
    wait_for_table(driver)

    records = read_records_found(driver)
    print(f"Admin Records Found: {records}")

    admin_total = 0
    ess_total = 0

    while True:
        rows = WebDriverWait(driver, DEFAULT_TIMEOUT).until(
            EC.visibility_of_all_elements_located(
                (By.CSS_SELECTOR, ".oxd-table-body .oxd-table-card")
            )
        )

        for row in rows:
            cells = row.find_elements(By.CSS_SELECTOR, "div[role='cell']")
            if len(cells) < 3:
                continue

            role = cells[2].text.strip()
            if role == "Admin":
                admin_total += 1
            elif role == "ESS":
                ess_total += 1

        if not go_to_next_page(driver):
            break

    print(f"Admin users: {admin_total}")
    print(f"ESS users: {ess_total}")


def go_to_next_page(driver):
    buttons = driver.find_elements(
        By.CSS_SELECTOR, "button.oxd-pagination-page-item--previous-next"
    )
    if not buttons:
        return False

    next_button = buttons[-1]
    classes = next_button.get_attribute("class") or ""
    if "disabled" in classes or next_button.get_attribute("disabled"):
        return False

    first_row = None
    rows = driver.find_elements(By.CSS_SELECTOR, ".oxd-table-body .oxd-table-card")
    if rows:
        first_row = rows[0]

    safe_click(driver, next_button)
    if first_row:
        WebDriverWait(driver, DEFAULT_TIMEOUT).until(EC.staleness_of(first_row))
    wait_for_table(driver)
    return True


def open_employee_list(driver):
    click_side_menu(driver, "PIM")
    WebDriverWait(driver, DEFAULT_TIMEOUT).until(EC.url_contains("/pim/"))
    employee_list = wait_clickable(
        driver, (By.XPATH, "//a[normalize-space()='Employee List']")
    )
    safe_click(driver, employee_list)
    WebDriverWait(driver, DEFAULT_TIMEOUT).until(
        EC.url_contains("/pim/viewEmployeeList")
    )
    wait_for_table(driver)


def click_search_and_wait(driver):
    old_rows = driver.find_elements(By.CSS_SELECTOR, ".oxd-table-body .oxd-table-card")
    old_first_row = old_rows[0] if old_rows else None
    search_button = wait_clickable(
        driver, (By.XPATH, "//button[@type='submit' and normalize-space()='Search']")
    )
    safe_click(driver, search_button)

    if old_first_row:
        try:
            WebDriverWait(driver, DEFAULT_TIMEOUT).until(EC.staleness_of(old_first_row))
        except TimeoutException:
            pass
    wait_for_table(driver)


def add_employee(driver, employee, employee_id):
    add_button = wait_clickable(driver, (By.XPATH, "//button[normalize-space()='Add']"))
    safe_click(driver, add_button)

    first_name = wait_visible(driver, (By.NAME, "firstName"))
    middle_name = driver.find_element(By.NAME, "middleName")
    last_name = driver.find_element(By.NAME, "lastName")

    first_name.clear()
    first_name.send_keys(employee["firstName"])
    middle_name.clear()
    middle_name.send_keys(employee["middleName"])
    last_name.clear()
    last_name.send_keys(employee["lastName"])
    fill_input_by_label(driver, "Employee Id", employee_id)

    for attempt in range(1, 4):
        if "/pim/viewPersonalDetails/empNumber/" in driver.current_url:
            return employee_id

        save_button = wait_clickable(
            driver, (By.XPATH, "//button[@type='submit' and normalize-space()='Save']")
        )
        safe_click(driver, save_button)

        try:
            WebDriverWait(driver, SAVE_TIMEOUT).until(
                lambda active_driver: "/pim/viewPersonalDetails/empNumber/"
                in active_driver.current_url
                or collect_validation_messages(active_driver)
            )
        except TimeoutException:
            if attempt < 3:
                print(f"Save did not finish, retrying ({attempt}/3)...")
                continue
            raise RuntimeError(
                f"Employee was not saved: {employee['firstName']} "
                f"{employee['lastName']} with Employee Id {employee_id}."
            )

        if "/pim/viewPersonalDetails/empNumber/" in driver.current_url:
            return employee_id

        messages = collect_validation_messages(driver)
        if attempt < 3:
            employee_id = make_employee_id()
            print(f"Save validation failed {messages}; retrying with ID {employee_id}")
            fill_input_by_label(driver, "Employee Id", employee_id)
            continue

        raise RuntimeError(
            f"Employee was not saved: {employee['firstName']} "
            f"{employee['lastName']} with Employee Id {employee_id}. "
            f"Validation messages: {messages}"
        )


def add_employees_from_file(driver):
    employees = load_employees()
    employee_ids = {}
    open_employee_list(driver)
    initial_count = read_records_found(driver)
    print(f"PIM Records Found before adding: {initial_count}")

    for index, employee in enumerate(employees, start=1):
        full_name = (
            f"{employee['firstName']} {employee['middleName']} {employee['lastName']}"
        )
        employee_id = make_employee_id()
        print(f"Adding employee {index}/{len(employees)}: {full_name} ({employee_id})")
        employee_id = add_employee(driver, employee, employee_id)
        employee_ids[full_name] = employee_id
        open_employee_list(driver)

    final_count = read_records_found(driver)
    added_count = final_count - initial_count
    print(f"PIM Records Found after adding: {final_count}")
    print(f"Added employees: {added_count} (expected {len(employees)})")

    if added_count != len(employees):
        print("WARNING: global Records Found changed by a different amount.")

    verify_added_employees(driver, employee_ids)

    return employee_ids


def verify_added_employees(driver, employee_ids):
    verified = 0
    for full_name, employee_id in employee_ids.items():
        open_employee_list(driver)
        fill_input_by_label(driver, "Employee Id", employee_id)
        click_search_and_wait(driver)

        rows = driver.find_elements(By.CSS_SELECTOR, ".oxd-table-body .oxd-table-card")
        if rows:
            verified += 1
        else:
            print(f"WARNING: added employee was not found by ID: {full_name}")

    print(f"Verified added employees by ID: {verified}/{len(employee_ids)}")


def search_employee(driver, name, employee_id=None):
    open_employee_list(driver)

    employee_name = wait_visible(
        driver,
        (
            By.XPATH,
            "//label[normalize-space()='Employee Name']"
            "/ancestor::div[contains(@class,'oxd-input-group')]//input",
        ),
    )
    employee_name.clear()
    employee_name.send_keys(name)

    option = wait_clickable(driver, (By.CSS_SELECTOR, ".oxd-autocomplete-option"))
    safe_click(driver, option)

    if employee_id:
        fill_input_by_label(driver, "Employee Id", employee_id)

    click_search_and_wait(driver)


def open_first_employee_profile(driver):
    edit_button = wait_clickable(
        driver,
        (
            By.XPATH,
            "//div[contains(@class,'oxd-table-body')]"
            "//i[contains(@class,'bi-pencil-fill')]/ancestor::button[1]",
        ),
    )
    safe_click(driver, edit_button)
    WebDriverWait(driver, DEFAULT_TIMEOUT).until(
        EC.url_contains("/pim/viewPersonalDetails/empNumber/")
    )


def fill_samuel_contact_details(driver, employee_id=None):
    search_employee(driver, "Samuel", employee_id)
    open_first_employee_profile(driver)

    contact_tab = wait_clickable(
        driver, (By.XPATH, "//a[normalize-space()='Contact Details']")
    )
    safe_click(driver, contact_tab)
    wait_visible(driver, (By.XPATH, "//h6[normalize-space()='Contact Details']"))

    fill_input_by_label(driver, "Street 1", "123 Main Street")
    fill_input_by_label(driver, "Street 2", "Apt 4B")
    fill_input_by_label(driver, "City", "Kyiv")
    fill_input_by_label(driver, "State/Province", "Kyiv Oblast")
    fill_input_by_label(driver, "Zip/Postal Code", "01001")
    select_oxd_dropdown(driver, "Country", "Ukraine")
    fill_input_by_label(driver, "Home", "+380441234567")
    fill_input_by_label(driver, "Mobile", "+380501234567")
    fill_input_by_label(driver, "Work", "+380441112233")
    fill_input_by_label(driver, "Work Email", "samuel.white@example.com")
    fill_input_by_label(driver, "Other Email", "samuel.alt@example.com")

    save_button = wait_clickable(
        driver,
        (By.XPATH, "//button[@type='submit' and normalize-space()='Save']"),
    )
    safe_click(driver, save_button)

    try:
        wait_visible(driver, (By.XPATH, "//*[contains(.,'Successfully Saved')]"), 10)
    except TimeoutException:
        pass

    print("Samuel contact details saved")


def main():
    driver = build_driver()
    try:
        login(driver)

        print("\n--- Part 1 ---")
        count_admin_roles(driver)

        print("\n--- Part 2 ---")
        employee_ids = add_employees_from_file(driver)

        print("\n--- Part 3 ---")
        fill_samuel_contact_details(driver, employee_ids.get("Samuel Caleb White"))
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
