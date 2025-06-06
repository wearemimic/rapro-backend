import datetime
from decimal import Decimal
from core.models import Scenario, Client, Spouse, IncomeSource

class ScenarioProcessor:
    def __init__(self, scenario_id, debug=False):
        self.debug = debug
        self.scenario = Scenario.objects.get(id=scenario_id)
        self.client = self.scenario.client
        self.spouse = getattr(self.client, "spouse", None)
        self.primary_birthdate = self.client.birthdate
        self.spouse_birthdate = self.spouse.birthdate if self.spouse else None
        self.tax_status = self.client.tax_status
        self.assets = list(self.scenario.income_sources.values())

        current_year = datetime.datetime.now().year
        retirement_age_primary = self.scenario.retirement_age or 65
        retirement_age_spouse = getattr(self.scenario, 'spouse_retirement_age', None) or 65
        mortality_age_primary = self.scenario.mortality_age or 90
        mortality_age_spouse = getattr(self.scenario, 'spouse_mortality_age', None) or mortality_age_primary

        current_age_primary = current_year - self.primary_birthdate.year
        if self.spouse_birthdate:
            current_age_spouse = current_year - self.spouse_birthdate.year
        else:
            current_age_spouse = None

        if self.tax_status == "Single" or not self.spouse_birthdate:
            years_until_retirement = retirement_age_primary - current_age_primary
            self.start_year = current_year + max(years_until_retirement, 0)
        else:
            years_until_retirement_primary = retirement_age_primary - current_age_primary
            years_until_retirement_spouse = retirement_age_spouse - current_age_spouse
            start_year_primary = current_year + max(years_until_retirement_primary, 0)
            start_year_spouse = current_year + max(years_until_retirement_spouse, 0)
            self.start_year = min(start_year_primary, start_year_spouse)

        end_year_primary = self.primary_birthdate.year + mortality_age_primary
        end_year_spouse = self.spouse_birthdate.year + mortality_age_spouse if self.spouse_birthdate else end_year_primary

        max_end_year = max(end_year_primary, end_year_spouse)

        for asset in self.assets:
            start_age = asset.get("age_to_begin_withdrawal")
            end_age = asset.get("age_to_end_withdrawal")
            owner = asset.get("owned_by", "primary")
            birthdate = self.primary_birthdate if owner == "primary" else self.spouse_birthdate
            if birthdate and end_age is not None:
                asset_end_year = birthdate.year + end_age
                if asset_end_year > max_end_year:
                    max_end_year = asset_end_year

        self.end_year = max_end_year

    def calculate(self):
        results = []
        cumulative_federal_tax = 0
        for year in range(self.start_year, self.end_year + 1):
            primary_age = year - self.primary_birthdate.year
            spouse_age = year - self.spouse_birthdate.year if self.spouse_birthdate else None

            gross_income = self._calculate_gross_income(year)
            ss_income = self._calculate_social_security(year)
            taxable_income = self._calculate_taxable_income(gross_income, ss_income)
            federal_tax = self._calculate_federal_tax(taxable_income)
            cumulative_federal_tax += federal_tax
            medicare_base, irmaa, total_medicare = self._calculate_medicare_costs(taxable_income)
            net_income = gross_income + ss_income - federal_tax - total_medicare

            summary = {
                "year": year,
                "primary_age": primary_age,
                "spouse_age": spouse_age if self.tax_status != "Single" else None,
                "gross_income": round(gross_income, 2),
                "ss_income": round(ss_income, 2),
                "taxable_income": round(taxable_income, 2),
                "federal_tax": round(federal_tax, 2),
                "cumulative_federal_tax": round(cumulative_federal_tax, 2),
                "medicare_base": round(medicare_base, 2),
                "irmaa": round(irmaa, 2),
                "total_medicare": round(total_medicare, 2),
                "net_income": round(net_income, 2)
            }

            self._log_debug(f"Year {year}: {summary}")
            results.append(summary)
        return results

    def _calculate_gross_income(self, year: int) -> float:
        self._log_debug(f"Processing gross income for year {year}")
        income_total = 0
        for asset in self.assets:
            owner = asset.get("owned_by", "primary")
            birthdate = self.primary_birthdate if owner == "primary" else self.spouse_birthdate
            if not birthdate:
                continue

            current_age = year - birthdate.year
            start_age = asset.get("age_to_begin_withdrawal")
            end_age = asset.get("age_to_end_withdrawal")
            cola = Decimal(asset.get("cola", 0)) / 100  # Cost of Living Adjustment as decimal, e.g., 0.02 for 2%

            self._log_debug(f"  Asset: {asset}, Current Age: {current_age}, Start Age: {start_age}, End Age: {end_age}, COLA: {cola}")

            if start_age is not None and end_age is not None and start_age <= current_age <= end_age:
                years_since_start = current_age - start_age
                monthly_amount = asset.get("monthly_amount", 0)
                inflated_amount = monthly_amount * (Decimal(1 + cola) ** years_since_start)
                income_total += inflated_amount * 12  # Annualize monthly income

        return income_total

    def _calculate_social_security(self, year):
        self._log_debug(f"Processing social security income for year {year}")
        total_ss = 0
        for asset in self.assets:
            if asset.get("income_type") == "Social Security":
                owner = asset.get("owned_by", "primary")
                birthdate = self.primary_birthdate if owner == "primary" else self.spouse_birthdate
                if not birthdate:
                    continue
                current_age = year - birthdate.year
                start_age = asset.get("age_to_begin_withdrawal")
                end_age = asset.get("age_to_end_withdrawal")
                cola = asset.get("cola", 0)

                self._log_debug(f"  SS Asset: {asset}, Current Age: {current_age}, Start Age: {start_age}, End Age: {end_age}, COLA: {cola}")

                if start_age is not None and end_age is not None and start_age <= current_age <= end_age:
                    years_since_start = current_age - start_age
                    monthly_amount = asset.get("monthly_amount", 0)
                    inflated_amount = monthly_amount * (Decimal(1 + cola) ** years_since_start)
                    total_ss += inflated_amount * 12
        return total_ss

    def _calculate_taxable_income(self, gross_income, ss_income):
        return gross_income + ss_income * Decimal("0.85")

    def _calculate_federal_tax(self, taxable_income):
        if self.tax_status == "Single":
            return taxable_income * Decimal("0.15")
        return taxable_income * Decimal("0.12")

    def _calculate_medicare_costs(self, taxable_income):
        base = 1700
        irmaa = 0
        if taxable_income > 97000:
            irmaa = 1000
        return base, irmaa, base + irmaa

    def _log_debug(self, message):
        if self.debug:
            print(f"🔍 Debug: {message}")
