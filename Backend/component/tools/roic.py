from langchain_core.tools import tool
@tool
def roic(
    operating_income: float,
    total_debt: float,
    equity: float,
    cash_and_equivalents: float,
    tax_rate: float = 0.35,
) -> float:
    """
    Computes the return on invested capital (ROIC) for a given company.
    Use this function to evaluate the efficiency of a company in generating returns from its capital.
    """
    net_operating_profit_after_tax = operating_income * (1 - tax_rate)
    invested_capital = total_debt + equity - cash_and_equivalents
    return net_operating_profit_after_tax / invested_capital
