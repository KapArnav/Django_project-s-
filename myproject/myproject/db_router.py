class DatabaseRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'flask_data':
            return 'flask_db'  # Read from Flask database
        return 'default'  # Default for other models

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'flask_data':
            return 'flask_db'  # Write to Flask database
        return 'default'  # Default for other models

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'flask_data':
            return db == 'flask_db'
        return db == 'default'
