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
    Computes the Return on Invested Capital (ROIC) for a given company.

    ROIC is a key financial metric that measures how efficiently a company
    generates profit from its invested capital.

    Parameters:
        operating_income (float): Earnings before interest and taxes (EBIT).
        total_debt (float): Total debt of the company.
        equity (float): Total shareholder equity.
        cash_and_equivalents (float): Cash or cash equivalents on the balance sheet.
        tax_rate (float, optional): The applicable corporate tax rate (default is 35%).

    Returns:
        float: The ROIC value calculated as Net Operating Profit After Tax (NOPAT) divided by invested capital.
    """

    # Calculate Net Operating Profit After Tax (NOPAT)
    net_operating_profit_after_tax = operating_income * (1 - tax_rate)

    # Calculate invested capital (debt + equity - cash & equivalents)
    invested_capital = total_debt + equity - cash_and_equivalents

    # Calculate and return the ROIC ratio
    return net_operating_profit_after_tax / invested_capital
