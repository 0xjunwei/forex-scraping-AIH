from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

app = Flask(__name__)


def get_western_union_rate(country_code):
    driver = webdriver.Firefox()
    try:
        url = f"https://www.westernunion.com/sg/en/web/send-money/start?ReceiveCountry={country_code}&ISOCurrency=INR&SendAmount=1000.00&FundsOut=AG&FundsIn=PayNow"
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "exchangeRate"))
        )
        exchange_rate_element = driver.find_element(By.ID, "exchangeRate")
        rate_text = exchange_rate_element.text
        parts = rate_text.split()
        if len(parts) == 2:
            rate_value = parts[0]
            return rate_value
        return "Rate not found"
    except Exception as e:
        print(f"Error: {e}")
        return "Rate not found"
    finally:
        driver.quit()


@app.route("/get_rate", methods=["GET"])
def get_rate():
    # Get country_code from query parameters, default to 'IN' if not provided
    country_code = request.args.get("country_code", default="IN", type=str).upper()

    # Validate country code length
    if len(country_code) != 2:
        return (
            jsonify(
                {
                    "error": "Invalid country code. Please provide a 2-letter abbreviation."
                }
            ),
            400,
        )

    # Get the exchange rate
    rate = get_western_union_rate(country_code)

    # Return appropriate JSON response
    if rate == "Rate not found":
        return jsonify({"error": "Rate not found"}), 404
    return jsonify({"exchange_rate": rate}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
    # print(get_western_union_rate("IN"))
