from flask import Flask, request, jsonify, render_template
import random

app = Flask(__name__)

# Product List (Name, Price, GST)
products = {
    "Oswal Soap": {"price": 63.56, "gst": 18},
    "Oswal Single": {"price": 7.288, "gst": 18},
    "Powder 1kg": {"price": 44.915, "gst": 18},
    "Powder 3kg": {"price": 134.745, "gst": 18},
    "Powder 5kg": {"price": 288.135, "gst": 18},
    "D.C. 5Mrp": {"price": 3.531, "gst": 18},
    "D.C. 10mrp": {"price": 7.0621, "gst": 18},
    "D.W. 500gm": {"price": 21.186, "gst": 18},
    "D.W. 1kg": {"price": 39.83, "gst": 18},
    "custom": {"price": 0, "gst": 5}
}

# Priorities for product selection (higher = more frequent)
product_priority = {
    "Oswal Soap": 4,     # High priority
    "Oswal Single": 3,   # High priority
    "Powder 1kg": 2,     # Medium priority
    "Powder 3kg": 2,     # Medium priority
    "Powder 5kg": 1,     # Low priority (reduced)
}

def best_fit_product(grand_total):
    best_result = None
    all_results = []

    for product_name, details in products.items():
        price, gst = details["price"], details["gst"]
        if price == 0:
            continue  # Skip custom product if price is zero
        
        initial_quantity = round(grand_total / ((100 + gst) / 100 * price) / 5) * 5
        if initial_quantity <= 0:
            continue  # Skip invalid quantities

        adjusted_price = price * grand_total / (price * initial_quantity * (1 + gst / 100))
        rounded_quantity = round(grand_total / ((100 + gst) / 100 * adjusted_price) / 5) * 5
        new_grand_total = adjusted_price * rounded_quantity * (1 + gst / 100)

        result = {
            "Product": product_name,
            "Quantity": rounded_quantity,
            "Price": round(adjusted_price, 2),
            "Gross_Total": round(adjusted_price * rounded_quantity, 2),
            "SGST": round(adjusted_price * rounded_quantity * gst / 200, 2),
            "CGST": round(adjusted_price * rounded_quantity * gst / 200, 2),
            "Grand_Total": round(new_grand_total, 2),
            "Priority": product_priority.get(product_name, 1)  # Default priority = 1 if not in list
        }

        all_results.append(result)

    # Sort by priority, then closest Grand Total match
    all_results.sort(key=lambda x: (-x["Priority"], abs(grand_total - x["Grand_Total"])))

    # Select a product with some randomness to prevent repeating the same product
    best_result = random.choices(all_results, weights=[r["Priority"] for r in all_results], k=1)[0]

    return best_result

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/calculate", methods=["POST"])
def calculate():
    try:
        data = request.get_json()
        grand_total = float(data["grand_total"])
        result = best_fit_product(grand_total)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
