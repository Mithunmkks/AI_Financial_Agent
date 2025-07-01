from langchain_core.tools import tool


@tool
def percentage_change(start: float, end: float):
    """
    Calculate the percentage change between two floats, start and end.

    :param start: The starting value
    :param end: The end value
    :return: The percentage change as a float
    """
    if start == 0:
        raise ValueError("Start cannot be zero")

    price_change = end - start
    percentage_change = (price_change / start) * 100

    return round(percentage_change, 2)