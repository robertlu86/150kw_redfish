from mylib.components_summary.base_component_summary import BaseComponentSummary

class FanComponentSummary(BaseComponentSummary):
  def __init__(self):
    self.sensor_data_path = "sensor_data.json"
    self.init()

  def init(self):
    # read data
    self.sensor_data = {}
    pass

  def summary(self):
    pass