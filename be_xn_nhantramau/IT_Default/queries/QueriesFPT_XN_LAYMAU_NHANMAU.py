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
    Execute SQL with sorting + pagination.

    :param str_sql: inner SQL (without order/paging)
    :param sort: e.g. "ID" or "-ID"
    :param page_config: dict with {"from": int, "amount": int}
    :return: (result object, infor_more)
    """
    result = Result()
    infor_more = {
        "count_all": 0,
        "count_current": 0,
    }

    if page_config is None:
        page_config = {"from": 0, "amount": 150}

    try:
        __db = db_sql_server.FPT_HIS_PRODUCTION_DBSQLConnection()

        with __db["cursor"] as cursor:
            sql_base = f"({str_sql}) AS TBL"

            # 🔹 Count all rows BEFORE limit/offset
            sql_count = f"SELECT COUNT(1) AS CNT FROM {sql_base}"
            cursor.execute(sql_count)
            infor_more["count_all"] = cursor.fetchone()[0]

            # Sorting
            order_col = sort.lstrip("-")
            order_dir = "DESC" if sort.startswith("-") else "ASC"
            sql_order = f"ORDER BY {order_col} {order_dir}"

            # Pagination
            sql_offset = f"""
                OFFSET {page_config["from"]} ROWS
                FETCH NEXT {page_config["amount"]} ROWS ONLY
            """

            # 🔹 Final SQL with ORDER + LIMIT
            sql_final = f"""
                SELECT * FROM {sql_base}
                {sql_order}
                {sql_offset}
            """

            cursor.execute(sql_final)
            # print(sql_final)
            
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

    except Exception as e:
        result.message = str(e)
        result.status = 0

    return result, infor_more


# ---------------------------------------------#
# ------------- FPT PHÒNG LẤY MẤU -------------#
# ---------------------------------------------#

# ---------------------------------------------#
# Lấy danh sách STT trong phòng lấy mẫu theo điều kiện
# ---------------------------------------------#


def PLM_get_danhsach_xn_by_where(
    where={
        "date_from": "",
        "date_to": "",
        "STATE": "",
        "MAYTE": "",
        "TENBN": "",
        "SOTHUTU": "",
        "REMARKS": "",
        "UUTIEN": "",
        #
        "name_sort": "",
        "type_sort": "",
    },
    page_config={"from": "", "amount": ""},
):
    # -- # RES
    result = Result()
    infor_more = {
        "count_all": 0,
        "count_current": 0,
    }
    try:
        # Config
        id_hangdoi_laymau = GET_VALUE_ACTION_SYSTEM("SET_ID_HANGDOI_LAYMAU")
        if id_hangdoi_laymau == None:
            id_hangdoi_laymau = f"AND QI.QUEUE_ID = 149"
        else:
            id_hangdoi_laymau = f"AND QI.QUEUE_ID in ({id_hangdoi_laymau})"

        uutien_sql = ""
        if where["UUTIEN"] != "":
            if where["UUTIEN"] == "1":
                uutien_sql = ""
            elif where["UUTIEN"] == "0":
                uutien_sql = "AND QI.PRIORITY = 0"

        trangthai_sql = ""
        if where["TRANGTHAI"] != "":
            status_list = [
                f"'{v.strip()}'" for v in where["TRANGTHAI"].split(",") if v.strip()]
            trangthai_sql = f"AND dv.TRANGTHAI IN ({', '.join(status_list)})"

        __db = db_sql_server.FPT_HIS_PRODUCTION_DBSQLConnection()

        with __db["cursor"] as cursor:
            sql = f"""
                (
                SELECT 
                    bn.MAYTE,
                    bn.TENBENHNHAN,
                    bn.NAMSINH,
                    bn.NGAYSINH AS TUOI,
                    bn.DIACHILIENLAC AS DIACHI,
                    bn.GIOITINH,
                    GD.DESCRIPTION AS TENGIOITINH,
                    ISNULL(qi.DISPLAYTEXT, dv.SOTHUTU) AS SOTHUTU,
                    ca.TENKHOACHIDINH,   -- Lấy từ CROSS APPLY
                    QI.ID as QI_ID,
                    QI.PRIORITY UUTIEN,
                    QI.STATE,
                    QI.CREATEDATE NGAYCAPSTT,
                    QI.NGAYCAPNHAT NGAYGOISST,
                    QI.REMARKS,
                    MAX(dv.KHAN) AS MAX_KHAN
                FROM TT_DVYEUCAU dv
                    INNER JOIN TT_TIEPNHAN tn ON dv.TIEPNHAN_ID = tn.TIEPNHAN_ID
                    INNER JOIN TT_BENHNHAN bn ON tn.BENHNHAN_ID = bn.BENHNHAN_ID
                    INNER JOIN dbo.QMS_QUEUE_ITEM QI ON bn.MAYTE = QI.PATIENTCODE
                    INNER JOIN TM_DICHVU A ON A.DICHVU_ID = dv.DICHVU_ID
                    INNER JOIN TM_PHONGBAN nth ON nth.PHONGBAN_ID = dv.NOITHUCHIEN_ID
                    INNER JOIN TM_PHONGBAN nyc ON nyc.PHONGBAN_ID = dv.NOIYEUCAU_ID
                    INNER JOIN TM_NHOMDICHVU B ON B.NHOMDICHVU_ID = A.NHOMDICHVU_ID
                    INNER JOIN TM_GENDER GD ON GD.ID = bn.GIOITINH
                    LEFT JOIN dbo.TT_DVYEUCAU_MASTER DV_MASTER ON DV_MASTER.DVYC_MASTER_ID = dv.DVYC_MASTER_ID
                    LEFT JOIN TM_BENHVIEN ngt ON ngt.BENHVIEN_STT_ID = dv.DONVIGIOITHIEU_ID
                    LEFT JOIN TM_NHANVIEN bscd ON bscd.NHANVIEN_ID = dv.BACSICHIDINH_ID
                    LEFT JOIN TM_NHANVIEN ngtt ON ngtt.NHANVIEN_ID = dv.NGUOIGIOITHIEU_ID
                    LEFT JOIN TT_KSK_HOPDONG_BENHNHAN_DICHVU hddv 
                        ON dv.DVYEUCAU_ID = hddv.DVYEUCAU_ID
                        AND ISNULL(hddv.LYDOKHOA, '') = ''
                    CROSS APPLY (
                        SELECT STRING_AGG(x.TENPHONGBAN, ' | ') 
                                WITHIN GROUP (ORDER BY x.TENPHONGBAN) AS TENKHOACHIDINH
                        FROM (
                            SELECT DISTINCT nyc2.TENPHONGBAN
                            FROM TT_DVYEUCAU dv2
                            INNER JOIN TM_PHONGBAN nyc2 ON nyc2.PHONGBAN_ID = dv2.NOIYEUCAU_ID
                            WHERE dv2.TIEPNHAN_ID = dv.TIEPNHAN_ID
                        ) x
                    ) ca
                WHERE dv.DICHVU_ID IS NOT NULL
                    AND (CONVERT(DATE, tn.NGAYTIEPNHAN) BETWEEN '{where['date_from']}T00:00:00' AND '{where['date_to']}T23:59:59.997')
                    AND (CONVERT(DATE, QI.CREATEDATE) BETWEEN '{where['date_from']}T00:00:00' AND '{where['date_to']}T23:59:59.997')
                    AND HUYYEUCAU = 0
                    AND dv.NGAYHENCLS IS NULL
                    AND (CASE
                            WHEN hddv.HOPDONG_DICHVU_BENHNHAN_ID IS NOT NULL THEN
                                ISNULL(hddv.HUY, 0)
                            ELSE
                                0
                        END != 1
                        )
                    AND ISNULL(dv.DUOCPHEPTHUCHIEN, 0) = 1 -- dv đó chưa đóng viện phí
                    {trangthai_sql}
                    AND LEFT(B.MANHOMDICHVU, 2) = '01'
                    AND tn.TRANGTHAI IN ( 'DATIEPNHAN', 'NOITRU', 'CAPCUU', 'NGOAITRU', 'HOANTHANH' )
                    --
                    AND QI.STATE IN ({where['STATE']})
                    AND bn.MAYTE like '%{where["MAYTE"]}%'
                    AND LOWER(bn.TENBENHNHAN) like (N'%{where["TENBENHNHAN"]}%')
                    AND ISNULL(qi.DISPLAYTEXT, dv.SOTHUTU) like (N'%{where["SOTHUTU"]}%')
                    AND (LOWER(QI.REMARKS) like (N'%{where["REMARKS"]}%') or QI.REMARKS is null)
                    {id_hangdoi_laymau}
                    {uutien_sql}
                GROUP BY 
                    bn.MAYTE, bn.TENBENHNHAN, bn.NAMSINH, bn.NGAYSINH,
                    bn.DIACHILIENLAC, bn.GIOITINH, GD.DESCRIPTION,
                    ISNULL(qi.DISPLAYTEXT, dv.SOTHUTU),
                    QI.ID, QI.PRIORITY, QI.STATE, QI.CREATEDATE, QI.NGAYCAPNHAT, QI.REMARKS, ca.TENKHOACHIDINH
                ) 
            """
            sql_order = f""" 
                order by {where["name_sort"]} {where["type_sort"]} 
            """
            sql_offset = f""" 
                OFFSET {page_config["from"]} ROWS 
                FETCH NEXT {page_config["amount"]} ROWS ONLY 
            """

            # print(sql + sql_order + sql_offset)
            cursor.execute(sql + sql_order + sql_offset)
            # print(f"PLM_get_danhsach_stt_by_where:: {sql + sql_order + sql_offset}")
            # Name column
            columns = [col[0] for col in cursor.description]
            row = cursor.fetchall()

            # List column name + value ---> { id : ...}
            rs = []
            for r in row:
                row_dict = dict(zip(columns, r))
                rs.append(row_dict)

            # Set Infor More
            sl = FPT_count_query_non_offset(sql)
            infor_more["count_all"] = sl
            infor_more["count_current"] = len(rs)

            result.data = {"infor_more": infor_more, "data": rs}
            result.message = (
                "Lấy dữ liệu thành công!"
                if len(result.data["data"]) > 0
                else "Không có dữ liệu nào!"
            )
            result.status = 1
            return result
    except Exception as e:
        print(f"PLM_get_danhsach_stt_by_where:: {e}")
        result.data = {"infor_more": infor_more, "data": []}
        result.message = e
        result.status = 0
        return result


# ---------------------------------------------#
# Lấy danh sách dịch vụ yêu cầu theo điều kiện
# ---------------------------------------------#
def PLM_get_danhsach_xn_dvyc_by_where(
    where={
        "date_from": "",
        "date_to": "",
        "STATE": "",
        "MAYTE": "",
        "TENBN": "",
        "SOTHUTU": "",
        "REMARKS": "",
        "UUTIEN": "",
        #
        "name_sort": "",
        "type_sort": "",
    },
    page_config={"from": "", "amount": ""},
):
    # -- # RES
    result = Result()
    infor_more = {
        "count_all": 0,
        "count_current": 0,
    }
    try:
        # Config
        id_hangdoi_laymau = GET_VALUE_ACTION_SYSTEM("SET_ID_HANGDOI_LAYMAU")
        if id_hangdoi_laymau == None:
            id_hangdoi_laymau = f"AND QI.QUEUE_ID = 149"
        else:
            id_hangdoi_laymau = f"AND QI.QUEUE_ID in ({id_hangdoi_laymau})"

        uutien_sql = ""
        if where["UUTIEN"] != "":
            if where["UUTIEN"] == "1":
                uutien_sql = ""
            elif where["UUTIEN"] == "0":
                uutien_sql = "AND QI.PRIORITY = 0"

        trangthai_sql = ""
        if where["TRANGTHAI"] != "":
            status_list = [
                f"'{v.strip()}'" for v in where["TRANGTHAI"].split(",") if v.strip()]
            trangthai_sql = f"AND dv.TRANGTHAI IN ({', '.join(status_list)})"

        __db = db_sql_server.FPT_HIS_PRODUCTION_DBSQLConnection()

        with __db["cursor"] as cursor:
            sql = f"""
                (
                select 
                dvyc.DVYEUCAU_ID
                , dvyc.TIEPNHAN_ID
                , dvyc.BENHAN_ID
                , dvyc.LUUTRU_ID
                , dvyc.BENHNHAN_ID
                , dvyc.DICHVU_ID
                , dvyc.NOIYEUCAU_ID
                , dvyc.NGUOICHIDINH_ID
                , dvyc.BACSICHIDINH_ID
                , dvyc.NOITHUCHIEN_ID
                , dvyc.SOPHIEUYEUCAU
                , dv.TENDICHVU
                , NDV.MANHOMDICHVU
                , NDV.TENNHOMDICHVU
                , dvyc.NGAYGIOYEUCAU
                , dvyc.NGAYTAO
                , dvyc.NGAYDUKIEN_THUCHIEN
                , dvyc.TRANGTHAI
                --, dvyc.* 
                from TT_DVYEUCAU dvyc
                left join TM_DICHVU DV on DV.DICHVU_ID = dvyc.DICHVU_ID
                LEFT JOIN TM_NHOMDICHVU NDV ON NDV.NHOMDICHVU_ID = DV.NHOMDICHVU_ID
                where 
                TIEPNHAN_ID = 18643
                and dvyc.DICHVU_ID in (
                    SELECT 
                    DICHVU_ID
                    FROM TM_DICHVU DV
                    LEFT JOIN TM_NHOMDICHVU NDV ON NDV.NHOMDICHVU_ID = DV.NHOMDICHVU_ID
                    WHERE LEFT(NDV.MANHOMDICHVU, 2) = '01'
                    AND DV.MADICHVU NOT LIKE N'%.%'
                )
                and dvyc.DUOCPHEPTHUCHIEN = 1
                ) 
            """
            sql_order = f""" 
                order by dvyc.DVYEUCAU_ID asc 
            """
            sql_offset = f""" 
                OFFSET {page_config["from"]} ROWS 
                FETCH NEXT {page_config["amount"]} ROWS ONLY 
            """

            # print(sql + sql_order + sql_offset)
            cursor.execute(sql + sql_order + sql_offset)
            # print(f"PLM_get_danhsach_stt_by_where:: {sql + sql_order + sql_offset}")
            # Name column
            columns = [col[0] for col in cursor.description]
            row = cursor.fetchall()

            # List column name + value ---> { id : ...}
            rs = []
            for r in row:
                row_dict = dict(zip(columns, r))
                rs.append(row_dict)

            # Set Infor More
            sl = FPT_count_query_non_offset(sql)
            infor_more["count_all"] = sl
            infor_more["count_current"] = len(rs)

            result.data = {"infor_more": infor_more, "data": rs}
            result.message = (
                "Lấy dữ liệu thành công!"
                if len(result.data["data"]) > 0
                else "Không có dữ liệu nào!"
            )
            result.status = 1
            return result
    except Exception as e:
        print(f"PLM_get_danhsach_stt_by_where:: {e}")
        result.data = {"infor_more": infor_more, "data": []}
        result.message = e
        result.status = 0
        return result
