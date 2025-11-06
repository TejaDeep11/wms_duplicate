import bcrypt

def hash_password(plain_password):
    """
    Hashes a plain-text password using bcrypt.
    """
    # 1. Encode the password to bytes
    password_bytes = plain_password.encode('utf-8')

    # 2. Generate a "salt" (random data) and hash the password
    # The salt is automatically included in the final hash string
    hashed_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

    # 3. Decode the hash back to a string to store in the database
    hashed_string = hashed_bytes.decode('utf-8')
    
    return hashed_string

def check_password(plain_password_attempt, hash_from_db):
    """
    Checks a login attempt against a stored hash.
    """
    try:
        # 1. Encode both the attempt and the stored hash to bytes
        attempt_bytes = plain_password_attempt.encode('utf-8')
        hash_bytes = hash_from_db.encode('utf-8')

        # 2. Use bcrypt's checkpw function
        # This securely compares the two
        return bcrypt.checkpw(attempt_bytes, hash_bytes)
    
    except Exception as e:
        # (e.g., if the hash_from_db is not a valid hash)
        print(f"Error checking password: {e}")
        return False

# --- Run this script once to get your hashes ---

# Passwords for your sample users
passwords = {
    'admin124@gmail.com': 'admin_pass',
    'supriya.pathrik12@gmail.com': 'supriya_pass',
    'vijay.kumar78k@gmail.com': 'vijay_pass',
    'ananya.rao5@67@gmail.com': 'ananya_pass'
}

print("--- Generated Hashes for your INSERT statements ---")

for email, plain_pass in passwords.items():
    user_hash = hash_password(plain_pass)
    print(f"Email: {email}\nHash: {user_hash}\n")