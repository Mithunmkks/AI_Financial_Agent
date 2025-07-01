from langchain_core.tools import tool

@tool
def owner_earnings(
    net_income: float,
    depreciation_amortization: float = 0.0,
    capital_expenditures: float = 0.0
):
    """
    Calculates the owner earnings for a company based on the net income, depreciation/amortization, and capital expenditures.
    """
    return net_income + depreciation_amortization - capital_expenditures

