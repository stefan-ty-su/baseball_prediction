from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from num2words import num2words
import time


class WebScraper():

    def __init__(self, exec_path: str = 'chromedriver.exe') -> None:
        """
        WebScraper class, takes path for browser driver executable

        Arguments:
        exec_path -- path of the driver's executable

        Returns:
        None
        """

        self.zodiac_to_planet = {
            'aries': ['mars'],
            'taurus': ['venus'],
            'gemini': ['mercury'],
            'cancer': ['moon'],
            'leo': ['sun'],
            'virgo': ['mercury'],
            'libra': ['venus'],
            'scorpio': ['mars'],
            'sagittarius': ['jupiter'],
            'capricorn': ['saturn'],
            'aquarius': ['saturn', 'uranus'],
            'pisces': ['neptune']
        }

        self.service = Service(executable_path=exec_path)
        self.driver = webdriver.Chrome(service=self.service)
        self.phrases = []

    def generate_phrases(self, date: datetime.date) -> None:
        """
        Generates the list of phrases to be input into gematrinator.
        List of phrases is assigned to class variable 'phrases'

        Arguments:
        date -- date which phrases will be based off

        Returns:
        None
        """
        # Obtaining all 'words'
        day_of_month = date.strftime('%d') # e.g. 25
        day_of_month_ordinal = self._ordinal_suffix(day_of_month) # e.g. 25th
        day_of_month_words = num2words(int(day_of_month), to='ordinal') # twenty-five

        day_of_week = date.strftime('%A') # e.g. Monday
        month = date.strftime('%B') # e.g. January
        year = date.strftime('%Y') # e.g. 2005

        moon_sign = self.obtain_moon_sign(day_of_month, month, year) # e.g. Gemini
        planets = self.zodiac_to_planet[moon_sign]

        # Generating phrases
        self.phrases.append(f'{day_of_month} {month} {year}')
        self.phrases.append(f'{day_of_month} {month}')
        self.phrases.append(f'{day_of_month_words} {month}')
        self.phrases.append(f'{day_of_month_ordinal} {month} {year}')
        self.phrases.append(f'{day_of_month_ordinal} {month}')
        for planet in planets:
            self.phrases.append(f'{planet}')
        self.phrases.append(f'{moon_sign}')
        self.phrases.append(f'moon in {moon_sign}')
        self.phrases.append(f'{day_of_week}')

    def enter_phrases(self) -> None:
        """
        Inputs phrases into provided input element

        Arguments:
        None

        Returns:
        None
        """
        self.driver.get("https://gematrinator.com/calculator")
        self.add_ciphers(['chaldean'])

        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "EntryField"))
        )

        input_element = self.driver.find_element(By.ID, "EntryField")
        
        for phrase in self.phrases:
            input_element.clear()
            input_element.send_keys(phrase + Keys.ENTER)

    def add_ciphers(self, ciphers: list[str]) -> None:
        """
        Inputs phrases into provided input element

        Arguments:
        ciphers -- list of ciphers to be added

        Returns:
        None
        """
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "calcMenuItem"))
        )

        # Opening Cipher options
        elements = self.driver.find_elements(By.CLASS_NAME, "calcMenuItem")
        for element in elements:
            print(element.text.lower())
            if element.text.lower() == 'ciphers ':
                element.click()

                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, 'CancelCiphers'))
                )
                self.driver.find_element(By.ID, 'CancelCiphers').click()

                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "calcMenuItem"))
                )
                element.click()

        # Applying all ciphers
        
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'cipherBox'))
        )

        li_elements = self.driver.find_element(By.ID, 'cipherBox').find_elements(By.TAG_NAME, 'li')
        for li in li_elements:
            text = li.find_element(By.TAG_NAME, 'font').text
            if text.lower() in ciphers:
                li.find_element(By.TAG_NAME, 'input').click()
        
        #Update Click
        self.driver.find_element(By.ID, 'SaveCiphers').click()        

    def obtain_moon_sign(self, day_of_month:str, month:str, year: str) -> str:
        """
        Obtains moon sign, and returns as string

        Arguments:
        day_of_month -- day of month (e.g. 25)
        month -- month (e.g. January)
        year -- year (e.g. 2005)

        Returns:
        str -- string of moon sign
        """

        self.driver.get(f'https://mooncalendar.astro-seek.com/moon-phase-day-{day_of_month}-{month.lower()}-{year}')

        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "astro_symbol"))
        )

        elements = self.driver.find_elements(By.CLASS_NAME, 'astro_symbol')
        for element in elements:
            moon_sign = element.get_attribute('alt').lower()
            if moon_sign in self.zodiac_to_planet.keys():
                return moon_sign
        return ''

    def run(self) -> None:
        """
        Runs the scraper class

        Arguments:
        None

        Returns:
        None
        """
        self.generate_phrases(datetime.strptime('02/01/2025', '%d/%m/%Y'))
        self.enter_phrases()

        time.sleep(25)
        self.driver.quit()

    def _ordinal_suffix(self, numberStr: str) -> str:
        """
        Adds suffix to a number, returns string (e.g 2 -> 2nd)
        
        Argments:
        numberStr -- an integer in string format

        Returns:
        str -- a string with the integer and its appropriate suffix
        """

        if numberStr[-2:] in ('11', '12', '13'):
            return numberStr + 'th'
        elif numberStr[-1] == '1':
            return numberStr + 'st'
        elif numberStr[-1] == '2':
            return numberStr + 'nd'
        elif numberStr[-1] == '3':
            return numberStr + 'rd'
        else:
            return numberStr + 'th'

if __name__=="__main__":
    # service = Service(executable_path='chromedriver.exe')
    # driver = webdriver.Chrome(service=service)

    # driver.get("https://gematrinator.com/calculator")

    # WebDriverWait(driver, 10).until(
    #     EC.element_to_be_clickable((By.ID, "EntryField"))
    # )

    # input_element = driver.find_element(By.ID, "EntryField")
    # input_element.clear()
    # input_element.send_keys("Test" + Keys.ENTER)

    # time.sleep(3)

    # driver.quit()

    ws = WebScraper()
    ws.run()