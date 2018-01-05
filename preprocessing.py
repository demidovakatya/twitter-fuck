tws = []
current_tw = ''
next_tw = ''
for line in all:
    # current_tw = ''
    next_tw += line
    if len(next_tw) >= 140:
        tws.append(current_tw)
        current_tw = ''
        next_tw = ''
    else:
        current_tw += line
        current_tw += " "