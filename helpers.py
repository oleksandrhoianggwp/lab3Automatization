"""Shared helpers for OrangeHRM Selenium lab scripts."""
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "https://opensource-demo.orangehrmlive.com"
LOGIN_URL = f"{BASE_URL}/web/index.php/auth/login"
DEFAULT_TIMEOUT = 20


def build_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(options=options)
    return driver


def wait_visible(driver, locator, timeout=DEFAULT_TIMEOUT):
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located(locator)
    )


def wait_clickable(driver, locator, timeout=DEFAULT_TIMEOUT):
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable(locator)
    )


def wait_all_visible(driver, locator, timeout=DEFAULT_TIMEOUT):
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_all_elements_located(locator)
    )


def safe_click(driver, element):
    try:
        element.click()
    except Exception:
        driver.execute_script("arguments[0].click();", element)


def login(driver, username="Admin", password="admin123"):
    driver.get(LOGIN_URL)
    wait_visible(driver, (By.NAME, "username")).send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    wait_visible(driver, (By.CSS_SELECTOR, ".oxd-topbar-header"))


def click_side_menu(driver, name):
    locator = (By.XPATH, f"//aside//span[normalize-space()='{name}']/ancestor::a")
    el = wait_clickable(driver, locator)
    safe_click(driver, el)


def read_records_found(driver, timeout=DEFAULT_TIMEOUT):
    locator = (
        By.XPATH,
        "//span[contains(@class,'oxd-text') and contains(text(),'Records Found')]",
    )
    el = wait_visible(driver, locator, timeout)
    match = re.search(r"\((\d+)\)", el.text)
    if not match:
        raise RuntimeError(f"Cannot parse records-found text: {el.text!r}")
    return int(match.group(0).strip("()"))


def select_oxd_dropdown(driver, label_text, option_text):
    """Open a non-native OrangeHRM dropdown by its label and pick an option."""
    field = wait_visible(
        driver,
        (
            By.XPATH,
            f"//label[normalize-space()='{label_text}']"
            "/ancestor::div[contains(@class,'oxd-input-group')]"
            "//div[contains(@class,'oxd-select-text')]",
        ),
    )
    safe_click(driver, field)
    option = wait_clickable(
        driver,
        (
            By.XPATH,
            f"//div[@role='listbox']//span[normalize-space()='{option_text}']",
        ),
    )
    safe_click(driver, option)


def fill_input_by_label(driver, label_text, value):
    inp = wait_visible(
        driver,
        (
            By.XPATH,
            f"//label[normalize-space()='{label_text}']"
            "/ancestor::div[contains(@class,'oxd-input-group')]//input",
        ),
    )
    inp.clear()
    inp.send_keys(value)
    return inp
