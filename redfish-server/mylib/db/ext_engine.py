from flask_sqlalchemy import SQLAlchemy


class ExtEngine():
    """
    A class to manage the SQLAlchemy instance and its application context.
    """
    def __init__(self):
        self.db = SQLAlchemy()
        self.db_app = None
        
    def init_db(self, app):
        self.db.init_app(app)
        self.db_app = app

    def get_app(self):
        if self.db_app is None:
            raise Exception("Database app not initialized.")
        return self.db_app
    
    def get_db(self):
        return self.db