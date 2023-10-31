from flask import Flask, render_template, request
from pv_calculator import PVCalculator

app = Flask(__name__)
calculator = PVCalculator()

# Define a route for the main page
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Retrieve input parameters from the form
        input_parameters = {
            "project_lifetime": request.form.get("project_lifetime"),
            "nominal_power_kwp": request.form.get("nominal_power_kwp"),
            "annual_yield_kwh_kwp": request.form.get("annual_yield_kwh_kwp"),
            "degradation_percent_per_year": request.form.get("degradation_percent_per_year"),
            "years": request.form.get("years"),
            "price_eur_per_kwh": request.form.get("price_eur_per_kwh"),
            "index_percent": request.form.get("index_percent"),
            "total_installation_price_eur": request.form.get("total_installation_price_eur"),
            "insurance_premium_percent": request.form.get("insurance_premium_percent"),
            "maintenance_percent": request.form.get("maintenance_percent"),
            "inflation_rate_percent": request.form.get("inflation_rate_percent"),
            "discount_rate_percent": request.form.get("discount_rate_percent"),
        }

        # Calculate LCOE and NPV based on input parameters
        # lcoe, npv = calculator.calculate_lcoe_npv(input_parameters)

        
        cashflows = calculator.calculate_cashflows(input_parameters)
        summary = calculator.calculate_summary(cashflows, input_parameters)

        # Render the result template with the calculated values
        return render_template("result.html", cashflows=cashflows, summary=summary)

    # Render the input form if it's a GET request
    return render_template("input.html")

@app.template_filter('currency')
def currency_filter(value):
    return "{:,.2f}".format(value)

if __name__ == "__main__":
    app.run(debug=True)
