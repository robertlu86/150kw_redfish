from abc import ABC, abstractmethod


class BaseComponentSummary(ABC):
  def __init__(self):
    self.sensor_data_path = "sensor_data.json"
    self.init()

  @abstractmethod
  def init(self):
    # read data
    pass

  @abstractmethod
  def summary(self):
    pass