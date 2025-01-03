from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time

class WebScraperDatabase():

    def __init__(self, exec_path: str = 'chromedriver.exe') -> None:
        """
        WebScraper class, takes path for browser driver executable

        Arguments:
        date -- date which the scraper will scrape for
        exec_path -- path of the driver's executable

        Returns:
        None
        """

        self.service = Service(executable_path=exec_path)
        self.driver = webdriver.Chrome(service=self.service)
        self.phrases = []

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
        with open('teams.csv', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                self.phrases.append(row)

        self.phrases = [string for row in self.phrases for string in row]
        
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

    def read_phrase_results(self, ciphers: list[str] = ['chaldean']) -> None:
        """
        Reads the results of the phrases from gematrinator

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

        for i in range(1,(len(self.phrases) // 5)+1):
            
            for j in range((i-1)*5, i*5):
                input_element.clear()
                phrase = self.phrases[j]
                input_element.send_keys(phrase + Keys.ENTER)

            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "printHistoryTable"))
            )

            results = []
            tr_elements = self.driver.find_element(By.ID, 'printHistoryTable').find_elements(By.TAG_NAME, 'tr')[1:]
            for tr in tr_elements:
                td_elements = tr.find_elements(By.TAG_NAME, 'td')
                cipher_results = []
                for td in td_elements:
                    if td.get_attribute('class') == 'HistorySum':
                        cipher_result = td.find_element(By.ID, 'finalBreakNum').text
                        cipher_results.append(cipher_result)
                results.append(cipher_results)
            
            results.reverse()

            with open('team_nums.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerows([phrase] + result for phrase, result in zip(self.phrases[(i-1)*5: i*5], results))
            
    def run(self, ciphers: list[str] = ['chaldean']) -> None:
        """
        Runs the scraper class

        Arguments:
        None

        Returns:
        None
        """
        self.generate_phrases()
        self.read_phrase_results(ciphers)

        time.sleep(15)
        self.driver.quit()

if __name__=="__main__":
    a = WebScraperDatabase()
    a.run()