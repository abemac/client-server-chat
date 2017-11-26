from hashlib import md5
def gethash(string):
    m=md5()
    m.update(string.encode())
    return m.hexdigest()
