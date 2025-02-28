import requests
from bs4 import BeautifulSoup
import json

def remittance_webhook(request):
    # Get the request data from Dialogflow
    request_data = request.get_json()
    # Extract the currency parameter from session parameters
    currency = request_data['sessionInfo']['parameters']['currency'].upper()
    
    # List of banks to scrape (same as your script)
    bank_list = ["dbs", "uob", "ocbc"]  # Extend as needed
    
    # Perform the scraping (directly from your Flask logic)
    results = {}
    for bank in bank_list:
        url = f"https://www.sgrates.com/bankrate/{bank}.html"
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            table = soup.find("table")
            if not table:
                results[bank] = "Table not found"
                continue
            
            exchange_rates = {}
            rows = table.find_all("tr")[1:]  # Skip header row
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 6:
                    currency_symbol = cols[0].text.split()[-1].strip("()")
                    bank_sell_tt = cols[2].text.strip()
                    try:
                        exchange_rates[currency_symbol] = round(1 / float(bank_sell_tt), 6)
                    except ValueError:
                        exchange_rates[currency_symbol] = "N/A"
            
            results[bank] = exchange_rates.get(currency, "N/A")
        else:
            results[bank] = f"Failed to retrieve data. HTTP {response.status_code}"
    
    # Process results to find the best rate (customized for Dialogflow response)
    valid_rates = {bank: rate for bank, rate in results.items() if isinstance(rate, float)}
    if valid_rates:
        best_bank = max(valid_rates, key=valid_rates.get)
        best_rate = valid_rates[best_bank]
        response_message = f"The bank with the best rate for {currency} is {best_bank.upper()} with a rate of {best_rate:.2f}."
    else:
        response_message = f"No valid rates found for {currency}."
    
    # Format the response for Dialogflow CX
    fulfillment_response = {
        "fulfillment_response": {
            "messages": [
                {
                    "text": {
                        "text": [response_message]
                    }
                }
            ]
        }
    }
    
    return json.dumps(fulfillment_response)
