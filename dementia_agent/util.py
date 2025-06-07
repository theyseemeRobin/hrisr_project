import time


def get_yes_or_no(question: str) -> bool:
    """
    Ask a yes or no question and return True for 'yes' and False for 'no'.

    Args:
        question (str): The question to ask.

    Returns:
        bool: True if the answer is 'yes', False if the answer is 'no'.
    """
    while True:
        answer = input(question + " (yes/no): ").strip().lower()
        if answer in ['yes', 'y']:
            return True
        elif answer in ['no', 'n']:
            return False
        else:
            print("Please answer with 'yes' (y) or 'no' (n).")

def get_time(question: str) -> str:
    """
    Ask for a time input and return it as a string.

    Args:
        question (str): The question to ask.

    Returns:
        str: The time input provided by the user.
    """
    while True:
        time_input = input(question + " (HH:MM): ").strip()
        try:
            # Validate the time format
            time.strptime(time_input, "%H:%M")
            return time_input
        except ValueError:
            print("Invalid time format. Please enter in HH:MM format.")

def get_day(question: str) -> str:
    """
    Ask for a day input and return it as a string.

    Args:
        question (str): The question to ask.

    Returns:
        str: The day input provided by the user.
    """
    while True:
        day_input = input(question + " (e.g., Monday): ").strip()
        # Validate the day input
        if day_input.lower() in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
            return day_input.capitalize()
        else:
            print("Invalid day. Please enter a valid day of the week.")