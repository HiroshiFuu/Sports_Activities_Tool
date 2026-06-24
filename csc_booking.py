import os
import sys
import time
from datetime import datetime

import ntplib
import pytz
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait


class CSC:
    def __init__(self):
        with open("top_secret.txt", encoding="utf-8-sig") as f:
            self.username = f.readline().strip()
            self.password = f.readline().strip()
        chrome_options = Options()
        chrome_options.add_argument("--incognito")
        chrome_options.add_experimental_option("detach", True)
        base = getattr(sys, "_MEIPASS", os.path.dirname(__file__))
        driver_path = os.path.join(base, "chromedriver.exe")
        self.browser = webdriver.Chrome(service=Service(driver_path), options=chrome_options)
        self.browser.get("https://gateway.csc.sg/webclub/facilities/")

    def _login(self, user, password):
        member_id_field = self.browser.find_element(By.NAME, "login")
        member_id_field.send_keys(user)
        password_field = self.browser.find_element(By.NAME, "password")
        password_field.send_keys(password)
        self.browser.find_element(By.NAME, "Login").click()
        self.browser.implicitly_wait(2)
        els = self.browser.find_elements(By.PARTIAL_LINK_TEXT, "Disconnect")
        if len(els) == 1:
            els[0].click()

    def _navigate_to_badminton_booking(self, target_date: str, timed: None):
        el = WebDriverWait(self.browser, timeout=3).until(lambda d: d.find_element(By.PARTIAL_LINK_TEXT, "Facilities"))
        el.click()

        if timed:
            timed_parts = timed.split(":")
            hour = int(timed_parts[0])
            minute = int(timed_parts[1])
            second = int(timed_parts[2])
            time_out = False
            print(f"Targeted time: {timed}")
            c = ntplib.NTPClient()
            while not time_out:
                try:
                    response = c.request("sg.pool.ntp.org", version=3, timeout=3)
                    ct = datetime.fromtimestamp(response.tx_time, pytz.timezone("Asia/Singapore"))
                except Exception:
                    ct = datetime.now(pytz.timezone("Asia/Singapore"))
                print(f"Now: {ct.hour}, {ct.minute}, {ct.second}")
                if ct.hour == hour and ct.minute == minute and ct.second == second:
                    time_out = True
                else:
                    time.sleep(1)

        found = False
        while not found:
            clubhouse = Select(WebDriverWait(self.browser, timeout=3, poll_frequency=0.1).until(lambda d: d.find_element(By.NAME, "locationCode")))
            clubhouse.select_by_visible_text("Tessensohn Clubhouse")
            time.sleep(0.1)
            # select facility
            try:
                facility = Select(WebDriverWait(self.browser, timeout=3, poll_frequency=0.1).until(lambda d: d.find_element(By.NAME, "facilityCode")))
                facility.select_by_value("FCLS1FBA")
            except Exception:
                time.sleep(0.5)
                facility = Select(WebDriverWait(self.browser, timeout=3, poll_frequency=0.1).until(lambda d: d.find_element(By.NAME, "facilityCode")))
                facility.select_by_value("FCLS1FBA")
            time.sleep(0.1)
            # select date
            try:
                date = Select(WebDriverWait(self.browser, timeout=3, poll_frequency=0.1).until(lambda d: d.find_element(By.NAME, "bookingDate")))
            except Exception:
                time.sleep(0.5)
                date = Select(WebDriverWait(self.browser, timeout=3, poll_frequency=0.1).until(lambda d: d.find_element(By.NAME, "bookingDate")))
            option_list = date.options
            for option in option_list:
                print("dates: " + option.text)
                text = option.text
                if target_date in text:
                    found = True
                    option.click()
                    self.browser.implicitly_wait(1)
                    self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
                    el = WebDriverWait(self.browser, timeout=3).until(lambda d: d.find_element(By.PARTIAL_LINK_TEXT, "Next Step"))
                    el.click()
                    print("Found targeted date")
                    break
            if not found:
                self.browser.implicitly_wait(0.5)
                self.browser.refresh()

    def _book_timing_for_courts(self, prefer_timing_1, prefer_timing_2):
        print("Start finding courts")
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Next Step")))
        prefer_timing_1 -= 6
        prefer_timing_2 -= 6
        t1_done = False
        t2_done = False
        # self.browser.execute_script("document.body.style.zoom='0.5'")
        for i in [3, 2, 1, 4]:
            if not t1_done:
                name = f"facno00{prefer_timing_1:02d}0{i}"
                els = self.browser.find_elements(By.NAME, name)
                if len(els) == 1:
                    # ActionChains(self.browser).move_to_element(els[0]).click().perform()
                    self.browser.execute_script("arguments[0].click();", els[0])
                    t1_done = True
                    print(f"booking court t1 {name}")
            if not t2_done:
                name = f"facno00{prefer_timing_2:02d}0{i}"
                els = self.browser.find_elements(By.NAME, name)
                if len(els) == 1:
                    # ActionChains(self.browser).move_to_element(els[0]).click().perform()
                    self.browser.execute_script("arguments[0].click();", els[0])
                    t2_done = True
                    print(f"booking court t2 {name}")
        if t1_done or t2_done:
            self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            el = self.browser.find_element(By.XPATH, "//a[@onclick='btnClick(1);']")
            el.click()

    def court_booking(self, target_date, prefer_timing_1, prefer_timing_2, timed=None):
        self._login(self.username, self.password)
        target_date_str = datetime.strptime(target_date, "%y%m%d").strftime("%d %b %Y")
        self._navigate_to_badminton_booking(target_date_str, timed)
        self._book_timing_for_courts(int(prefer_timing_1), int(prefer_timing_2))
