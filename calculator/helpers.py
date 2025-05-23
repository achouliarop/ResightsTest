def parse_share_string(share_string):
    """
    Parse a share string into numerical values.
    Args:
        share_string (str): Share string in format like "50%", "10-15%", or "<10%".
                            Returns (0.0, 0.0, 0.0) for malformed or empty strings.
    Returns:
        tuple: (lower_percentage, avg_percentage, upper_percentage) as fractions (e.g., 0.5 for 50%).
    """
    share_val = share_string.rstrip('%')
    
    if not share_val:
        return 0.0, 0.0, 0.0

    if '-' in share_val:
        try:
            parts = share_val.split('-')
            if len(parts) != 2:
                return 0.0, 0.0, 0.0
            lower, upper = map(float, parts)
            if lower > upper:
                lower, upper = upper, lower
            avg = (lower + upper) / 2.0
            return lower / 100.0, avg / 100.0, upper / 100.0
        except ValueError:
            return 0.0, 0.0, 0.0
    elif share_val.startswith('<'):
        try:
            upper = float(share_val[1:])
            avg = upper / 2.0 # Lower is 0
            return 0.0, avg / 100.0, upper / 100.0
        except ValueError:
            return 0.0, 0.0, 0.0
    else:
        try:
            value = float(share_val)
            return value / 100.0, value / 100.0, value / 100.0
        except ValueError:
            return 0.0, 0.0, 0.0

def multiply_shares(share_tuple1, share_tuple2):
    """
    Multiplies two share tuples (lower, avg, upper).
    Assumes share_tuple components are fractions (e.g., 0.5 for 50%).
    The resulting average is recalculated as (new_lower + new_upper) / 2.
    """
    l1, _, u1 = share_tuple1
    l2, _, u2 = share_tuple2

    new_lower = l1 * l2
    new_upper = u1 * u2
    new_avg = (new_lower + new_upper) / 2.0
    return new_lower, new_avg, new_upper

def add_shares(share_tuple1, share_tuple2):
    """
    Adds two share tuples (lower, avg, upper).
    Assumes share_tuple components are fractions (e.g., 0.5 for 50%).
    The resulting average is recalculated as (new_lower + new_upper) / 2.
    Results are rounded to avoid floating-point precision issues.
    """
    l1, _, u1 = share_tuple1
    l2, _, u2 = share_tuple2

    # Shares can exceed 1.0 if an entity is owned through multiple paths by the same ultimate owner.
    # Clamping at 1.0 is needed as an entity can't own more than 100% of another entity.
    new_lower = round(min(1.0, l1 + l2), 10)
    new_upper = round(min(1.0, u1 + u2), 10)
    new_avg = round((new_lower + new_upper) / 2.0, 10)
    return new_lower, new_avg, new_upper

def update_edge_shares(edge, share_tuple):
    """
    Updates edge with new share values.
    
    Args:
        edge (dict): Edge to update
        share_tuple (tuple): (lower, average, upper) share values as fractions
    """
    edge['real_lower_share'] = round(share_tuple[0] * 100.0, 2)
    edge['real_average_share'] = round(share_tuple[1] * 100.0, 2)
    edge['real_upper_share'] = round(share_tuple[2] * 100.0, 2)
    
def get_share_tuple_from_edge(edge):
    """
    Extracts share tuple from an edge, converting percentages to fractions.
    
    Args:
        edge (dict): Edge with real share values
        
    Returns:
        tuple: (lower, average, upper) share values as fractions
    """
    return (
        edge['real_lower_share'] / 100.0,
        edge['real_average_share'] / 100.0,
        edge['real_upper_share'] / 100.0
    )