
class ProjError(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
    
    def to_dict(self):
        return {
            "code": self.code,
            "message": self.message
        }
    
    def to_dict_v2(self):
        return {
            "error": {
                "code": self.code,
                "message": self.message
            }
        }
        