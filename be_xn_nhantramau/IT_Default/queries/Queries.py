from django.db import connections
from ..serializers import *
from .db_tables.db_tables import *
from datetime import datetime
import xml.etree.ElementTree as ET
import os


# Default Result

class Result:
    data = None
    message = ''
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

# Danh sách khoa phòng -- nkdg
def get_danhsach_khoaphong_nk(where={}, page_config={}):
    result = Result()
    # -- where
    # Lấy đối tượng
    # sodong = where.get('sodong') or ''

    try:
        with connections['mq'].cursor() as cursor:
            sql = f"""
            SELECT kp.makp, kp.tenkp 
            FROM btdkp_bv kp 
            WHERE kp.makp in (034,035,032,041,033,038,030,013) 
            ORDER BY kp.tenkp
            """
            # print(sql)

            cursor.execute(sql)
            # Name column
            columns = [col[0] for col in cursor.description]
            row = cursor.fetchall()

            # List column name + value ---> { id : ...}
            rs = []
            for r in row:
                row_dict = dict(zip(columns, r))
                rs.append(row_dict)

            # Result
            if len(row) > 0:
                # Process the row data
                result.data = rs
                result.message = 'Get Success'
                result.status = 1
            else:
                result.data = []
                result.message = 'Không có dữ liệu nào!'
                result.status = 1
            connections['mq'].close()

    except Exception as e:
        print(e)
        connections['mq'].close()
        result.data = []
        result.message = e
        result.status = 0

    return result



