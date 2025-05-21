from langchain_core.tools import tool

@tool
def percentage_change(start: float, end: float):
    """
    Calculate the percentage change between two numerical values: start and end.

    Parameters:
        start (float): The initial value (must not be zero).
        end (float): The final value.

    Returns:
        float: The percentage change from start to end, rounded to two decimals.

    Raises:
        ValueError: If the start value is zero to avoid division by zero.
    """

    # Validate input to prevent division by zero
    if start == 0:
        raise ValueError("Start cannot be zero")

    # Calculate the absolute change between end and start
    price_change = end - start

    # Compute the percentage change relative to start
    percentage_change = (price_change / start) * 100

    # Return the percentage change rounded to 2 decimal places
    return round(percentage_change, 2)
