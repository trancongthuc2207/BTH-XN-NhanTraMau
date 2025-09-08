from django.db import connections
from IT_Default.utils.sql_server import db_sql_server
from IT_Default.models import *
from general_utils.GetConfig.UtilsConfigSystem import GET_VALUE_ACTION_SYSTEM
# Default Result


class Result:
    data = None
    message = ""
    status = 0

    def __int__(self, data, message, status):
        self.data = data
        self.message = message
        self.status = status


# ---------------------------- #
# ---------------------------- #
# ---------- SELECT ---------- #
# ---------------------------- #
# ---------------------------- #


# get all list
def FPT_count_query_non_offset(sql):
    count = 0
    try:
        __db = db_sql_server.FPT_HIS_PRODUCTION_DBSQLConnection()

        with __db["cursor"] as cursor:
            sql_ = f"""
                SELECT COUNT(*) from ({sql}) all_temp
            """
            cursor.execute(sql_)
            row = cursor.fetchall()

            # print(f"QUERY NO OFFSSET:::: {sql_} \n")

            if row:
                # Process the row data
                count = row[0][0]
            # __db["connection"].close()
            return count
    except Exception as e:
        print(e)
        __db["connection"].close()
        return count

# EXCUTE BY SQL


def EXCUTE_SQL(str_sql="", sort="-ID", page_config=None):
    """
    Execute SQL with sorting + optional pagination.

    :param str_sql: inner SQL (without order/paging)
    :param sort: e.g. "ID", "-ID", or None (no sort)
    :param page_config: dict with {"from": int, "amount": int} or None
    :return: (result object, infor_more)
    """
    result = Result()
    infor_more = {
        "count_all": 0,
        "count_current": 0,
    }

    try:
        __db = db_sql_server.FPT_HIS_PRODUCTION_DBSQLConnection()

        with __db["cursor"] as cursor:
            sql_base = f"({str_sql}) AS TBL"

            # 🔹 Count all rows BEFORE limit/offset
            sql_count = f"SELECT COUNT(1) AS CNT FROM {sql_base}"
            cursor.execute(sql_count)
            infor_more["count_all"] = cursor.fetchone()[0]

            # Sorting (optional)
            if sort:
                order_col = sort.lstrip("-")
                order_dir = "DESC" if sort.startswith("-") else "ASC"
                sql_order = f"ORDER BY {order_col} {order_dir}"
            else:
                sql_order = ""  # no sorting

            # Pagination (optional)
            if page_config:
                sql_offset = f"""
                    OFFSET {page_config["from"]} ROWS
                    FETCH NEXT {page_config["amount"]} ROWS ONLY
                """
            else:
                sql_offset = ""  # no pagination

            # 🔹 Final SQL
            sql_final = f"""
                SELECT * FROM {sql_base}
                {sql_order}
                {sql_offset}
            """
            # print(sql_final)
            cursor.execute(sql_final)

            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

            data = [dict(zip(columns, row)) for row in rows]
            result.data = data
            result.message = (
                "Lấy dữ liệu thành công!"
                if len(data) > 0
                else "Không có dữ liệu nào!"
            )
            infor_more["count_current"] = len(data)
            result.status = 1

    except Exception as e:
        result.message = str(e)
        result.status = 0

    return result, infor_more


# ---------------------------------------------#
# ------------------- UPDATE ------------------#
# ---------------------------------------------#
def EXECUTE_UPDATE(str_sql=""):
    """
    Execute SQL update/insert/delete statement safely.
    Requires WHERE clause for UPDATE/DELETE to avoid full-table operations.

    :param str_sql: SQL statement (UPDATE, INSERT, DELETE, etc.)
    :return: (result object, info)
    """
    result = Result()
    info = {
        "rows_affected": 0,
    }

    try:
        sql_upper = str_sql.strip().upper()

        # 🔹 Require WHERE for UPDATE and DELETE
        if sql_upper.startswith("UPDATE") or sql_upper.startswith("DELETE"):
            if "WHERE" not in sql_upper:
                result.message = "❌ UPDATE/DELETE requires a WHERE clause!"
                result.status = 0
                return result, info

        __db = db_sql_server.FPT_HIS_PRODUCTION_DBSQLConnection()

        with __db["cursor"] as cursor:
            print(f"EXECUTE_UPDATE:: {str_sql}")
            cursor.execute(str_sql)
            __db["connection"].commit()  # ✅ commit transaction
            info["rows_affected"] = cursor.rowcount

            result.message = f"✅ Thực thi thành công ({info['rows_affected']} dòng ảnh hưởng)!"
            result.status = 1

    except Exception as e:
        result.message = str(e)
        result.status = 0

    finally:
        if __db and __db.get("connection"):
            __db["connection"].close()

    return result, info
