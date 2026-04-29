"""Part 1: login, open Admin, print Records Found and counts of Admin/ESS roles."""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

from helpers import (
    build_driver,
    login,
    click_side_menu,
    read_records_found,
    wait_visible,
    safe_click,
    DEFAULT_TIMEOUT,
)


def count_roles_on_current_page(driver):
    rows = WebDriverWait(driver, DEFAULT_TIMEOUT).until(
        EC.visibility_of_all_elements_located(
            (By.CSS_SELECTOR, ".oxd-table-body .oxd-table-card")
        )
    )
    admin = ess = 0
    for row in rows:
        try:
            cells = row.find_elements(By.CSS_SELECTOR, "div[role='cell']")
            if len(cells) < 3:
                continue
            role = cells[2].text.strip()
            if role == "Admin":
                admin += 1
            elif role == "ESS":
                ess += 1
        except StaleElementReferenceException:
            continue
    return admin, ess


def go_to_next_page_if_any(driver):
    next_buttons = driver.find_elements(
        By.CSS_SELECTOR, "button.oxd-pagination-page-item--previous-next"
    )
    next_btn = next_buttons[-1] if next_buttons else None
    if next_btn and next_btn.is_enabled():
        safe_click(driver, next_btn)
        return True
    return False


def main():
    driver = build_driver()
    try:
        login(driver)
        click_side_menu(driver, "Admin")
        wait_visible(driver, (By.CSS_SELECTOR, ".oxd-table-body"))

        records = read_records_found(driver)
        print(f"Records Found: {records}")

        admin_total = ess_total = 0
        while True:
            a, e = count_roles_on_current_page(driver)
            admin_total += a
            ess_total += e
            try:
                if not go_to_next_page_if_any(driver):
                    break
                wait_visible(driver, (By.CSS_SELECTOR, ".oxd-table-body"))
            except TimeoutException:
                break

        print(f"Admin: {admin_total}, ESS: {ess_total}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
