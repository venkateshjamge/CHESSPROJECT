from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from dotenv import load_dotenv
import os
import time
import re

def get_last_move_number(pgn_text):
    moves_section = pgn_text.strip().split('\n\n', 1)[1].strip()
    move_numbers = re.findall(r'(\d+)\.', moves_section)
    if move_numbers:
        return int(move_numbers[-1])
    return None

def run_chess_analysis(pgn):
    load_dotenv()
    username = os.getenv("CHESS_USERNAME")
    password = os.getenv("CHESS_PASSWORD")

    print(f"Username from env: {username}")
    print(f"Password from env: {'*' * len(password) if password else None}")

    last_move_number = get_last_move_number(pgn)
    last_move_number = 2 * last_move_number

    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 20)
    driver.set_window_size(1920, 8080)
    driver.set_window_position(0, 0)
    # time.sleep(60)
    driver.get("https://www.chess.com/login")

    username_input = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//input[contains(@placeholder, 'Username') or contains(@name, 'username')]")
    ))
    username_input.send_keys(username)

    password_input = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "input[type='password']")
    ))
    password_input.send_keys(password)

    login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    login_button.click()

    print("Logged in successfully!")
    time.sleep(3)

    driver.get("https://www.chess.com/analysis")
    print("Navigating to analysis board...")
    time.sleep(5)

    textarea = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea.load-from-pgn-textarea")))
    textarea.clear()
    textarea.send_keys(pgn)

    button = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "button.cc-button-component.cc-button-primary.cc-button-medium.cc-bg-primary[type='button']")
    ))
    button.click()

    tab_container = wait.until(EC.presence_of_element_located((
        By.CSS_SELECTOR,
        "div.board-tab-container-component.sidebar-tabs-container[role='tablist']"
    )))

    tab_buttons = tab_container.find_elements(By.CSS_SELECTOR, "button.board-tab-item-component[role='tab']")

    for tab in tab_buttons:
        if "Review" in tab.text or tab.get_attribute("aria-selected") == "false":
            tab.click()
            print("Clicked the desired tab.")
            break
    else:
        print("Could not find the desired tab.")

    time.sleep(5)

    start_review_button = wait.until(EC.element_to_be_clickable((
        By.CSS_SELECTOR,
        "button.tab-review-start-review-button"
    )))

    time.sleep(3)
    start_review_button.click()
    print("Review Clicked")
    time.sleep(3)

    for move_num in range(0, last_move_number):
        explanation_selector = "div.bot-speech-content-component.bot-speech-content-bot-align-bottom.bot-speech-content-should-show-bot"
        explanation_div = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, explanation_selector)))
        old_explanation_text = explanation_div.text.strip()

        try:
            next_move_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Next Move']")))
            driver.execute_script("arguments[0].scrollIntoView(true);", next_move_btn)
            next_move_btn.click()
        except TimeoutException:
            print(f"❌ Could not find 'Next Move' button on move {move_num}. Skipping...")
            continue

        try:
            wait.until(lambda d: d.find_element(By.CSS_SELECTOR, explanation_selector).text.strip() != old_explanation_text)
            print(f"Explanation updated for move {move_num}")
        except TimeoutException:
            print(f"Timeout waiting for explanation update after move {move_num}. Maybe text didn't change.")

        time.sleep(3)

    time.sleep(10)
    driver.quit()

if __name__ == "__main__":
    pgn = """
    [Event "Fool's Mate"]
    [Site "?"]
    [Date "????.??.??"]
    [Round "?"]
    [White "White"]
    [Black "Black"]
    [Result "0-1"]

    1. f3 e5 2. g4 Qh4#
    """
    run_chess_analysis(pgn)
