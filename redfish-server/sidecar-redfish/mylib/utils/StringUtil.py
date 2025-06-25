import string
import random

class StringUtil:
    @classmethod
    def shuffle_string(cls, s):
        return ''.join(random.choice(s) for _ in range(len(s)))
    
    @classmethod
    def random(cls, n=6):
        # string.ascii_uppercase # 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        # string.ascii_lowercase 
        # string.digits # '0123456789'
        choice_str = string.ascii_uppercase + string.digits
        # return ''.join(random.choice(choice_str) for _ in range(n))
        return cls.shuffle_string(choice_str)[0:n]
    