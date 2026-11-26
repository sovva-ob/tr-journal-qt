def calculate_risk(entry, stop, direction):
    if direction == "Long":
        risk = entry - stop
    elif direction == "Short":
        risk = stop - entry
    else:
        raise ValueError("Choose Long or Short.")

    if risk <= 0:
        raise ValueError("Stop must be on the risk side of Entry.")
    return risk


def calculate_planned_r(entry, stop, target, direction):
    risk = calculate_risk(entry, stop, direction)
    if direction == "Long":
        reward = target - entry
    else:
        reward = entry - target
    if reward <= 0:
        raise ValueError("Target must be on the reward side of Entry")
    return reward / risk


def calculate_realized_r(entry, stop, exit_price, direction):
    risk = calculate_risk(entry, stop, direction)
    if direction == "Long":
        gain_or_loss = exit_price - entry
    else:
        gain_or_loss = entry - exit_price
    return gain_or_loss / risk