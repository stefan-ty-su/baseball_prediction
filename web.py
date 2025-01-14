from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from num2words import num2words
import time
import csv


class WebScraper():

    def __init__(self, date: datetime.date, exec_path: str = 'chromedriver.exe') -> None:
        """
        WebScraper class, takes path for browser driver executable

        Arguments:
        date -- date which the scraper will scrape for
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
        self.date = date
        self.phrases = []
        self.phrase_results = []
        self.phrase_dict = dict()

        self.date_stats = dict()

    def generate_phrases(self) -> None:
        """
        Generates the list of phrases to be input into gematrinator.
        List of phrases is assigned to class variable 'phrases'

        Arguments:
        date -- date which phrases will be based off

        Returns:
        None
        """
        # Obtaining all 'words'
        day_of_month = self.date.strftime('%d') # e.g. 25
        day_of_month_ordinal = self._ordinal_suffix(day_of_month) # e.g. 25th
        day_of_month_words = num2words(int(day_of_month), to='ordinal') # twenty-five

        day_of_week = self.date.strftime('%A') # e.g. Monday
        month = self.date.strftime('%B') # e.g. January
        year = self.date.strftime('%Y') # e.g. 2005

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
        self.phrases.extend(['pi', 'kill', 'sweep', 'comeback'])

    def enter_phrases(self, ciphers: list[str] = ['chaldean']) -> None:
        """
        Inputs phrases into provided input element

        Arguments:
        None

        Returns:
        None
        """
        self.driver.get("https://gematrinator.com/calculator")
        self.add_ciphers(ciphers)

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

    def read_phrase_results(self, team1_name: str, team2_name: str) -> None:
        """
        Reads the results of the phrases from gematrinator

        Arguments:
        None

        Returns:
        None
        """

        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "printHistoryTable"))
        )

        tr_elements = self.driver.find_element(By.ID, 'printHistoryTable').find_elements(By.TAG_NAME, 'tr')[1:]
        for tr in tr_elements:
            td_elements = tr.find_elements(By.TAG_NAME, 'td')
            cipher_results = []
            for td in td_elements:
                if td.get_attribute('class') == 'HistorySum':
                    cipher_result = td.find_element(By.ID, 'finalBreakNum').text
                    cipher_results.append(cipher_result)
            self.phrase_results.append(cipher_results)
        
        self.phrase_results.reverse()

        phrases = []
        results = []
        counter = 5
        with open('team_nums.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:

                if row[0] == team1_name or row[0] == team2_name:
                    phrases.append(row[0])
                    results.append(row[1:])
                    counter = 1
                elif counter < 5:
                    phrases.append(row[0])
                    results.append(row[1:])
                    counter += 1
        
        self.phrase_results.extend(results)
        self.phrases.extend(phrases)
        self.phrase_dict = {phrase: result for phrase, result in zip(self.phrases, self.phrase_results)}
        # print(self.phrase_dict)

    def get_date_stats(self) -> None:
        """
        Obtains date statistics

        """
        self.driver.get("https://gematrinator.com/date-calculator")

        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "Month1"))
        )
        
        # Inputting Date 1 (Start of date year)
        input_element = self.driver.find_element(By.ID, "Month1")
        input_element.clear()
        input_element.send_keys('1')

        input_element = self.driver.find_element(By.ID, "Day1")
        input_element.clear()
        input_element.send_keys('1')

        input_element = self.driver.find_element(By.ID, "Year1")
        input_element.clear()
        input_element.send_keys(datetime.strftime(self.date, '%Y'))


        # Inputting Date 2 (self.date)
        print(datetime.strftime(self.date, '%d'))
        input_element = self.driver.find_element(By.ID, "Month2")
        input_element.clear()
        input_element.send_keys(str(int(datetime.strftime(self.date, '%m'))))

        input_element = self.driver.find_element(By.ID, "Day2")
        input_element.clear()
        input_element.send_keys(str(int(datetime.strftime(self.date, '%d'))))

        input_element = self.driver.find_element(By.ID, "Year2")
        input_element.clear()
        input_element.send_keys(datetime.strftime(self.date, '%Y'))
        
        # Retrieving stats from table
        table_element = self.driver.find_elements(By.CLASS_NAME, 'ClassicDateTable')[1]
        tr_elements = table_element.find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME, 'tr')
        for tr in tr_elements:
            key = tr.find_element(By.CLASS_NAME, 'NumString').text
            value = tr.find_element(By.CLASS_NAME, 'SumString').text
            self.date_stats[key] = [value, 'NA']

        duration_elements = self.driver.find_elements(By.CLASS_NAME, 'DurNum')
        self.date_stats['Months Days'] = [duration_elements[8].text, duration_elements[9].text]
        self.date_stats['Weeks Days'] = [duration_elements[10].text, duration_elements[11].text]
        self.date_stats['Days'] = [duration_elements[12].text, 'NA']

    def run(self, team1_name: str, team2_name: str, ciphers: list[str] = ['chaldean']) -> None:
        """
        Runs the scraper class

        Arguments:
        None

        Returns:
        None
        """
        self.generate_phrases()
        self.enter_phrases(ciphers)
        self.read_phrase_results(team1_name, team2_name)

        self.get_date_stats()

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

class NumberCounter():

    def __init__(self, date: datetime.date, phrase_results: list[list[str]], date_stats: dict) -> None:
        """
        Number Counter class, performs number counting and ranking.
        Also does any additional number modifications (e.g. removing 0s)

        Arguments:
        date -- the date being analysed
        phrase_results -- a 2d array of numbers in string format
        date_stats -- statistics of the date

        Returns:
        None
        """
        self.date = date
        self.results = [number for result in phrase_results for number in result]
        self.date_stats = [num for stat in date_stats.values() for num in stat]
        self.date_stats = [num for num in self.date_stats if num != '0']

        self.add_additional_numbers()

        self.counter = dict()
        self.count_nums()

    def add_additional_numbers(self) -> None:
        """
        Adds all other additional numbers

        Arguments:
        None

        Returns:
        None
        """
        self.all_nums = self.results + self.date_stats
        for num in self.results + self.date_stats:
            new_num = num.replace('0', '')
            if new_num != num:
                self.all_nums.append(new_num)
        self.all_nums = [num for num in self.all_nums if num != 'NA']
    
    def count_nums(self) -> None:
        """
        Counts the number of occurrences of numbers, records into self.counter

        Arguments:
        None

        Returns:
        None
        """
        for num in self.all_nums:
            if num in self.counter:
                self.counter[num] = self.counter[num] + 1
            else:
                self.counter[num] = 1

    def display_nums(self, ranked: bool=True, significance: int = 2) -> list[tuple]:
        """
        Displays nums as tuples

        Arguments:
        ranked -- displays numbers in descending order if True

        Returns:
        None
        """
        nums_tuple = list(zip(self.counter.keys(), self.counter.values()))
        if ranked:
            nums_tuple.sort(key=lambda x: x[1], reverse=True)
        return [tup for tup in nums_tuple if tup[1] >= significance]


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
    # date = datetime.strptime('03/01/2025', '%d/%m/%Y')
    # ws = WebScraper(date)
    # ws.run()
    # nc = NumberCounter(date, ws.phrase_results, ws.date_stats)
    # print(nc.display_nums())
    pass