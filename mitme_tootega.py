"""
Tambet Osman, Mattias Randaru

Õpetus programmi jooksutamiseks.

1. Tuleb alla laadida paketid: selenium, beautifulsoup4
2. Tuleb alla laadida chromedriver, selle kohta on õpetus siin:
https://developer.chrome.com/docs/chromedriver/downloads?authuser=2
2.10 Tuleb luua oma kettale webdrivers kaust ja asetada chromedriver.exe fail sinna kausta
2.11 On võimalus muuta ära
"""



from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.keys import Keys
from collections import defaultdict
import re



# nimed jne tambet, TÖÖNIMI
# OPETUS KUIDAS KÄIMA PANNA

# kasutame nuppude ja info kättesaamiseks veebilehelt ostukorvid.ee seleniumit ja beautifulsoupi
# seleniumi puhul kasutame XPathi ja beautifulsoupi puhul kasutame HTMLi klasse

class ProductScraper: 
    def __init__(self, url):
        self.url = url
        service = Service()
        options = webdriver.FirefoxOptions()
        self.driver = webdriver.Firefox(service=service, options=options)
        # defineerime driveri seleniumi jaoks

    def scrape_product(self, search_term):
        self.driver.get(self.url) # selenium leiab veebilehe ostukorvid.ee

        # selenium vajutab nr 1 otsingulahtrile
        try:
            search_bar = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div/nav/div/div/div[3]/div/div/button"))
            )
            search_bar.click()
        except Exception as e:
            print(f"Error clicking search bar: {e}")
            self.driver.quit()
            return (search_term, "Error", 0, "")
        # jõuame uue leheni, kuhu sisestatakse toode

        time.sleep(2) # kasutame time.sleep, et selenium jõuaks oma protsessid teha
        try:
            search_input = self.driver.find_element(By.XPATH, "//input") #ideaalses olukorras mitte vajalik rida
            search_input.send_keys(search_term) # nr 2 otsingu lahter peaks ideaalis olema alati aktiivne kui
            search_input.send_keys(Keys.ENTER) # see kasutajale kuvatakse, aga error handlemise mõttes võib ta igaksjuhuks alles olla
            time.sleep(2)
            
        except Exception as e: # error handling kui me ei leia nr 2 otsingu lahtrit
            print(f"Error typing search term or clicking submit: {e}")
            self.driver.quit()
            return (search_term, "Error", 0, "")
        time.sleep(2)

        # vajutame nuppu "Tooted"
        try:
            tooted_button = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/reach-portal/div[3]/div/div/div/div[3]/ul/li[2]/button"))
            )
            tooted_button.click()
            time.sleep(2)
        except Exception as e:
            print(f"Error clicking 'Tooted' button: {e}")
            self.driver.quit()
            return (search_term, "Error", 0, "")
        time.sleep(2)

        #Lihtsuse mõttes vajutame kõige esimest toodet, sest ilmub suur sarnaste toodete list
        #nt kui otsida vesi, võib tulla 50 erinevat toodet mis vastab päringule "vesi"
        #see eeldab, et kasutaja peab kirjeldama oma otsingus toodet, mida ta otsib
        #"nutella" asemel on vaja kirjutada "nutella pähklikreem" ja nt "vesi" asemel "aura vesi gaseerimata"
        try:
            first_product = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/reach-portal/div[3]/div/div/div/div[4]/ul/li/a/img"))
            )
            first_product.click()
        except Exception as e:
            print(f"Error clicking first product: {e}")
            self.driver.quit()
            return (search_term, "Error", 0, "")

        # hakkame lugema lehelt, kus on spetsiifilise toote hinnad
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "ml-auto")) #kuna lehe struktuur on alati sama, saame leida õige elementi tema klassi kaudu
            )
            time.sleep(2)  # ooteaeg, et kõik lehe sisu saaks laetud
        except Exception as e:
            print(f"Error loading page: {e}")
            self.driver.quit()
            return (search_term, "Error", 0, "")

        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser") #kasutame beautiful soupi, et leida üles erinevad hinnad erinevates poodides

        prices = []

        # leiame kõikide poodide nimed, hinnad ja lingid lehe html koodist
        # see klass on taas leitud lihtsalt Inspect Elementi abil ostukorvid.ee leheküljelt
        store_links = soup.find_all("a", class_="mb-2 mt-2 flex w-full flex-row items-center rounded-sm border-2 border-gray-300 p-1 hover:border-gray-500 dark:border-gray-600 dark:hover:border-gray-500")

        print(f"Found {len(store_links)} store links for '{search_term}'")

        for link in store_links:
            try:
                store_url = link.get("href")
                store_title = link.get("title")

                print(f"Processing link: {store_title} - {store_url}")

                # leiame hinna teksti HTMList
                price_text = None
                # vaatame läbi teksti, mis võib sisaldada hinda (st seal on sees € märk)
                text_elements = link.find_all(text=True, recursive=True)

                for text in text_elements:
                    text = text.strip()
                    if '€' in text:
                        price_text = text
                        break

                if price_text:
                    try:
                        # puhastame hinna teksti ja teeme ta arvuks
                        price = float(price_text.replace("€", "").replace(",", ".").strip())
                        # proovime saada kätte tekstist ka poe nime
                        store_name = ""
                        if "Selver" in store_title:
                            store_name = "Selver"
                        elif "Rimi" in store_title:
                            store_name = "Rimi"
                        elif "Coop" in store_title:
                            store_name = "Coop"
                        elif "Prisma" in store_title:
                            store_name = "Prisma"
                        else:
                            # kui eelneva nelja poe nime tekstis ei olnud, siis saame selle
                            # kätte toote lingist, sest see link viib meid alati õigele poele
                            # ja teame et link on korrektne
                            match = re.search(r"(?<=www\.)[\w-]+", store_url)
                            if match:
                                store_name = match.group().capitalize()
                            else:
                                store_name = "Unknown Store"

                        prices.append({
                            "store": store_name,
                            "price": price,
                            "url": store_url
                        })
                        print(f"Successfully scraped {store_name}: €{price}")
                    except ValueError as ve:
                        print(f"Could not convert price text '{price_text}' to float: {ve}")
                else:
                    print(f"No price found for {store_title}")

            except Exception as e:
                print(f"Error processing store link: {e}")
                continue

        # järjestame hinnad kasvavas järjekorras
        prices.sort(key=lambda x: x["price"])

        # leiame kõige odavama poe spetsiifilise toote jaoks
        if prices:
            cheapest_store = next((store["store"] for store in prices if "Selver" in store["store"]), "Error")
            if cheapest_store == "Error":
                cheapest_store = next((store["store"] for store in prices), "No price information found")
            cheapest_price = next((store["price"] for store in prices if store["store"] == cheapest_store), 0)
            cheapest_url = next((store["url"] for store in prices if store["store"] == cheapest_store), "")
            return (search_term, cheapest_store, cheapest_price, cheapest_url)
        else:
            return (search_term, "No price information found", 0, "")

    def __del__(self):
        try:
            self.driver.quit()
        except:
            pass

def main():
    url = "https://ostukorvid.ee"
    scraper = ProductScraper(url)

    try:
        search_terms = []
        while True:
            search_term = input("Enter a product to search for (or press Enter to finish): ")
            if not search_term:
                break
            search_terms.append(search_term)

        for search_term in search_terms:
            product, cheapest_store, cheapest_price, cheapest_url = scraper.scrape_product(search_term)
            print(f"\nThe cheapest store for '{product}' is: {cheapest_store} (€{cheapest_price})")
            if cheapest_url:
                print(f"Store link: {cheapest_url}")
            else:
                print("No price information found.")

    except Exception as e:
        print(f"An error occurred during scraping: {e}")
    finally:
        del scraper

if __name__ == "__main__":
    main()
