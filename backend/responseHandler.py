yes = ["y", "yeah", "yes", "yep", "affirmative"]
no = ["n", "no", "nope", "nah", "nay", "never", "not"]


def yesorno(userInpt):
    userInpt = userInpt.lower()
    for word in userInpt.split(" "):
        if word in yes:
            return True
        elif word in no:
            return False
    for word in yes:
        if word in userInpt:
            return True
    for word in no:
        if word in userInpt:
            return False
