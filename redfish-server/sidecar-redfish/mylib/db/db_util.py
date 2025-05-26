from mylib.models.account_model import RoleModel, AccountModel
from mylib.models.setting_model import SettingModel

def init_orm(app, db):
    """
    Initialize the ORM models and create the database tables if they don't exist.
    
    Args:
        app: The Flask application instance.
        db: The SQLAlchemy instance.
    """
    with app.app_context():
        print("#################################################################")
        print("# app_context")
        print("#################################################################")
        # @see https://flask-sqlalchemy.readthedocs.io/en/stable/queries/
        db.drop_all()
        db.create_all()
        # Create default roles
        if not RoleModel.query.first():  # Check if any role exists
            admin_privi = ["Login",
                           "ConfigureManager",
                           "ConfigureUsers",
                           "ConfigureSelf",
                           "ConfigureComponents",
                           "ConfigureSelf"]
            operator_privi = ["Login",
                              "ConfigureComponents",
                              "ConfigureSelf"
                              ]
            readonly_privi = ["Login",
                              "ConfigureSelf"
                              ]
            admin_role = RoleModel(name='Administrator', assigned_privileges=",".join(admin_privi))
            
            operator_role = RoleModel(name='Operator', assigned_privileges=",".join(operator_privi))
            readonly_role = RoleModel(name='ReadOnly', assigned_privileges=",".join(readonly_privi))
            db.session.add(admin_role)
            db.session.add(operator_role)
            db.session.add(readonly_role)
            db.session.commit()

        # Create default user
        if not AccountModel.query.first():  # Check if any user exists
            admin_user = AccountModel(user_name='admin', role = admin_role, password='admin')
            #admin_user.role = admin_role
            db.session.add(admin_user)
            db.session.commit()

        if not SettingModel.query.first():
            setting = SettingModel(key='SessionService.SessionTimeout', value='3600')
            db.session.add(setting)
            db.session.commit()

       
           

