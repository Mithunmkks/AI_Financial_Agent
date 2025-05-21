from langchain_core.tools import tool

@tool
def intrinsic_value(
    free_cash_flow: float,
    growth_rate: float = 0.05,
    discount_rate: float = 0.10,
    terminal_growth_rate: float = 0.02,
    num_years: int = 5,
) -> float:
    """
    Computes the discounted cash flow (DCF) intrinsic value of a company based on its free cash flow.

    Parameters:
        free_cash_flow (float): The current free cash flow of the company.
        growth_rate (float): Expected annual growth rate of free cash flow (default: 5%).
        discount_rate (float): The discount rate used to present-value future cash flows (default: 10%).
        terminal_growth_rate (float): The perpetual growth rate used for terminal value calculation (default: 2%).
        num_years (int): Number of years to project cash flows (default: 5).

    Returns:
        float: The estimated intrinsic value based on the discounted cash flow model.
    """
    # Step 1: Estimate future free cash flows over the projection period
    cash_flows = [
        free_cash_flow * (1 + growth_rate) ** i  # Growth applied for each future year
        for i in range(num_years)
    ]

    # Step 2: Calculate present value of each projected cash flow
    present_values = []
    for i in range(num_years):
        present_value = cash_flows[i] / (1 + discount_rate) ** (i + 1)  # Discount each cash flow to present value
        present_values.append(present_value)

    # Step 3: Calculate terminal value using the Gordon Growth Model
    terminal_value = (
        cash_flows[-1] * (1 + terminal_growth_rate) / (discount_rate - terminal_growth_rate)
    )
    terminal_present_value = terminal_value / (1 + discount_rate) ** num_years  # Discount terminal value to present

    # Step 4: Sum present values of projected cash flows and terminal value
    dcf_value = sum(present_values) + terminal_present_value

    return dcf_value
