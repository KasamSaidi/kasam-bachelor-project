from passlib.hash import bcrypt


def hash_password(password):
    hasher = bcrypt.using(rounds=13)
    hashed_password = hasher.hash(password)
    return hashed_password
