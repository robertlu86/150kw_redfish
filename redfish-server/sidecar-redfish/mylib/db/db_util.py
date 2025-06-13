from werkzeug.security import generate_password_hash
from mylib.models.account_model import RoleModel, AccountModel
from mylib.models.setting_model import SettingModel
import sqlalchemy as sa


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
        elif setting.value != str(value):
            setting.value = str(value)
            db.session.commit()
        return setting
 
    def key_ensure_setting(key, value):
        setting = SettingModel.query.filter_by(key=key).first()
        if not setting:
            setting = SettingModel(key=key, value=value)
            db.session.add(setting)
            db.session.commit()
        return setting

    def check_db_schema_changes(db):
        """Check if database schema has changed and needs migration"""
        try:
            current_metadata = sa.MetaData()
            current_metadata.reflect(bind=db.engine)
            expected_metadata = db.metadata
            for table_name in expected_metadata.tables:
                if table_name not in current_metadata.tables:
                    return True
                current_table = current_metadata.tables[table_name]
                expected_table = expected_metadata.tables[table_name]
                current_columns = set(c.name for c in current_table.columns)
                expected_columns = set(c.name for c in expected_table.columns)
                if current_columns != expected_columns:
                    return True
            return False
        except Exception as e:
            return False
    try:
        with app.app_context():
            # @see https://flask-sqlalchemy.readthedocs.io/en/stable/queries/
            # Recreate database if schema has changed
            if check_db_schema_changes(db):
                print(" * Database schema has changed. Recreating tables...")
                db.drop_all()
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
                noaccess_role = RoleModel(name='NoAccess', assigned_privileges="")
                db.session.add(admin_role)
                db.session.add(operator_role)
                db.session.add(readonly_role)
                db.session.add(noaccess_role)
                db.session.commit()

            # Create default users
            admin_role = RoleModel.query.filter_by(name='Administrator').first()
            if not admin_role:
                raise Exception("Administrator role not found. Please ensure roles are created before users.")
            if not AccountModel.query.filter_by(user_name='user').first():  # Check if user with name "user" exists
                user_user = AccountModel(user_name='user', role = admin_role, password="scrypt:32768:8:1$RU6pVamEtGMXCkfY$823baa550bb7bf3bf0267e05758f6228c6d3409ebcb196b0f43130b4a0b5532e370ed5e8d773e64f066753760cfcd185796c56848c5068f3f010db692bb3f03b")
                db.session.add(user_user)
                db.session.commit()
            if not AccountModel.query.filter_by(user_name='admin').first():  # Check if user with name "admin" exists
                admin_user = AccountModel(user_name='admin', role= admin_role, password="scrypt:32768:8:1$Stw1tEtDXmDfvpOd$99b39e2d6fde2a2c6b07527563a41f073330e6e913f92fad2b87ad5393a735e2607df8f362bbf33db00ebcb2c5e964168dd449b2f6eb6c2ba2aa338745198a1d")
                db.session.add(admin_user)
                db.session.commit()

            # Create default setting
            #AccountService DSP0246
            ensure_setting(key='AccountService.MaxAllowedAccounts', value='15')
            key_ensure_setting(key='AccountService.AuthFailureLoggingThreshold', value='3')
            key_ensure_setting(key='AccountService.MinPasswordLength', value='5')
            key_ensure_setting(key='AccountService.MaxPasswordLength', value='25')
            key_ensure_setting(key='AccountService.AccountLockoutThreshold', value='3')
            key_ensure_setting(key='AccountService.AccountLockoutDuration', value='60')
            key_ensure_setting(key='AccountService.AccountLockoutCounterResetAfter', value='30')
            key_ensure_setting(key='SessionService.SessionTimeout', value='360')
    except Exception as e:
            print(f" * Error occurred: {e}")
    return
