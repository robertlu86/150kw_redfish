from mylib.models.account_model import RoleModel, AccountModel
from mylib.models.setting_model import SettingModel



def init_orm(app, db):
    """
    Initialize the ORM models and create the database tables if they don't exist.
    
    Args:
        app: The Flask application instance.
        db: The SQLAlchemy instance.
    """
    def ensure_setting(key, value):
        setting = SettingModel.query.filter_by(key=key).first()
        if not setting:
            setting = SettingModel(key=key, value=value)
            db.session.add(setting)
            db.session.commit()
        return setting
 
    with app.app_context():
        # @see https://flask-sqlalchemy.readthedocs.io/en/stable/queries/
        db.create_all()
        # Create default roles
        if not RoleModel.query.first():  # Check if any role exists
            admin_privi = ["Login",
                           "ConfigureManager",
                           "ConfigureUsers",
                           "ConfigureSelf",
                           "ConfigureComponents",
                           ]
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
            admin_user = AccountModel(user_name='admin', role = admin_role, password='Supermicro')
            #admin_user.role = admin_role
            db.session.add(admin_user)
            db.session.commit()

        # Create default setting
        #AccountService DSP0246
        ensure_setting(key='AccountService.AuthFailureLoggingThreshold', value='3')
        ensure_setting(key='AccountService.MinPasswordLength', value='5')
        ensure_setting(key='AccountService.AccountLockoutThreshold', value='5')
        ensure_setting(key='AccountService.AccountLockoutDuration', value='30')
        ensure_setting(key='AccountService.AccountLockoutCounterResetAfter', value='30')
        ensure_setting(key='SessionService.SessionTimeout', value='3600')
