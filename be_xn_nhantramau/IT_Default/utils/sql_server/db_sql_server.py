import pyodbc
from django.conf import settings

connection_string_fpt_his_production = settings.CONFIG.CONNECTION_STRING_HIS_PRODUCTION_FPT_MSSQL


def FPT_HIS_PRODUCTION_DBSQLConnection():
    # Establish the connection
    try:
        connection = pyodbc.connect(connection_string_fpt_his_production)
        # print("TD Connection successful!")
    except Exception as e:
        print("Error: ", e)
        exit()

    # Create a cursor object
    cursor = connection.cursor()

    config = {"cursor": cursor, "connection": connection}

    return config
