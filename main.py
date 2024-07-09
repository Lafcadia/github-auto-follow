import os
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
import threading

# Logo and information
logo = r"""
  ______ __  __ __     __     ___       __         ____     ____          
 / ___(_) /_/ // /_ __/ /    / _ |__ __/ /____    / __/__  / / /__ _    __
/ (_ / / __/ _  / // / _ \  / __ / // / __/ _ \  / _// _ \/ / / _ \ |/|/ /
\___/_/\__/_//_/\_,_/_.__/ /_/ |_\_,_/\__/\___/ /_/  \___/_/_/\___/__,__/
"""
print("--------------------------------------------------")
print(logo)
print("GitHub Auto Follow")
print("Made by 💜 from Zigao Wang.")
print("This project is licensed under MIT License.")
print("GitHub Repo: https://github.com/ZigaoWang/github-auto-follow/")
print("--------------------------------------------------")

# Disclaimer
print("DISCLAIMER: This script may violate GitHub's community guidelines.")
print("Use this script for educational purposes only.")
print("To stop the script at any time, type 'stop' in the terminal.")
print("--------------------------------------------------")

# Ensure the user reads and agrees to the disclaimer
agreement = input("Type 'agree' to continue: ").strip().lower()
if agreement != 'agree':
    print("You did not agree to the disclaimer. Exiting...")
    exit()

# Load environment variables from .env file
load_dotenv()

# Get GitHub credentials from environment variables
github_username = os.getenv("GITHUB_USERNAME")
github_password = os.getenv("GITHUB_PASSWORD")

# Prompt the user for the GitHub repository URL
default_repo_url = "https://github.com/torvalds/linux"
repo_url = input(f"Enter the GitHub repository URL (default {default_repo_url}): ").strip()
repo_url = repo_url if repo_url else default_repo_url


# Function to log in to GitHub
def github_login(username, password):
    driver.get("https://github.com/login")
    time.sleep(2)

    username_input = driver.find_element(By.ID, "login_field")
    password_input = driver.find_element(By.ID, "password")
    sign_in_button = driver.find_element(By.NAME, "commit")

    username_input.send_keys(username)
    password_input.send_keys(password)
    sign_in_button.click()
    time.sleep(2)


# Function to follow users on the stargazers page
def follow_stargazers(page, delay, follow_count):
    driver.get(f"{repo_url}/stargazers?page={page}")
    time.sleep(3)

    # Find all follow buttons on the page
    follow_buttons = driver.find_elements(By.XPATH, "//input[@type='submit' and @name='commit' and @value='Follow']")

    if not follow_buttons:
        return False, follow_count  # No follow buttons found, likely end of pages

    for button in follow_buttons:
        try:
            parent_element = button.find_element(By.XPATH, "./ancestor::div[contains(@class, 'd-flex')]")
            username_element = parent_element.find_element(By.XPATH, ".//a[contains(@data-hovercard-type, 'user')]")
            username = username_element.get_attribute("href").split("/")[-1]
            follow_count = click_follow_button(button, delay, username, follow_count)
        except Exception as e:
            print(f"Error clicking follow button: {e}")

    return True, follow_count


# Function to click a follow button with a delay and print user info
def click_follow_button(button, delay, username, follow_count):
    try:
        button.click()
        follow_count += 1
        print(f"{follow_count}. Followed {username}: https://github.com/{username}")
        time.sleep(delay)
    except Exception as e:
        print(f"Error clicking follow button for {username}: {e}")

    return follow_count


# Prompt the user for the starting page and speed mode
default_start_page = 1
default_speed_mode = "random"

start_page_input = input(f"Enter the starting page (default {default_start_page}): ").strip()
start_page = int(start_page_input) if start_page_input else default_start_page

speed_mode_input = input(
    f"Enter speed mode (fast, medium, slow, random) (default {default_speed_mode}): ").strip().lower()
speed_mode = speed_mode_input if speed_mode_input else default_speed_mode

# Set delay based on speed mode
if speed_mode == "fast":
    delay = 0.1
elif speed_mode == "medium":
    delay = 0.5
elif speed_mode == "slow":
    delay = 1
elif speed_mode == "random":
    delay = random.uniform(0.1, 2)
else:
    print("Invalid speed mode. Defaulting to random.")
    delay = random.uniform(0.1, 2)

print("Starting now")

# Create a new Chrome session
driver = webdriver.Chrome()

# Log in to GitHub
github_login(github_username, github_password)

# Variable to control the stop command
stop_thread = False

# Function to listen for the stop command
def listen_for_stop():
    global stop_thread
    while True:
        if input().strip().lower() == "stop":
            stop_thread = True
            break

# Start the stop command listener thread
stop_listener = threading.Thread(target=listen_for_stop)
stop_listener.start()

# Loop through pages and follow stargazers
page = start_page
users_followed = 0
follow_count = 0

try:
    while not stop_thread:
        followed_on_page, follow_count = follow_stargazers(page, delay, follow_count)
        if not followed_on_page:
            print(f"No follow buttons found on page {page}. Exiting.")
            break
        page += 1
except KeyboardInterrupt:
    print("Program interrupted by user.")

# Output the number of users followed
print(f"Total users followed: {follow_count}")

# Close the browser
driver.quit()