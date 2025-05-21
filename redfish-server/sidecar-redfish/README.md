# sidecar-redfish

Implement sidecar Redfish API  


## Startup Service
Enter your python virtual environment and run
```bash
cd ${PROJECT_ROOT}
# for dev
python app.py --env=dev
# for prod
python app.py --env=prod
```


## Directory Structure  
```
{project_name}/
|--mylib/
   |--common/      # 放置共用常數、定義…
   |--routers/     # 放置blueprint
      |--accountservice_router.py # redfish AccountService api
      |--sessionservice_router.py # redfish SessionService api
      |--device_router.py         # redfish Device api (ITG提供)
   |--services/    # Logic Layer
   |--auth/
      |--TokenProvider.py (ITG提供)
   |--managements/
      |--FlaskSessionManager.py (ITG提供)
   |--models/      # Model Layer
      |--account_model.py
      |--role_model.py
   |--utils/  
|--app.py          # Flask main app
|--requirements.txt
|--.env   
```

## Other Documents
* [AccountService,SessionService planning document](https://docs.google.com/document/d/102J-SfI7yyY3LnNWWcaKx2A0af6lKepY4VmaWh-lwR8/edit?tab=t.0)  




## Testing ##
Use pytest framework to test    

#### Install
```
pip install pytest
pip install pytest-html
```
#### Run
Beforehand: Enter your python virtual environment
```bash
cd ${PROJECT_ROOT}
# Run whole test cases
pytest
pytest -v
pytest -v test/
pytest -v test/ --html=/tmp/report.html # generate html report after test
# or Run specific test cases
pytest -v test/test_root_router.py
```
Or use VSCode by `.vscode/launch.json`
```json
{
  "version": "0.2.0",
  "configurations": [
    {
        "name": "Python: pytest",
        "type": "python",
        "request": "launch",
        "module": "pytest",
        "args": [
            "test/", 
            "--html=/tmp/report.html"
        ],
        "justMyCode": false,
    }
  ]
}
```



## flask-sqlalchemy example ##

#### Install dependencies
```bash
pip install Flask-SQLAlchemy
```

#### How to use
1. Define your model inherit from `MyOrmBaseModel`  
```python
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from mylib.models.my_orm_base_model import MyOrmBaseModel

@dataclass
class ExampleModel(MyOrmBaseModel):
    # Define table name
    __tablename__ = 'examples'
    # Define columns
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(32))
```

2. Add `@dataclass` decorator to your model  
```python
from dataclasses import dataclass
@dataclass
class ExampleModel(MyOrmBaseModel):
    # **Note** You must add data type hint for dataclass
    # {COLUMN_NAME}: Mapped[{DATA_TYPE}] = mapped_column({DATA_TYPE})
    pass
```

3. Initialize db  
```python
from flask import Flask, jsonify
from mylib.db.extensions import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/user/storage/examples.db'
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 5,
    'max_overflow': 1,
    'pool_timeout': 10,
}
db.init_app(app)
```

4. Use model  
```python
from mylib.models.example_model import ExampleModel

@app.route('/examples')
def examples():
    examples = ExampleModel.all()
    return jsonify({
        "examples": examples
    })
```
Response:  
```json
{
  "examples": [
    {
      "id": 1,
      "title": "this is a example title 1"
    },
    {
      "id": 2,
      "title": "this is a example title 2"
    }
  ]
}
```
