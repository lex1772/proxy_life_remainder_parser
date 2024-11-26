import os
import time
from typing import Tuple, List

import chromedriver_autoinstaller
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ProxyParser:
    load_dotenv()
    chromedriver_autoinstaller.install()

    def __init__(self, username: str, password: str) -> None:
        self.username: str = username
        self.password: str = password
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)

    def open_site(self):
        """Метод для открытия страницы"""
        self.driver.get(os.getenv("URL"))
        time.sleep(2)

    def login(self):
        """Метод для входа в ЛК через email и password. Капча вводится самостоятельно в течении 60 секунд"""
        login_button = self.driver.find_element(By.LINK_TEXT, "Войти")
        login_button.click()
        time.sleep(2)

        self.driver.find_element(By.NAME, "email").send_keys(os.getenv("LOGIN"))
        self.driver.find_element(By.NAME, "password").send_keys(os.getenv("PASSWORD"))

        self.wait.until(
            EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[@title='reCAPTCHA']"))
        )
        self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@id='recaptcha-anchor']"))
        ).click()

        self.driver.switch_to.default_content()
        time.sleep(60)

        login_button = WebDriverWait(self.driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Войти']"))
        )
        login_button.click()
        time.sleep(2)

    def get_proxy_data(self) -> Tuple[List[str], List[str]]:
        """Метод для получения прокси и даты окончания"""
        proxy_list: List[str] = []
        date_list: List[str] = []

        left_elements = self.wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "left"))
        )

        for left_element in left_elements:
            left_text = left_element.text

            if left_text == "Дата" or (left_text.startswith("Прокси") and "IP:PORT" in left_text):
                if left_text == "Дата":
                    right_element = left_element.find_element(By.XPATH,
                                                              "following-sibling::div[contains(@class, 'right')]")
                    date_list.append(right_element.text)
                    continue

                right_element = left_element.find_element(By.XPATH, "following-sibling::div[contains(@class, 'right')]")
                right_text = right_element.text
                proxy_list.append(right_text)

        return proxy_list, date_list

    def print_proxy_data(self) -> None:
        """Метод для вывода прокси с соответствующей датой окончания"""
        proxy_list, date_list = self.get_proxy_data()

        for proxy, date in zip(proxy_list, date_list):
            print(f"{proxy} - {date}")

    def close(self) -> None:
        self.driver.quit()


if __name__ == "__main__":
    username: str = os.getenv("LOGIN")
    password: str = os.getenv("PASSWORD")

    parser = ProxyParser(username, password)
    parser.open_site()
    parser.login()

    print("Полученные прокси:")
    parser.print_proxy_data()

    parser.close()
