# README #


## web service
#### app.py  
    RestAPI資料夾的api主體  
#### app_redfish.py  
    產生另一份符合redfish規範的api，它會呼叫app.py裡面的api後，把值依redfish規範回傳給前端  


## 環境變數 ##
請先設定.env檔的環境變數
```ini
ITG_REST_HOST=192.168.3.137:5001
```