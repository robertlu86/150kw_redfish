# README #

Test Case說明  

## test_chassis_router.py
### Test Case: PATCH設定值
測試設定Fan, Pump, OperationMode的值是否正確運作  
    test_chassis_FansSpeedControl_patch_api  
        Endpoint: /redfish/v1/Chassis/{chassis_id}/Controls/FansSpeedControl  
        Cases:  
            Manual模式下:  
                1) 速度設為50，風扇全設為ON，則reading值應接近設定值。  
                2) 速度設15-60隨機挑選，`Fan[1-6]` 隨機設為ON。  
                3) 同上。  
                4) 速度設為50，個別測`Fan[1-6]`，則單一風扇的reading值應接近設定值，其他Fan的reading值應為0。  
                ( 以上請見 `test_chassis_FansSpeedControl_patch_api` )  
            Auto模式下: PLC會去追冷卻液的目標溫度，API這邊無控制權，只能設定標溫度後，看風扇是否有運轉。  
                1) 設定目標溫度，看風扇是否有運轉。  
    test_chassis_PumpsSpeedControl_patch_api  
        Endpoint: /redfish/v1/Chassis/{chassis_id}/Controls/PumpsSpeedControl    
        Cases:  
            Manual模式下:  
                同Fan  
                ( 以上請見 `test_chassis_PumpsSpeedControl_patch_api` )  
            Auto模式下:   
                1) 有3個pump，每次只會開2個pump，另一個pump的轉速應為0。(程式不好測，只能先用Manual模式全開，再設至Auto模式觀察)  
                ( 以上請見 `test_chassis_AutoMode_patch_api` )  
    test_chassis_OperationMode_patch_api  
        Endpoint: /redfish/v1/Chassis/{chassis_id}/Controls/OperationMode    

Test Command:
```bash
cd /home/user/service/redfish-server/sidecar-redfish

# activate venv
source /home/user/service/redfish-server/redfish_venv/bin/activate

# run test
## test all
pytest -v --html=/tmp/report.html --self-contained-html test/
## test normal api
pytest --html=/tmp/report.html --self-contained-html test/test_chassis_router.py::test_chassis_normal_api
## test patch api (測PATCH -> GET -> Wait for sensor value)
pytest --html=/tmp/report.html --self-contained-html test/test_chassis_router.py::test_chassis_FansSpeedControl_patch_api
pytest --html=/tmp/report.html --self-contained-html test/test_chassis_router.py::test_chassis_FansSpeedControl_patch_api[testcase0] # 只跑第0個case
pytest --html=/tmp/report.html --self-contained-html test/test_chassis_router.py::test_chassis_PumpsSpeedControl_patch_api
pytest --html=/tmp/report.html --self-contained-html test/test_chassis_router.py::test_chassis_OperationMode_patch_api
## test sensor reading value (單純測fan的sensor值是否為目標值附近)
pytest --html=/tmp/report.html --self-contained-html test/test_chassis_router.py::test_fan_sensors_should_be_corrected
## test Auto mode
pytest --html=/tmp/report.html --self-contained-html test/test_chassis_router.py::test_chassis_AutoMode_patch_api

```

### Test Case: reading值
測試sensor reading值(Fan, Pump)是否正確運作  
    test_fan_sensors_should_be_corrected  
        Endpoint: /redfish/v1/Chassis/{chassis_id}/Sensors/Fan{sn}  
    test_pump_sensors_should_be_corrected (尚未實作) 
        Endpoint: /redfish/v1/Chassis/{chassis_id}/Sensors/Pump{sn}  

### Test Case: Normal 
測試redfish必要欄位是否正常  
    test_chassis_normal_api  
        Endpoint: ...  


