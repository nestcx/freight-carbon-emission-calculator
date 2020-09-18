import math


def convert_kilogram_to_tonnes(kg):
    """This function converts kilograms to tones by multiplying the input which
    would be expected to be the kilograms by 0.001 to return tonnes
    Parameters:
    kg {float} -- the ammount of kilograms
    Returns:
    [float] -- the conversion of kilograms to tonnes
    """

    # the calculation for the function
    conversion = kg * 0.001

    return conversion


def litres_per_kilometre_to_litres_per_100km(litres):
    """This function coverts how many letres are being used per kilometre to 
    litres per 100 kilometres by multiplying the litre per kilomtre by 100

    Parameters:
    lires {float} -- the ammount of litres per kilometre
    Returns:
    [float] -- the conversion of litres per kilometres into litres per 100 kilometres
    """

    conversion = litres * 100

    return conversion


def kilometres_per_litre_to_litres_per_100km(km):
    """This function coverts how many kilometres per letre to litres per 100 
    kilometres by dividing the letres by the kilometres per letres then 
    multiplying by 100

    Parameters:
    km {float} -- the ammount of kilometres per litre
    Returns:
    [float] -- the conversion of kilometres per litre into litres per 100 kilometres
    """

    conversion = (1 / km) * 100

    return conversion


def metre_to_kilometre(metre):
    """This function converts metres to kilometres by multiplying the input 
    which would be expected to be the metres by 0.001 to return kilometres
    Parameters:
    metre {float} -- the ammount of metres
    Returns:
    [float] -- the conversion of metres to kilometres
    """

    conversion = metre * 0.001

    return conversion


# There are libraries that do a similar job to what this function does, but none
# were found that can format durations that exceed 24 hours
# TODO: Check if a library that provides this functionality exists
def convert_seconds_to_dhms(n):
    """Format the amount of time it will take from starting location to destination into a readable format

    Arguments:
    n {number} -- The amount of seconds

    Returns:
    [string] -- The amount of time in days, HH:MM:SS format
    """

    # Get the days by using the // operator which divides and returns the floor value (rounding down to an integer)
    days = n // (60 * 60 * 24)

    # Use the % operator to exclude the days and get the remaining hours
    n = n % (60 * 60 * 24)
    # Get the amount of hours by rounding down to the nearest integer
    hours = n // (60 * 60)

    # Exclude the hours to get the remaining minutes
    n = n % (60 * 60)
    minutes = n // 60

    seconds = math.floor(n % 60)

    # Format string to "HH:MM:SS"
    formatted_str = str(int(hours)).zfill(
        2) + ":" + str(int(minutes)).zfill(2) + ":" + str(int(seconds)).zfill(2)

    # If total duration exceeds 24 hours, prepend the number of days it will take to the beginning of the string
    if days != 0:
        return str(int(days)) + " days " + formatted_str
    else:
        return formatted_str
