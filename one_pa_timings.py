from selenium import webdriver


class OnePaTiming:
    def get_one_pa_timings(self, day):
        # setting up selenium
        driver = webdriver.Chrome(
            "C:/Users/winst/Documents/MEGA/Programs!/chromedriver_win32/chromedriver.exe"
        )

        # Connecting to the page
        driver.get("https://www.onepa.sg/facilities/4020CCMCPA-BM")

        # Click to open drop-down
        driver.find_element_by_xpath("//*[@id='content_0_tbDatePicker']").click()

        # Getting the elements in the date picker and clicking selected date
        elements = driver.find_elements_by_xpath(
            ".//*[@id='ui-datepicker-div']/table/tbody/tr/td/a"
        )
        for dates in elements:
            if (
                dates.is_enabled()
                and dates.is_displayed()
                and str(dates.get_attribute("innerText")) == str(day)
            ):
                dates.click()
                break

        # Finding available courst for the day
        print("reached new date")
        driver.implicitly_wait(5)
        courts = driver.find_elements_by_xpath(".//*[@id='facTable1']/div/span")
        print("courts found")
        court_checked = 0
        for court in courts:
            court_checked += 1
            print("checking court availability")
            if court.get_attribute("class") == "slots normal":
                print(
                    court.find_element_by_xpath(".//div/input").get_attribute("id")[-1]
                )
        # Todo: get the timing that the available courts correspond too
        # Todo: go through all the courts that the cc has to offer
        # Todo: store the results for the timings in each CC somewhere
        # Todo: return the result for the timings in each CC

        print(court_checked)