import bcrypt

def encrypt_password(password: str) -> str:
    """
    Encrypts the password using bcrypt

    The salt is in the hash, so no need to store it separately.
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def check_password(password: str, hashed_password: str) -> bool:
    """
    Checks if the password matches the hashed password
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))