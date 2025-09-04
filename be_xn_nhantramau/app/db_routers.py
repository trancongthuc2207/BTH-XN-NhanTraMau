class AppDatabaseRouter:
    """
    A router to control database operations for each app.

    DEFAULT IS ::: MYSQL

    """

    def db_for_read(self, model, **hints):
        """
        Returns the database to use for read operations.
        """

        # print(f'ROUTES DB::::: {model._meta.app_label}')
        if model._meta.app_label in ["IT_Default", "IT_FilesManager", "general_utils", "IT_MailManager", "IT_SOCKET_SYS"]:
            return "default"
        if model._meta.app_label in ["IT_OAUTH"]:
            return "oauth"
        # Add more app-to-database mappings as needed
        return None

    def db_for_write(self, model, **hints):
        """
        Returns the database to use for write operations.
        """
        # print(f'ROUTES DB::::: {model._meta.app_label}')
        if model._meta.app_label in ["IT_Default", "IT_FilesManager", "general_utils", "IT_MailManager", "IT_SOCKET_SYS"]:
            return "default"
        if model._meta.app_label in ["IT_OAUTH"]:
            return "oauth"
        # Add more app-to-database mappings as needed
        return None

    # def allow_relation(self, obj1, obj2, **hints):
    #     """
    #     Allow relations between objects in different databases.
    #     """
    #     if obj1._meta.app_label == 'myapp1' or obj2._meta.app_label == 'myapp1':
    #         return True  # Allow relations if involving 'myapp1'
    #     elif obj1._meta.app_label == 'myapp2' or obj2._meta.app_label == 'myapp2':
    #         return True  # Allow relations if involving 'myapp2'
    #     # Add more app-specific relations as needed
    #     return None
    def allow_relation(self, obj1, obj2, **hints):
        return True  # Default behavior

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Allow migrations for specific apps and databases.
        """
        if app_label in ["IT_Default", "IT_FilesManager", "general_utils", "IT_MailManager", "IT_SOCKET_SYS"]:
            return db == "default"
        if app_label in ["IT_OAUTH"]:
            return db == "oauth"
        # Add more app-to-database migration rules as needed
        return None
