from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os
import time
import re

# Load environment variables
load_dotenv()
username = os.getenv("CHESS_USERNAME")
password = os.getenv("CHESS_PASSWORD")

print(f"Username from env: {username}")
print(f"Password from env: {'*' * len(password) if password else None}")


pgn= """
[Event "Fool's Mate"]
[Site "?"]
[Date "????.??.??"]
[Round "?"]
[White "White"]
[Black "Black"]
[Result "0-1"]

1. f3 e5 2. g4 Qh4#
"""
# PGN to analyze
pgn1 = """
[Event "Kasparov Immortal"]
[Site "Wijk aan Zee"]
[Date "1999.01.20"]
[Round "?"]
[White "Kasparov, Garry"]
[Black "Topalov, Veselin"]
[Result "1-0"]
1.e4 d6 2.d4 Nf6 3.Nc3 g6 4.Be3 Bg7 5.Qd2 c6 6.f3 b5 7.Nge2 Nbd7
8.Bh6 Bxh6 9.Qxh6 Bb7 10.a3 e5 11.O-O-O Qe7 12.Kb1 a6 13.Nc1 O-O-O
14.Nb3 exd4 15.Rxd4 c5 16.Rd1 Nb6 17.g3 Kb8 18.Na5 Ba8 19.Bh3 d5
20.Qf4+ Ka7 21.Rhe1 d4 22.Nd5 Nbxd5 23.exd5 Qd6 24.Rxd4!! cxd4
25.Re7+!! Kb6 26.Qxd4+ Kxa5 27.b4+ Ka4 28.Qc3 Qxd5 29.Ra7 Bb7
30.Rxb7 Qc4 31.Qxf6 Kxa3 32.Qxa6+ Kxb4 33.c3+ Kxc3 34.Qa1+ Kd2
35.Qb2+ Kd1 36.Bf1!! Rd2 37.Rd7 Rxd7 38.Bxc4 bxc4 39.Qxh8 Rd3
40.Qa8 c3 41.Qa4+ Ke1 42.f4 f5 43.Kc1 Kf2 44.Qa7+ Kg2 45.Qxh7
Rd6 46.Qc7 Rd3 47.Qc6+ Kxh2 48.Qxg6 Kg2 49.Qxf5 Rf3 50.g4 Kg3
51.g5 Rf2 52.g6 c2 53.g7 1-0
"""
def get_last_move_number(pgn_text):
    # Extract the moves part (skip PGN tags)
    moves_section = pgn_text.strip().split('\n\n', 1)[1].strip()
    
    # Find all occurrences of move numbers in the moves section
    move_numbers = re.findall(r'(\d+)\.', moves_section)
    
    if move_numbers:
        return int(move_numbers[-1])
    else:
        return None

last_move_number = get_last_move_number(pgn)

# Start browser and login
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 20)

driver.get("https://www.chess.com/login")

# Enter username
username_input = wait.until(EC.presence_of_element_located(
    (By.XPATH, "//input[contains(@placeholder, 'Username') or contains(@name, 'username')]")
))
username_input.send_keys(username)

# Enter password
password_input = wait.until(EC.presence_of_element_located(
    (By.CSS_SELECTOR, "input[type='password']")
))
password_input.send_keys(password)

# Click login
login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
login_button.click()

print(" Logged in successfully!")
time.sleep(3)
# Navigate to analysis board
driver.get("https://www.chess.com/analysis")
print(" Navigating to analysis board...")
time.sleep(5)

textarea = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea.load-from-pgn-textarea")))
textarea.clear()
textarea.send_keys(pgn)

button = wait.until(EC.element_to_be_clickable(
    (By.CSS_SELECTOR, "button.cc-button-component.cc-button-primary.cc-button-medium.cc-bg-primary[type='button']")
))
button.click()

# Step 1: Wait for the tab container to be present
tab_container = wait.until(EC.presence_of_element_located((
    By.CSS_SELECTOR,
    "div.board-tab-container-component.sidebar-tabs-container[role='tablist']"
)))

# Step 2: Find the desired tab inside the container
tab_buttons = tab_container.find_elements(By.CSS_SELECTOR, "button.board-tab-item-component[role='tab']")

# Step 3: Click the correct tab (first inactive one, or matching text)
for tab in tab_buttons:
    if "Review" in tab.text or tab.get_attribute("aria-selected") == "false":
        tab.click()
        print("Clicked the desired tab.")
        break
else:
    print("Could not find the desired tab.")

time.sleep(5)

# Wait for the "Start Review" button to be clickable
start_review_button = wait.until(EC.element_to_be_clickable((
    By.CSS_SELECTOR,
    "button.tab-review-start-review-button"
)))

# Click the button
time.sleep(3)
start_review_button.click()
print("Reivew Clicked")
time.sleep(3)
for move_num in range(0, last_move_number + 1):
    explanation_selector = "div.bot-speech-content-component.bot-speech-content-bot-align-bottom.bot-speech-content-should-show-bot"
    
    # Wait until explanation div is present and get its text
    explanation_div = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, explanation_selector)))
    old_explanation_text = explanation_div.text.strip()

    # Wait for Next Move button to be clickable
    next_move_btn = wait.until(EC.element_to_be_clickable((
        By.CSS_SELECTOR,
        "button.cc-button-component.cc-button-secondary.cc-button-large.cc-bg-secondary.cc-button-full[aria-label='Next Move']"
    )))

    next_move_btn.click()
    print(f"Clicked Next Move button for move {move_num}")

    try:
        # Wait until explanation text changes OR timeout after 10 seconds
        wait.until(lambda driver: driver.find_element(By.CSS_SELECTOR, explanation_selector).text.strip() != old_explanation_text)
        print(f"Explanation updated for move {move_num}")
    except TimeoutException:
        print(f"Timeout waiting for explanation update after move {move_num}. Maybe text didn't change.")

    # Optional short pause to stabilize UI
    time.sleep(3)




# # logic to hit the great moves:
# # JavaScript to access elements inside <wc-move-list>'s shadow root and filter by <g id="great_find">
# # === NEW: wait for wc-move-list and its shadowRoot to be ready ===
# wait.until(lambda d: d.execute_script("""
#   const el = document.querySelector('wc-move-list.move-by-move-move-list');
#   return el && el.shadowRoot !== null;
# """))

# # logic to hit the great moves:
# great_moves = driver.execute_script("""
# const wcMoveList = document.querySelector("wc-move-list.move-by-move-move-list");
# if (!wcMoveList) return [];

# const shadow = wcMoveList.shadowRoot;
# if (!shadow) return [];

# const rows = shadow.querySelectorAll(".main-line-row");
# let results = [];

# rows.forEach(row => {
#     const iconSvg = row.querySelector("span.node-annotation-icon svg g#great_find");
#     if (iconSvg) {
#         const moveSpan = row.querySelector("span.node-highlight-content.selected");
#         if (moveSpan) {
#             results.push(moveSpan.textContent.trim());
#         }
#     }
# });

# return results;
# """)

# print("✨ Great Moves:")
# for move in great_moves:
#     print(f"➤ {move}")

# print("✅ PGN loaded and analysis started.")
time.sleep(10)
driver.quit()