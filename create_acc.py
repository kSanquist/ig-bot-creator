# Selenium 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.chrome.service import Service 
from webdriver_manager.chrome import ChromeDriverManager 
from selenium.webdriver.support.wait import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import TimeoutException
# Other
import os, random, string, pickle, time
from fake_useragent import UserAgent
import smtplib


# Suppose to create a fake user agent (No clue if this is doing anything)
def load_ua():
    ua = UserAgent()
    user_agent = ua.random
    print(user_agent)


# Everything you need to start Selenium's webdriver!
def start_webdriver(url: str) -> webdriver:
    options = Options()
    options.add_experimental_option('detach', True)
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    return driver


# Cleans up the process of grabbing elements using Selenium
def get_elem(driver: webdriver, by: By, input: str):
    element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((by, input)))
    return element


# Uses incognitiomail.co to generate a temporary email for the bot
def get_email(driver: webdriver) -> str:
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
    driver.get("https://incognitomail.co/")
    time.sleep(5)
    email = get_elem(driver, By.XPATH, "//*[@id='root']/div/div[2]/div/div/div[1]/div/span").text
    return email


# Creates a password for the bot account (just 12 random letters and numbers)
def create_password() -> str:
    password_characters = string.ascii_letters + string.digits
    return ''.join(random.choice(password_characters) for _ in range(12))


# Randomly grabs two names from names.txt for the full name of the bot
# Creates a username which, in essence, is just : firstname_lastname[random # 1000 - 9999]
def create_name() -> tuple:
    name_list = []
    with open('names.txt', 'r') as f:
        names = [name[:-1] for name in f]
        name_list = random.choices(names, k=2)

    name = name_list[0] + ' ' + name_list[1]
    username = name_list[0] + '_' + name_list[1] + str(random.randint(1000, 9999))

    return (name, username)


# The meat and potatoes, inputs all the sign-up information for the bot
# Also handles the confirmation code
def input_credentials(driver: webdriver, email: str, name: str, username: str, password: str):
    driver.switch_to.window(driver.window_handles[0])
    
    get_elem(driver, By.NAME, "emailOrPhone").send_keys(email)  # email
    get_elem(driver, By.NAME, "fullName").send_keys(name)       # name
    username_in = get_elem(driver, By.NAME, "username").send_keys(username)   # username
    get_elem(driver, By.NAME, "password").send_keys(password)   # password
    while True:  # Checks to make sure username is allowed
        try :
            get_elem(driver, By.XPATH, "//*[@id='mount_0_0_OW']/div/div/div[2]/div/div/div/div[1]/section/main/div/div/div[1]/div[2]/form/div[6]/div/div/span")
            username_in.clear()
            new_username = username[:-4] + str(random.randint(1000, 9999))
            username_in.send_keys(new_username)
        except TimeoutException:
            break

    get_elem(driver, By.CSS_SELECTOR, "button[type='submit']").click()

    add_birthday(driver)  # Handles birthday input
    print("DONE")

    # Handles confirmation code
    print("Dealing With Confirmation Code...")
    conf_code = get_conf_code(driver)
    driver.switch_to.window(driver.window_handles[0])
    get_elem(driver, By.NAME, "email_confirmation_code").send_keys(conf_code)
    get_elem(driver, By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/section/main/div/div/div[1]/div[2]/form/div/div[2]/div").click()
    print("DONE")


# Gets a random number for the birth month, day, and year for the bot. Happy birthday!
def add_birthday(driver: webdriver):
    titles = {'Month:' : (1, 12), 'Day:' : (1, 28), 'Year:' : (1940, 2004)}
    
    for title, range in titles.items():
        select_elem = get_elem(driver, By.CSS_SELECTOR, f"select[title='{title}']")
        select = Select(select_elem)
        select.select_by_value(str(random.randint(range[0], range[1])))
    
    get_elem(driver, By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/section/main/div/div/div[1]/div/div[6]/button").click()


# Loops through the bot's shiny, new temporary email until the email with the code appears
def get_conf_code(driver: webdriver) -> str:
    driver.switch_to.window(driver.window_handles[1])

    while True:
        try :
            email_subject = get_elem(driver, By.CLASS_NAME, "dataSubject").text
            code = email_subject.split(' ')[0]
            return code
        except TimeoutException:
            continue


# Unpickles a given txt file
def load_accounts(txt_file: str):
    accounts = {}
    if os.stat(txt_file).st_size != 0:
        with open(txt_file, 'rb') as f:
            accounts = pickle.load(f)
    return accounts


# Pickles accounts dict to the picklex_txt file and saves a readable account String to plain_txt file
def save_accounts(accounts_: dict, pickled_txt: str, plain_txt: str):
    with open(pickled_txt, 'wb') as f:
        pickle.dump(accounts_, f)

    with open(plain_txt, "w") as f:
        for email, passwd in accounts_.items():
            f.write(f"   email : {email} \npassword : {passwd}\n\n")
    

def email_accounts_file():
    pass


# Main, seen it a million times. BORING!
def main():
    load_ua()
    driver = start_webdriver("https://www.instagram.com/accounts/emailsignup/")

    accounts = load_accounts("pickled_accounts.txt")

    print("Generating Credentials...")
    email = get_email(driver)
    name, username = create_name()
    password = create_password()
    print("DONE")

    print("Inputting Credentials...")
    input_credentials(driver, email, name, username, password)

    print("\nAccount Created Successfully!")
    print(f"   email : {email} \npassword : {password}")

    accounts[email] = password
    save_accounts(accounts_=accounts, pickled_txt="pickled_accounts.txt", plain_txt="plain_accounts.txt")

    
if __name__ == '__main__':
    main()