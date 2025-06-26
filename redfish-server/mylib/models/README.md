# README #

因為多人開發的關係，這個資料夾有orm model和pydantic model，請注意! 

## Redfish Model

請注意!  
redfish model的命名方式是 rf_xxx_model.py  
使用python pydantic來定義model  

### Model定義方式(以PowerSupply為例)
schema文件：https://redfish.dmtf.org/schemas/v1/PowerSupply.v1_6_0.json  
在`properties`可找到定義的欄位  

#### 欄位：InputNominalVoltageType
```json
"InputNominalVoltageType": {
    "anyOf": [
        {
            "$ref": "http://redfish.dmtf.org/schemas/v1/Circuit.json#/definitions/NominalVoltageType"
        },
        {
            "type": "null"
        }
    ],
    "description": "The nominal voltage ...",
    "longDescription": "This property shall ...",
    "readonly": true
},
```
沒定義type資訊，則進一步看`anyOf`資訊  
anyOf看到`$ref`外部引用  
因為階層是`v1/Circuit.json`，屬schema第一層，所以需新增`rf_circuit_model.py`檔，對齊Redfish Schema規範  
(別因為`PowerSupply`需要`NominalVoltageType`就把`NominalVoltageType`定義在`PowerSupply`裡)  
NominalVoltageType定義在`rf_circuit_model.py`裡，是一個Enum  
Circuit與NomiaVoltageType定義如下：  
```python
class RfNominalVoltageType(str, Enum):
    """
    @see https://redfish.dmtf.org/schemas/v1/Circuit.json#/definitions/NominalVoltageType
    """
    AC100To127V = "AC100To127V"
    AC100To240V = "AC100To240V"
    AC100To277V = "AC100To277V"
    #...(略)

class RfCircuitModel(BaseModel):
    #...(略)
```
(註) redfish的model統一`Rf`開頭  
(註) 正常的model統一`Model`結尾，Enum的不用Model結尾  


#### 欄位：Assembly
```json
"Assembly": {
    "$ref": "http://redfish.dmtf.org/schemas/v1/Assembly.json#/definitions/Assembly",
    "description": "The link ...",
    "longDescription": "This property ...",
    "readonly": true
}
```
直接看到`$ref`外部引用，因為階層是`v1/Assembly.json`，屬schema第一層  
所以需新增`rf_assembly_model.py`檔，對齊Redfish Schema規範  
一路追查$ref，最終定義在 https://redfish.dmtf.org/schemas/v1/Assembly.v1_5_1.json#/definitions/Assembly  
欄位在AssemblyData.properties裡  





## ORM Model

orm model的命名方式是 {TABLE_NAME}.py，請注意! 
ex:  
- account.py : 代表table <accounts>  
- role.py : 代表table <roles>  



## Sensor Log Model
定義不同客戶的sensor log model  
並使用SensorLogModelFactory來產生model  



## 請AI幫忙產生model
#### Prompt範例
[prompt]

這是redfish scehma使用pydantic寫成的model
```python
class RfPowerSupplyModel(RfResourceBaseModel):
  """
  @see https://redfish.dmtf.org/schemas/v1/PowerSupply.v1_6_0.json
  @note properties 38 items
  """
  MinVersion: Optional[str] = Field(default=None)
  Assembly: Optional[RfAssemblyModel] = Field(default=None)
  # Certificates: RfCertificateCollection
  FirmwareVersion: Optional[str] = Field(default=None)
  HotPluggable: Optional[bool] = Field(default=None)
  InputNominalVoltageType: Optional[RfNominalVoltageType] = Field(default=None)
  LineInputStatus: Optional[RfLineStatus] = Field(default=None)
  Manufacturer: Optional[str] = Field(default=None)
  # Metrics: RfPowerSupplyMetricsModel
  Name: Optional[str] = Field(default=None)
  PartNumber: Optional[str] = Field(default=None)
  PowerCapacityWatts: Optional[float] = Field(default=None, extra={"unit": "W"})
  PowerSupplyType: Optional[RfPowerSupplyType] = Field(default=None)
  SerialNumber: Optional[str] = Field(default=None)
  Status: Optional[RfStatusModel] = Field(default=None)
```
請參考上方格式
閱讀下方網址
https://redfish.dmtf.org/schemas/v1/MetricDefinition.v1_0_0.json
找到 definitions.MetricDefinitions.properties 處
把欄位也寫成pydantic格式
順序不要改，以便我核對
例如:第一個是 "@odata.context"，在pydantic就是第一個欄位。因為這個欄位名稱無法被json使用，所以在pydantic改用alias呈現
例如:第五個是 "Accuracy"，在pydantic就是第5個欄位, 官方定義type是number，對照python則是float。
如果是Enum格式，則另外定義class RfXXX(str, enum), enum值則至 definition.XXX的enum裡找值。

[/prompt]
(註) 丟給Claude效果較好  