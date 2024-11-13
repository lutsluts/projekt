from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.keys import Keys

class ProductScraper:
    def __init__(self, url):
        self.url = url
        service = Service()
        options = webdriver.FirefoxOptions()
        self.driver = webdriver.Firefox(service=service, options=options)

    def scrape(self, search_term):
        self.driver.get(self.url)

        # Click the search bar
        try:
            search_bar = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div/nav/div/div/div[3]/div/div/button"))
            )
            search_bar.click()
        except Exception as e:
            print(f"Error clicking search bar: {e}")
            self.driver.quit()
            return []

        # Type the search term and submit the form
        time.sleep(2)
        try:
            search_input = self.driver.find_element(By.XPATH, "//input")
            search_input.send_keys(search_term) #sisestame otsitud toote searchbari
            search_input.send_keys(Keys.ENTER) # vajutame enterit
            time.sleep(2)

        except Exception as e:
            print(f"Error typing search term or clicking submit: {e}")
            self.driver.quit()
            return []
        time.sleep(5)
        # Click the "Tooted" button
        try:
            tooted_button = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/reach-portal/div[3]/div/div/div/div[3]/ul/li[2]/button"))
            )
            tooted_button.click()
            time.sleep(5)
        except Exception as e:
            print(f"Error clicking 'Tooted' button: {e}")
            self.driver.quit()
            return []
        time.sleep(5)
        # Click the first product in the list
        try:
            first_product = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/reach-portal/div[3]/div/div/div/div[4]/ul/li/a/img"))
            )
            first_product.click()
        except Exception as e:
            print(f"Error clicking first product: {e}")
            self.driver.quit()
            return []

        # Wait for the main content to load
        try:
            # Wait for the specific div with class ml-auto mr-auto
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "ml-auto"))
            )
            time.sleep(2)  # Small delay to ensure dynamic content loads
        except Exception as e:
            print(f"Error loading page: {e}")
            self.driver.quit()
            return []

        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        prices = []

        # Find all store links based on the exact classes from your HTML
        store_links = soup.find_all("a", class_="mb-2 mt-2 flex w-full flex-row items-center rounded-sm border-2 border-gray-300 p-1 hover:border-gray-500 dark:border-gray-600 dark:hover:border-gray-500")

        print(f"Found {len(store_links)} store links")  # Debug print

        for link in store_links:
            try:
                store_url = link.get("href")
                store_title = link.get("title")

                # Debug print
                print(f"Processing link: {store_title} - {store_url}")

                # First, try to find direct price text
                price_text = None
                # Look for any text that might contain the price
                text_elements = link.find_all(text=True, recursive=True)

                for text in text_elements:
                    text = text.strip()
                    if '€' in text:
                        price_text = text
                        break

                if price_text:
                    try:
                        # Clean up the price text and convert to float
                        price = float(price_text.replace("€", "").replace(",", ".").strip())
                        store_name = store_title.split()[0] if store_title else "Unknown Store"

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

        # Close the driver after scraping
        self.driver.quit()

        # Sort prices by price value
        prices.sort(key=lambda x: x["price"])

        return prices

    def __del__(self):
        try:
            self.driver.quit()
        except:
            pass

def main():
    url = "https://ostukorvid.ee"
    scraper = ProductScraper(url)

    try:
        product_prices = scraper.scrape("monster monarch")
        print("\nAll prices sorted from lowest to highest:")
        if not product_prices:
            print("No prices were found. DEBUG INFO:")
            print("Please check if the website's structure has changed.")
        for item in product_prices:
            print(f"{item['store']}: €{item['price']} ({item['url']})")
    except Exception as e:
        print(f"An error occurred during scraping: {e}")
    finally:
        del scraper

if __name__ == "__main__":
    main()
