from typing import Optional, Any
from functools import reduce

class JsonUtil:
    @classmethod
    def get_nested_value(cls, data: dict, path: str, path_separator: str = ".") -> Optional[Any]:
        """
        ex:
        data = {
            "layer1": {
                "layer2": {
                    "layer3": {
                        "key1":"value1", 
                        "key2":"value2"
                    }
                }
            }
        }
        JsonUtil.get_nested_value(data, "layer1.layer2") # => {'layer3': {'key1': 'value1', 'key2': 'value2'}}
        JsonUtil.get_nested_value(data, "layer1.layer2.layer3.key2") # => 'value2'
        JsonUtil.get_nested_value(data, "layer1/layer2/layer3/key2", path_separator="/") # => 'value2'
        """
        try:
            return reduce(lambda d, k: d[k], path.split(path_separator), data)
        except (KeyError, TypeError):
            return None

       