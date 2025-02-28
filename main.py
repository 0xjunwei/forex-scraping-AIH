from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/api/rates', methods=['GET'])
def get_rates():
    # 1. Get currency from query parameter, default to "USD"
    currency = request.args.get('currency', 'USD').upper()

    # 2. List of banks to scrape
    bank_list = ["dbs", "uob", "ocbc"]  # Extend as needed

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
            rows = table.find_all("tr")[1:]  # skip header row
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

    return jsonify({
        "requested_currency": currency,
        "rates": results
    })

# Gunicorn requires a variable named "app" in the main module:
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
