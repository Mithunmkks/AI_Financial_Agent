from langchain_core.tools import tool

@tool
def roe(
    net_income: float,
    equity: float,
) -> float:
    """
    Computes the Return on Equity (ROE) for a given company.

    ROE is a key financial metric that measures a company's profitability by revealing
    how much profit a company generates with the money shareholders have invested.

    Parameters:
        net_income (float): The company's net income over a period.
        equity (float): The shareholder's equity during the same period.

    Returns:
        float: The ROE ratio, calculated as net income divided by equity.
    """

    # Calculate and return the ROE value
    return net_income / equity
