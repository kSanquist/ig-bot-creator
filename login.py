import create_acc
import pickle, os, random, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys 


def get_created_acc() -> dict:
    if os.stat('accounts.txt').st_size == 0:
        create_acc.main()
    else:
        with open('accounts.txt', 'rb') as f:
            return pickle.load(f)


def login(driver: webdriver, email: str, password: str):
    create_acc.get_elem(driver, By.NAME, "username").send_keys(email)  # Input email
    create_acc.get_elem(driver, By.NAME, "password").send_keys(password)  # Input password
    time.sleep(5)
    create_acc.get_elem(driver, By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/section/main/article/div[2]/div[1]/div[2]/form/div/div[3]/button").click()  # Click "Log In"
    try:  # Bypass "Remember Me" popup
        create_acc.get_elem(driver, By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/section/main/div/div/div/div/div").click()
    except TimeoutException:
        pass
    try:  # Bypass notifications popup
        create_acc.get_elem(driver, By.XPATH, "/html/body/div[3]/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/button[2]").click()
    except TimeoutException:
        pass


def open_user_acc(driver: webdriver, user: str, extra=''):
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(f"https://instagram.com/{user}/{extra}")


def grab_user_following(driver: webdriver, user: str) -> list:
    pass


def main():
    driver = create_acc.start_webdriver("https://instagram.com/")
    accounts = get_created_acc()
    rand_email = random.choice(list(accounts.keys()))
    login(driver=driver, email=rand_email, password=accounts[rand_email])
    
    user = input("Enter First User : ")
    open_user_acc(driver=driver, user=user, extra='following')
    following_users = grab_user_following(driver=driver, user=user)


if __name__ == "__main__":
    main()