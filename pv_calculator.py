import numpy as np
from financial import xnpv, xirr
from datetime import datetime, timedelta


FORMAT = "{:,.2f}"
LCOE = 0.486848656921709;

class PVCalculator:

    def calculate_cashflows(self, input_parameters):
        project_lifetime = int(input_parameters["project_lifetime"])
        
        power_degradation = float(input_parameters["degradation_percent_per_year"])

        nominal_power_kwp = float(input_parameters["nominal_power_kwp"])
        annual_yield_kwh_kwp = float(input_parameters["annual_yield_kwh_kwp"])
        degradation_percent_per_year = float(input_parameters["degradation_percent_per_year"])
        years = int(input_parameters["years"])
        price_eur_per_kwh = float(input_parameters["price_eur_per_kwh"])
        fit_period = 1 if years <= project_lifetime and price_eur_per_kwh > 0 else 0
        index_percent = float(input_parameters["index_percent"])
        total_installation_price_eur = float(input_parameters["total_installation_price_eur"])
        insurance_premium_percent = float(input_parameters["insurance_premium_percent"])
        maintenance_percent = float(input_parameters["maintenance_percent"])
        inflation_rate_percent = float(input_parameters["inflation_rate_percent"])
        discount_rate_percent = float(input_parameters["discount_rate_percent"])

        cashflows = {}


        for year in range(1, project_lifetime + 1):
            power_degradation_year = (100 - (power_degradation * (year-1)) ) / 100
            energy_production_kwh = nominal_power_kwp * annual_yield_kwh_kwp * power_degradation_year
            revenue_fit_eur = energy_production_kwh * price_eur_per_kwh
            inflation_rate_accumulation = (1 + (inflation_rate_percent / 100)) ** (year-1)
            insurance_eur = (insurance_premium_percent / 100) * total_installation_price_eur * inflation_rate_accumulation * -1
            maintenance_eur = (maintenance_percent / 100) * total_installation_price_eur * inflation_rate_accumulation * -1
            earnings_eur = revenue_fit_eur + insurance_eur + maintenance_eur
            remaining_power_kwh = nominal_power_kwp * (1 - (power_degradation / 100)) ** year
            roi_calculation = earnings_eur  
            npv_calculation = earnings_eur

            if year == 1:
                income_cumulative_eur = earnings_eur
            else:
                income_cumulative_eur += earnings_eur

            lcoe_eur = LCOE;  # You need to implement the LCOE calculation here
            income_with_lcoe_eur = energy_production_kwh * lcoe_eur
            income_after_costs_eur = income_with_lcoe_eur + insurance_eur + maintenance_eur
            discounted_cash_eur = income_after_costs_eur / (1 + (discount_rate_percent / 100)) ** year
            if year == 1:
                present_value_eur = discounted_cash_eur
            else:
                present_value_eur += discounted_cash_eur

            cashflows[year] = {
                "energy_production": energy_production_kwh,
                "revenue_fit": revenue_fit_eur,
                "insurance": insurance_eur,
                "maintenance": maintenance_eur,
                "earnings": earnings_eur,
                "income_cumulative": income_cumulative_eur,
                "lcoe": lcoe_eur,
                "income_with_lcoe": income_with_lcoe_eur,
                "income_after_costs": income_after_costs_eur,
                "discounted_cash": discounted_cash_eur,
                "present_value": total_installation_price_eur - present_value_eur,
                "project_lifetime": project_lifetime - year + 1,
                "fit_period": fit_period,
                "roi_calculation":  roi_calculation,
                "npv_calculation":  npv_calculation,
                "power_degradation": power_degradation_year * 100,
                "remaining_power":  remaining_power_kwh
            }

        return cashflows

    def calculate_summary(self, cashflows, input_parameters):
        # Calculate the summary fields based on the cash flow data
        nominal_power_kw = input_parameters["nominal_power_kwp"]
        
        earning_cashflows = self.generate_earning_tuples(cashflows, int(input_parameters["project_lifetime"]))
        present_net_income_eur = xnpv(float(input_parameters["discount_rate_percent"])/100, earning_cashflows)
        # net_income_eur = np.sum([earning for date, earning in earning_cashflows])


        lcoe_eur_per_kwh = LCOE
        roi_percent = xirr(earning_cashflows) * 100
        npv_eur = present_net_income_eur - float(input_parameters["total_installation_price_eur"])

        return {
            "nominal_power_kw": nominal_power_kw,
            "net_income_eur": present_net_income_eur,
            "lcoe_eur_per_kwh": "%.04f" % lcoe_eur_per_kwh,
            "roi_percent": roi_percent,
            "npv_eur": npv_eur
        }
    
    def generate_earning_tuples(self, cashflows, project_lifetime):
        earning_tuples = []

        # Iterate through the years and extract earnings for each year
        for year in range(1, project_lifetime + 1):
            # The cashflows dictionary has results for each year
            earnings = cashflows.get(year, {}).get('earnings', 0)
            
            # Create a date for January 1st of the current year
            date = datetime(datetime.now().year + year, 1, 1)

            earning_tuples.append((date, earnings))

        return earning_tuples
    
    def calculate_lcoe(self, capital_cost, annual_om_costs, lifetime, annual_energy_production, discount_rate_percent):
        # Convert discount rate from percentage to decimal
        discount_rate = discount_rate_percent / 100

        # Calculate the present value of capital costs using the annuity formula
        capital_pv = capital_cost * (discount_rate / (1 - (1 + discount_rate) ** -lifetime))

        # Calculate the present value of annual operating and maintenance costs
        om_pv = annual_om_costs * (1 - (1 + discount_rate) ** -lifetime) / discount_rate

        # Calculate the total present value of costs
        total_costs = capital_pv + om_pv

        # Calculate the total electricity produced
        total_energy_produced = annual_energy_production * lifetime

        # Calculate the LCOE
        lcoe = total_costs / total_energy_produced

        return lcoe
