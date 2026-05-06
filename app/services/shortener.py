import random
import string
from app.models.link import Link
# Base62 alphabet: 0-9, A-Z, a-z = 62 characters total
ALPHABET = string.digits + string.ascii_uppercase + string.ascii_lowercase

def generate_short_key(db,length=6):
    # Randomly pick 'length' characters from ALPHABET, then join into a string
    # 62^6 = ~56 billion combinations — low collision risk
    while True:
         short_key = ''.join(random.choices(ALPHABET, k=length))
         link = db.query(Link).filter(Link.short_key == short_key).first()
         if not link: 
          break
    return short_key 