from langchain_core.tools import tool


@tool
def roe(
    net_income: float,
    equity: float,
) -> float:
    """
    Computes the return on equity (ROE) for a given company.
    Use this function to evaluate the profitability of a company.
    """
    return net_income / equity


