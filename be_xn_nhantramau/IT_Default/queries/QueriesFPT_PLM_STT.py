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

# ---------------------------------------------#
# ------------- FPT PHÒNG LẤY MẤU -------------#
# ---------------------------------------------#

# ---------------------------------------------#
# Lấy danh sách STT trong phòng lấy mẫu theo điều kiện
# ---------------------------------------------#


def PLM_get_danhsach_stt_by_where(
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


def PLM_get_danhsach_only_stt_by_where(
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
                    QI.ID, QI.PRIORITY, QI.STATE, QI.CREATEDATE, QI.NGAYCAPNHAT, QI.REMARKS
                ) 
            """
            sql_order = f""" 
                order by MAX_KHAN desc,{where["name_sort"]} {where["type_sort"]} 
            """
            sql_offset = f""" 
                OFFSET {page_config["from"]} ROWS 
                FETCH NEXT {page_config["amount"]} ROWS ONLY 
            """

            # print(sql + sql_order + sql_offset)
            cursor.execute(sql + sql_order + sql_offset)
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
# Lấy danh sách chỉ định dịch vụ của bệnh nhân theo mã bệnh nhân và số thứ tự
# ---------------------------------------------#


def PLM_get_danhsach_chidinh_by_stt_mabn_ngay(
    where={
        "SOTHUTU": "",
        "MAYTE": "",
        "CREATEDATE": "",
    },
):
    # -- # RES
    result = Result()
    try:
        # Config
        id_hangdoi_laymau = GET_VALUE_ACTION_SYSTEM("SET_ID_HANGDOI_LAYMAU")
        if id_hangdoi_laymau == None:
            id_hangdoi_laymau = f"AND QI.QUEUE_ID = 149"
        else:
            id_hangdoi_laymau = f"AND QI.QUEUE_ID in ({id_hangdoi_laymau})"

        __db = db_sql_server.FPT_HIS_PRODUCTION_DBSQLConnection()

        with __db["cursor"] as cursor:
            sql = f"""
                ( 
                SELECT DISTINCT
                    bn.MAYTE,
                    bn.TENBENHNHAN,
                    bn.NAMSINH,
                    bn.NGAYSINH AS TUOI,              
                    bn.DIACHILIENLAC AS DIACHI,
                    bn.GIOITINH,
                    GD.DESCRIPTION AS TENGIOITINH,              
                    ISNULL(dv.NGAYTAO, dv.NGAYCAPNHAT) AS THOIGIANDKDICHVU,
                    dv.TRANGTHAI AS TRANGTHAICODE,
                    A.TENDICHVU,
                    --nth.TENPHONGBAN AS NOITHUCHIEN,
                    nyc.TENPHONGBAN AS TENKHOACHIDINH, 
                    ISNULL(qi.DISPLAYTEXT, dv.SOTHUTU) AS SOTHUTU,
                    dv.KHAN
                FROM TT_DVYEUCAU dv
                    LEFT JOIN dbo.TT_DVYEUCAU_MASTER AS DV_MASTER
                        ON DV_MASTER.DVYC_MASTER_ID = dv.DVYC_MASTER_ID
                    INNER JOIN TT_TIEPNHAN tn
                        ON dv.TIEPNHAN_ID = tn.TIEPNHAN_ID
                    INNER JOIN TT_BENHNHAN bn
                        ON tn.BENHNHAN_ID = bn.BENHNHAN_ID
                    INNER JOIN dbo.QMS_QUEUE_ITEM QI 
                        ON bn.MAYTE = QI.PATIENTCODE
                    INNER JOIN TM_DICHVU A
                        ON A.DICHVU_ID = dv.DICHVU_ID
                    INNER JOIN TM_PHONGBAN nth
                        ON nth.PHONGBAN_ID = dv.NOITHUCHIEN_ID
                    LEFT JOIN TM_BENHVIEN ngt
                        ON ngt.BENHVIEN_STT_ID = dv.DONVIGIOITHIEU_ID
                    LEFT JOIN TM_NHANVIEN bscd
                        ON bscd.NHANVIEN_ID = dv.BACSICHIDINH_ID
                    LEFT JOIN TM_NHANVIEN ngtt
                        ON ngtt.NHANVIEN_ID = dv.NGUOIGIOITHIEU_ID
                    INNER JOIN TM_PHONGBAN nyc
                        ON nyc.PHONGBAN_ID = dv.NOIYEUCAU_ID
                    INNER JOIN TM_NHOMDICHVU B
                        ON B.NHOMDICHVU_ID = A.NHOMDICHVU_ID
            
                    INNER JOIN TM_GENDER GD
                        ON GD.ID = bn.GIOITINH

        
                    LEFT JOIN TT_KSK_HOPDONG_BENHNHAN_DICHVU hddv
                        ON dv.DVYEUCAU_ID = hddv.DVYEUCAU_ID
                        AND ISNULL(hddv.LYDOKHOA, '') = ''
                    
                WHERE dv.DICHVU_ID IS NOT NULL
                    AND (CONVERT(DATE, tn.NGAYTIEPNHAN) BETWEEN '{where['CREATEDATE']}T00:00:00' AND '{where['CREATEDATE']}T23:59:59.997')
                    AND (CONVERT(DATE, QI.CREATEDATE) BETWEEN '{where['CREATEDATE']}T00:00:00' AND '{where['CREATEDATE']}T23:59:59.997')
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
                    AND dv.TRANGTHAI IN ('CHUAKETQUA')
                    AND LEFT(B.MANHOMDICHVU, 2) = '01'
                    AND tn.TRANGTHAI IN ( 'DATIEPNHAN', 'NOITRU', 'CAPCUU', 'NGOAITRU', 'HOANTHANH' )
                    --
                    AND bn.MAYTE = '{where["MAYTE"]}'
                    AND ISNULL(qi.DISPLAYTEXT, dv.SOTHUTU) like '{where["SOTHUTU"]}%'
                    AND qi.DISPLAYTEXT = dv.SOTHUTU
                    {id_hangdoi_laymau}
                ) 
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

            result.data = rs
            result.message = (
                "Lấy dữ liệu thành công!"
                if len(result.data) > 0
                else "Không có dữ liệu nào!"
            )
            result.status = 1
            return result
    except Exception as e:
        print(f"PLM_get_danhsach_stt_by_where:: {e}")
        result.data = []
        result.message = e
        result.status = 0
        return result

# ---------------------------------------------#
# Lấy số thứ tự tiếp theo trong phòng lấy mẫu
# ---------------------------------------------#


def PLM_get_number_next_stt_uutien():
    # -- # RES
    result = Result()
    try:
        # Config
        id_hangdoi_laymau = GET_VALUE_ACTION_SYSTEM("SET_ID_HANGDOI_LAYMAU")
        if id_hangdoi_laymau == None:
            id_hangdoi_laymau = f"AND QI.QUEUE_ID = 149"
        else:
            id_hangdoi_laymau = f"AND QI.QUEUE_ID in ({id_hangdoi_laymau})"

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
                    
                WHERE dv.DICHVU_ID IS NOT NULL
                    AND (CONVERT(DATE, tn.NGAYTIEPNHAN) = CONVERT(DATE, GETDATE()))
                    AND CONVERT(DATE, QI.CREATEDATE) = CONVERT(DATE, GETDATE())
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
                    --AND dv.TRANGTHAI IN ('CHUAKETQUA')
                    AND LEFT(B.MANHOMDICHVU, 2) = '01'
                    AND tn.TRANGTHAI IN ( 'DATIEPNHAN', 'NOITRU', 'CAPCUU', 'NGOAITRU', 'HOANTHANH' )
                    -- 
					AND STATE != 3 AND STATE != 100
                    AND STATE != 0 AND STATE != 4 AND STATE != 2
                    {id_hangdoi_laymau}
                GROUP BY 
                    bn.MAYTE, bn.TENBENHNHAN, bn.NAMSINH, bn.NGAYSINH,
                    bn.DIACHILIENLAC, bn.GIOITINH, GD.DESCRIPTION,
                    ISNULL(qi.DISPLAYTEXT, dv.SOTHUTU),
                    QI.ID, QI.PRIORITY, QI.STATE, QI.CREATEDATE, QI.NGAYCAPNHAT, QI.REMARKS
                )
                ORDER BY MAX_KHAN desc, UUTIEN DESC, SOTHUTU
                OFFSET 0 ROWS
                FETCH NEXT 1 ROWS ONLY 
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

            result.data = rs
            result.message = (
                "Lấy dữ liệu thành công!"
                if len(result.data) > 0
                else "Không có dữ liệu nào!"
            )
            result.status = 1
            return result
    except Exception as e:
        print(f"PLM_get_number_next_stt:: {e}")
        result.data = []
        result.message = e
        result.status = 0
        return result


def PLM_get_number_next_stt_normal():
    # -- # RES
    result = Result()
    try:
        # Config
        id_hangdoi_laymau = GET_VALUE_ACTION_SYSTEM("SET_ID_HANGDOI_LAYMAU")
        if id_hangdoi_laymau == None:
            id_hangdoi_laymau = f"AND QI.QUEUE_ID = 149"
        else:
            id_hangdoi_laymau = f"AND QI.QUEUE_ID in ({id_hangdoi_laymau})"

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
                    
                WHERE dv.DICHVU_ID IS NOT NULL
                    AND (CONVERT(DATE, tn.NGAYTIEPNHAN) = CONVERT(DATE, GETDATE()))
                    AND CONVERT(DATE, QI.CREATEDATE) = CONVERT(DATE, GETDATE())
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
                    --AND dv.TRANGTHAI IN ('CHUAKETQUA')
                    AND LEFT(B.MANHOMDICHVU, 2) = '01'
                    AND tn.TRANGTHAI IN ( 'DATIEPNHAN', 'NOITRU', 'CAPCUU', 'NGOAITRU', 'HOANTHANH' )
                    -- 
					AND STATE != 3 AND STATE != 100
                    AND STATE != 0 AND STATE != 4 AND STATE != 2
                    AND QI.PRIORITY = 0
                    {id_hangdoi_laymau}
                GROUP BY 
                    bn.MAYTE, bn.TENBENHNHAN, bn.NAMSINH, bn.NGAYSINH,
                    bn.DIACHILIENLAC, bn.GIOITINH, GD.DESCRIPTION,
                    ISNULL(qi.DISPLAYTEXT, dv.SOTHUTU),
                    QI.ID, QI.PRIORITY, QI.STATE, QI.CREATEDATE, QI.NGAYCAPNHAT, QI.REMARKS
                )
                ORDER BY MAX_KHAN desc, UUTIEN DESC, SOTHUTU
                OFFSET 0 ROWS
                FETCH NEXT 1 ROWS ONLY 
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

            result.data = rs
            result.message = (
                "Lấy dữ liệu thành công!"
                if len(result.data) > 0
                else "Không có dữ liệu nào!"
            )
            result.status = 1
            return result
    except Exception as e:
        print(f"PLM_get_number_next_stt:: {e}")
        result.data = []
        result.message = e
        result.status = 0
        return result

# ---------------------------------------------#
# Kiểm tra số thứ đã gọi hay chưa
# ---------------------------------------------#


def PLM_check_number_next_stt_dangcho_by_id_qi(idqi):
    # -- # RES
    result = Result()
    try:
        __db = db_sql_server.FPT_HIS_PRODUCTION_DBSQLConnection()

        with __db["cursor"] as cursor:
            sql = f"""
                select ID, STATE from [QMS_QUEUE_ITEM]
                where ID in ({idqi}) and STATE=1
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

            result.data = rs
            result.message = (
                "Lấy dữ liệu thành công!"
                if len(result.data) > 0
                else "Không có dữ liệu nào!"
            )
            result.status = 1
            return result
    except Exception as e:
        print(f"PLM_check_number_next_stt_dangcho_by_id_qi:: {e}")
        result.data = []
        result.message = e
        result.status = 0
        return result

# ---------------------------------------------#
# Cập nhật Gọi STT
# ---------------------------------------------#


def PLM_update_call_stt_by_qi_id(idqi, quaygoi):
    # -- # RES
    result = Result()
    try:
        __db = db_sql_server.FPT_HIS_PRODUCTION_DBSQLConnection()

        with __db["cursor"] as cursor:
            sql = f"""
                UPDATE [QMS_QUEUE_ITEM] 
                SET STATE = ?, 
                NGAYCAPNHAT = GETDATE(),
                REMARKS = ?
                where ID=? and STATE=1
            """

            # Execute the query with parameterized values
            cursor.execute(
                sql,
                [
                    2,  # Assuming 2 is the state for "called"
                    quaygoi,
                    idqi
                ],
            )

            __db["connection"].commit()

            # Flatten list values and add "inserted": True
            flattened_data = {"is_updated": True}

            # Optionally fetch the inserted ID or confirmation
            result.data = flattened_data
            result.message = "Cập nhật dữ liệu thành công!"
            result.status = 1
            return result

    except Exception as e:
        print(f"Error during insertion: {e}")
        if __db and __db.get("connection"):
            __db["connection"].rollback()
        result.data = []
        result.message = f"Lỗi khi thêm dữ liệu: {e}"
        result.status = 0
        return result

    finally:
        if __db and __db.get("connection"):
            __db["connection"].close()


# ---------------------------------------------#
# Cập nhật Gọi STT
# ---------------------------------------------#
def PLM_get_ds_hangdoi_lm(sl=8):
    # -- # RES
    result = Result()
    try:
        # Config
        id_hangdoi_laymau = GET_VALUE_ACTION_SYSTEM("SET_ID_HANGDOI_LAYMAU")
        if id_hangdoi_laymau == None:
            id_hangdoi_laymau = f"AND QI.QUEUE_ID = 149"
        else:
            id_hangdoi_laymau = f"AND QI.QUEUE_ID in ({id_hangdoi_laymau})"

        __db = db_sql_server.FPT_HIS_PRODUCTION_DBSQLConnection()

        with __db["cursor"] as cursor:
            sql = f"""
                ( 
                SELECT DISTINCT
                    bn.MAYTE,
                    bn.TENBENHNHAN,
                    bn.NAMSINH,
                    bn.NGAYSINH AS TUOI,              
                    bn.DIACHILIENLAC AS DIACHI,
                    bn.GIOITINH,
                    GD.DESCRIPTION AS TENGIOITINH,              
                    --ISNULL(dv.NGAYTAO, dv.NGAYCAPNHAT) AS THOIGIANDKDICHVU,
                    dv.TRANGTHAI AS TRANGTHAICODE,
                    --A.TENDICHVU,
                    --nth.TENPHONGBAN AS NOITHUCHIEN,
                    nyc.TENPHONGBAN AS TENKHOACHIDINH, 
                    ISNULL(qi.DISPLAYTEXT, dv.SOTHUTU) AS SOTHUTU,
                    ---
                    QI.ID as QI_ID,
                    QI.PRIORITY UUTIEN,
                    QI.STATE,
                    QI.CREATEDATE NGAYCAPSTT,
                    QI.NGAYCAPNHAT NGAYGOISST,
                    QI.REMARKS
                FROM TT_DVYEUCAU dv
                    LEFT JOIN dbo.TT_DVYEUCAU_MASTER AS DV_MASTER
                        ON DV_MASTER.DVYC_MASTER_ID = dv.DVYC_MASTER_ID
                    INNER JOIN TT_TIEPNHAN tn
                        ON dv.TIEPNHAN_ID = tn.TIEPNHAN_ID
                    INNER JOIN TT_BENHNHAN bn
                        ON tn.BENHNHAN_ID = bn.BENHNHAN_ID
                    INNER JOIN dbo.QMS_QUEUE_ITEM QI 
                        ON bn.MAYTE = QI.PATIENTCODE
                    INNER JOIN TM_DICHVU A
                        ON A.DICHVU_ID = dv.DICHVU_ID
                    INNER JOIN TM_PHONGBAN nth
                        ON nth.PHONGBAN_ID = dv.NOITHUCHIEN_ID
                    LEFT JOIN TM_BENHVIEN ngt
                        ON ngt.BENHVIEN_STT_ID = dv.DONVIGIOITHIEU_ID
                    LEFT JOIN TM_NHANVIEN bscd
                        ON bscd.NHANVIEN_ID = dv.BACSICHIDINH_ID
                    LEFT JOIN TM_NHANVIEN ngtt
                        ON ngtt.NHANVIEN_ID = dv.NGUOIGIOITHIEU_ID
                    INNER JOIN TM_PHONGBAN nyc
                        ON nyc.PHONGBAN_ID = dv.NOIYEUCAU_ID
                    INNER JOIN TM_NHOMDICHVU B
                        ON B.NHOMDICHVU_ID = A.NHOMDICHVU_ID
            
                    INNER JOIN TM_GENDER GD
                        ON GD.ID = bn.GIOITINH

        
                    LEFT JOIN TT_KSK_HOPDONG_BENHNHAN_DICHVU hddv
                        ON dv.DVYEUCAU_ID = hddv.DVYEUCAU_ID
                        AND ISNULL(hddv.LYDOKHOA, '') = ''
                    
                WHERE dv.DICHVU_ID IS NOT NULL
                    AND CONVERT(DATE, QI.CREATEDATE) = CONVERT(DATE, GETDATE())
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
                    AND dv.TRANGTHAI IN ('CHUAKETQUA')
                    AND LEFT(B.MANHOMDICHVU, 2) = '01'
                    AND tn.TRANGTHAI IN ( 'DATIEPNHAN', 'NOITRU', 'CAPCUU', 'NGOAITRU', 'HOANTHANH' )
                    -- 
					AND STATE = 2
                    {id_hangdoi_laymau}
                )
                ORDER BY NGAYGOISST DESC
                OFFSET 0 ROWS
                FETCH NEXT {sl} ROWS ONLY 
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

            result.data = rs
            result.message = (
                "Lấy dữ liệu thành công!"
                if len(result.data) > 0
                else "Không có dữ liệu nào!"
            )
            result.status = 1
            return result
    except Exception as e:
        print(f"PLM_get_number_next_stt:: {e}")
        result.data = []
        result.message = e
        result.status = 0
        return result
