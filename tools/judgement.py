# judgement.py

JUDGEMENT_WINDOWS = {
    'sick': 45,
    'good': 90,
    'bad': 115,
    'abysmal dogshit': 135,
    'miss': 135  # used as upper bound in logic, not returned directly
}

def evaluate(note, press_time):
    """Return 'sick', 'good', 'bad', or 'miss' based on time difference."""
    diff = abs(press_time - note.time_ms)

    if diff <= JUDGEMENT_WINDOWS['sick']:
        return 'sick'
    elif diff <= JUDGEMENT_WINDOWS['good']:
        return 'good'
    elif diff <= JUDGEMENT_WINDOWS['bad']:
        return 'bad'
    elif diff <= JUDGEMENT_WINDOWS['abysmal dogshit']:
        return 'abysmal dogshit'
    else:
        return 'miss'

def window(label):
    """Return the window size in ms for a given judgement type."""
    return JUDGEMENT_WINDOWS.get(label, 9999)
