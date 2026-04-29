"""Part 2: read names from JSON and add each as a new PIM employee."""
import json
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from helpers import (
    build_driver,
    login,
    click_side_menu,
    read_records_found,
    wait_visible,
    wait_clickable,
    safe_click,
    DEFAULT_TIMEOUT,
)

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "employees.json")


def load_employees():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def open_employee_list(driver):
    click_side_menu(driver, "PIM")
    wait_clickable(
        driver,
        (By.XPATH, "//a[normalize-space()='Employee List']"),
    )
    safe_click(
        driver,
        driver.find_element(By.XPATH, "//a[normalize-space()='Employee List']"),
    )
    wait_visible(driver, (By.CSS_SELECTOR, ".oxd-table-body"))


def add_employee(driver, first, middle, last):
    add_btn = wait_clickable(
        driver, (By.XPATH, "//button[normalize-space()='Add']")
    )
    safe_click(driver, add_btn)

    wait_visible(driver, (By.NAME, "firstName"))

    fn = driver.find_element(By.NAME, "firstName")
    mn = driver.find_element(By.NAME, "middleName")
    ln = driver.find_element(By.NAME, "lastName")
    fn.clear(); fn.send_keys(first)
    mn.clear(); mn.send_keys(middle)
    ln.clear(); ln.send_keys(last)

    save_btn = wait_clickable(
        driver, (By.XPATH, "//button[@type='submit' and normalize-space()='Save']")
    )
    safe_click(driver, save_btn)

    WebDriverWait(driver, DEFAULT_TIMEOUT).until(
        EC.url_contains("/pim/viewPersonalDetails/empNumber/")
    )


def main():
    employees = load_employees()
    print(f"Loaded {len(employees)} employees from {DATA_FILE}")

    driver = build_driver()
    try:
        login(driver)
        open_employee_list(driver)
        initial = read_records_found(driver)
        print(f"Initial Records Found in PIM: {initial}")

        for i, emp in enumerate(employees, start=1):
            print(f"[{i}/{len(employees)}] Adding {emp['firstName']} {emp['lastName']}...")
            add_employee(driver, emp["firstName"], emp["middleName"], emp["lastName"])
            open_employee_list(driver)

        try:
            final = read_records_found(driver)
        except TimeoutException:
            open_employee_list(driver)
            final = read_records_found(driver)

        print(f"Final Records Found in PIM: {final}")
        print(f"Added: {final - initial} (expected {len(employees)})")
        if final - initial != len(employees):
            print("WARNING: number of added employees does not match expected.")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
