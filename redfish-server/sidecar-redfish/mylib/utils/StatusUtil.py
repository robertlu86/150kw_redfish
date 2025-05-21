from typing import Optional
from mylib.models.rf_status_model import RfStatusModel

class StatusUtil:
    @classmethod
    def get_worst_health(cls, status_list: list[RfStatusModel]) -> Optional[RfStatusModel]:
        """
        取得所有status_list當中，健康度(Health)最差的
        """
        ret_status = None
        for s in status_list:
            if ret_status is None:
                ret_status = s
            else:
                if s.numeric_health_value() > ret_status.numeric_health_value():
                    ret_status = s
        return ret_status

    # @classmethod
    # def init_from_dict(cls, status_dict: dict) -> RfStatusModel:
    #     return RfStatusModel(
    #         Health=status_dict.get("Health") or status_dict.get("health"),
    #         State=status_dict.get("State") or status_dict.get("state")
    #     )
    
    @classmethod
    def get_worst_health_dict(cls, status_list: list[dict]) -> Optional[dict]:
        """
        取得所有status_list當中，健康度(Health)最差的
        """
        rf_status_models = []
        for status_dict in status_list:
            rf_status_models.append(RfStatusModel.from_dict(status_dict))
        worst_health_status = cls.get_worst_health(rf_status_models)
        return worst_health_status.to_dict()    