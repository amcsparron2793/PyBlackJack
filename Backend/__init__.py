def yes_no(question):
    while True:
        reply = str(input(question+' (y/n): ')).lower().strip()
        if reply[0] == 'y': return True
        if reply[0] == 'n': return False