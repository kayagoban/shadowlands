import hashlib

def filehasher(app_zipfile):
    hasher = hashlib.sha256()
    with open(str(app_zipfile), 'rb') as afile:
        buf = afile.read()
        hasher.update(buf)
        return hasher.hexdigest()
