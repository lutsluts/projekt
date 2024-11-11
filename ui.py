import tkinter as tk
from tkinter import messagebox
from bs4 import BeautifulSoup
import requests
#tere jälle
#tervist jah
class ToidupoodRakendus:
    def __init__(self, root):
        self.root = root
        self.root.title("Nutike Ostunimekiri")
        self.root.geometry("400x500")

        # List to store shopping items
        self.ostunimekiri = []

        # UI setup
        self.setup_ui()

    def setup_ui(self):
        # Header
        header = tk.Label(self.root, text="🛒 Nutike Ostunimekiri", font=("Arial", 16, "bold"))
        header.pack(pady=10)

        # Product entry
        tk.Label(self.root, text="Sisesta toode:").pack()
        self.toode_entry = tk.Entry(self.root, font=("Arial", 12))
        self.toode_entry.pack(pady=5)

        # Add button
        add_button = tk.Button(self.root, text="Lisa toode", command=self.lisa_toode)
        add_button.pack(pady=5)

        # Shopping list display
        self.nimekiri_label = tk.Label(self.root, text="Sinu ostunimekiri:", font=("Arial", 12))
        self.nimekiri_label.pack()
        self.nimekiri_text = tk.Text(self.root, width=40, height=10, font=("Arial", 10))
        self.nimekiri_text.pack(pady=5)
        self.update_nimekiri()

        # Find best prices button
        find_prices_button = tk.Button(self.root, text="🔍 Leia parimad hinnad", bg="lightgreen", command=self.leia_parimad_hinnad)
        find_prices_button.pack(pady=10)

        # Clear list button
        clear_button = tk.Button(self.root, text="Kustuta nimekiri", bg="salmon", command=self.kustuta_nimekiri)
        clear_button.pack(pady=5)

    def update_nimekiri(self):
        """Uuendab, ostunimekirja listi ühe toote võrra"""
        self.nimekiri_text.delete(1.0, tk.END)
        for idx, toode in enumerate(self.ostunimekiri, start=1):
            self.nimekiri_text.insert(tk.END, f"{idx}. {toode}\n")

    def lisa_toode(self):
        """Add a product to the shopping list."""
        toode = self.toode_entry.get().strip()
        if toode:
            self.ostunimekiri.append(toode)
            self.update_nimekiri()
            self.toode_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Sisestusviga", "Palun sisesta toote nimi.")

    def kustuta_nimekiri(self):
        """Clear the shopping list."""
        self.ostunimekiri = []
        self.update_nimekiri()

    def leia_parimad_hinnad(self):
    
        try:
        # Iterate over items in the shopping list and fetch prices for each
            for toode in self.ostunimekiri:
                prices = self.fetch_prices(toode)  # Use self.fetch_prices() instead of fetch_prices()
            
            # Process the prices (remaining code here remains the same)
                if prices:
                    best_store, best_price = min(prices.items(), key=lambda x: x[1])
                    messagebox.showinfo("Tulemused", f"Sinu ostukorvi parim hind on poes {best_store} - {best_price:.2f}€")
                else:
                    messagebox.showwarning("Tulemused", f"Tootele '{toode}' ei leitud hindu.")
        except Exception as e:
            messagebox.showerror("Tulemused", f"Tekkis viga hinnainfo toomisel: {str(e)}")

    def extract_price(html):

        soup = BeautifulSoup(html, 'html.parser')
    
    # Replace 'price-class' with the actual class or structure of the price element from the website
        price_element = soup.find(class_="price-class")  # Update "price-class" with the actual class
    
        if price_element:
            price_text = price_element.get_text(strip=True)
            try:
            # Clean up the text to extract the numerical value
                price_text = price_text.replace("€", "").replace(",", ".").strip()
                return float(price_text)
            except ValueError:
                print("Error parsing price text:", price_text)
                return float('inf')  # Return a very high number if parsing fails
        else:
            print("Price element not found")
            return float('inf')

    def search_similar_products(self, toode):
        """Search for similar products on the website and return a list of matches."""
        try:
            search_url = f"{self.base_url}/kategooriad?q={toode}"
            response = requests.get(search_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            product_elements = soup.find_all("a", class_="product-link-class")  # Replace with actual class
            
            products = []
            for element in product_elements:
                product_name = element.get_text(strip=True)
                product_link = element['href']
                products.append((product_name, f"{self.base_url}{product_link}"))
            
            return products
        except Exception as e:
            print(f"Error searching for products: {e}")
            messagebox.showinfo("Tulemused", f"Tekkis viga tooteotsingul: {e}")
            return []
        
    def show_product_selection(self, products):
        """Display a list of products for the user to select from."""
        def on_select():
            selected_index = listbox.curselection()
            if selected_index:
                selected_product = products[selected_index[0]]
                self.fetch_prices(selected_product[1], selected_product[0])
                selection_window.destroy()
            else:
                messagebox.showinfo("Valik", "Palun vali toode.")

        selection_window = Toplevel()
        selection_window.title("Vali toode")
        
        listbox = Listbox(selection_window, width=50, height=15)
        for product in products:
            listbox.insert(END, product[0])
        listbox.pack()

        select_button = Button(selection_window, text="Vali", command=on_select)
        select_button.pack()

    def fetch_prices(self, product_url, product_name):
        """Fetch prices for the selected product from its specific page."""
        try:
            response = requests.get(product_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            prices = {}
            for store_price in soup.find_all("div", class_="store-price-class"):  # Replace with actual class
                store_name = store_price.find("span", class_="store-name-class").get_text(strip=True)  # Update class
                price_text = store_price.find("span", class_="price-class").get_text(strip=True)  # Update class
                price = self.extract_price(price_text)
                
                if price is not None:
                    prices[store_name] = price

            self.display_prices(product_name, prices)
        except Exception as e:
            print(f"Error fetching prices for product: {e}")
            messagebox.showinfo("Tulemused", f"Tekkis viga hinnainfo toomisel: {e}")

    def extract_price(self, price_text):
        """Extracts a numerical price from a price text string."""
        try:
            price_text = price_text.replace("€", "").strip()
            price_text = price_text.replace(",", ".")  # Convert to a float-friendly format
            return float(price_text)
        except ValueError:
            return None
    def display_prices(self, product_name, prices):
        """Display prices in a message box for the selected product."""
        if prices:
            message = f"Hinnad tootele '{product_name}':\n"
            for store, price in prices.items():
                message += f"{store}: {price}€\n"
            messagebox.showinfo("Hinnad", message)
        else:
            messagebox.showinfo("Hinnad", f"Hinnad tootele '{product_name}' ei leitud.")

    def start_search(self, toode):
        """Initiates the search process for a given product name."""
        products = self.search_similar_products(toode)
        if products:
            self.show_product_selection(products)
        else:
            messagebox.showinfo("Tulemused", f"Tooteid sarnaste nimedega '{toode}' ei leitud.")
# Run the application
root = tk.Tk()
app = ToidupoodRakendus(root)
root.mainloop()

