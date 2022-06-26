import hashlib

def equal_file_hashes(a, b) -> bool:
    """computes the hash of each file and compares them
    returns True if they are equal"""
    BUF_SIZE = 4096

    a_hashed = hashlib.sha256()
    b_hashed = hashlib.sha256()
   
    with open(a, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            a_hashed.update(data)
    
    with open(b, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            b_hashed.update(data)
    return a_hashed.hexdigest() == b_hashed.hexdigest()
