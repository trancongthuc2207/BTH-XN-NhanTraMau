from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from django.apps import apps
from .models import *


@receiver(post_migrate)
def sync_new_app(sender, **kwargs):
    try:
        print("")
        # Config SYS App

        # =========================== SQL =========================== #
        config = ConfigApp.objects.get_or_create(
            id=1,
            defaults={
                "name_config": "SQL_DS_DVYC_ALL",
                "value": """
            select 
            dvyc.DVYEUCAU_ID
            , dvyc.TIEPNHAN_ID
            , dvyc.BENHAN_ID
            , dvyc.LUUTRU_ID
            , dvyc.BENHNHAN_ID
            , bn.MAYTE
            , bn.TENBENHNHAN
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
            , dvyc.DUOCPHEPTHUCHIEN
            , pb_nyc.TENPHONGBAN as PHONGBAN_YEUCAU
            , bs_cd.TENNHANVIEN as TEN_BS_CD
            --, dvyc.* 
            from TT_DVYEUCAU dvyc
            left join TM_DICHVU DV on DV.DICHVU_ID = dvyc.DICHVU_ID
            LEFT JOIN TM_NHOMDICHVU NDV ON NDV.NHOMDICHVU_ID = DV.NHOMDICHVU_ID
            LEFT JOIN TM_PHONGBAN pb_nyc ON pb_nyc.PHONGBAN_ID = dvyc.NOIYEUCAU_ID
            LEFT JOIN TM_NHANVIEN bs_cd ON bs_cd.NHANVIEN_ID = dvyc.BACSICHIDINH_ID
            LEFT JOIN TT_BENHNHAN bn ON bn.BENHNHAN_ID = dvyc.BENHNHAN_ID
                        where 
                        (CAST(bn.MAYTE AS NVARCHAR(50)) = '{{MAYTE}}' or CAST(dvyc.TIEPNHAN_ID AS NVARCHAR(50)) = '{{TIEPNHAN_ID}}')
            AND (CONVERT(DATE, dvyc.NGAYGIOYEUCAU) BETWEEN '{{FROM_DATE}}T00:00:00' AND '{{TO_DATE}}T23:59:59.997')
            and dvyc.DICHVU_ID in (
                SELECT 
                DICHVU_ID
                FROM TM_DICHVU DV
                LEFT JOIN TM_NHOMDICHVU NDV ON NDV.NHOMDICHVU_ID = DV.NHOMDICHVU_ID
                WHERE LEFT(NDV.MANHOMDICHVU, 2) = '01'
                AND DV.MADICHVU NOT LIKE N'%.%'
            )
            and dvyc.DUOCPHEPTHUCHIEN = 1
            """,
                "status": 1,
                "description": "",
                "is_used": "",
                "type_config": "SQL_STATEMENT_CONFIG_XN"
            }
        )

        config = ConfigApp.objects.get_or_create(
            id=2,
            defaults={
                "name_config": "SQL_DS_SOBENHAN",
                "value": """
            select 
            dvyc.DVYEUCAU_ID
            , dvyc.TIEPNHAN_ID
            , dvyc.BENHAN_ID
            , dvyc.LUUTRU_ID
            , dvyc.BENHNHAN_ID
            , bn.MAYTE
            , bn.TENBENHNHAN
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
            , dvyc.DUOCPHEPTHUCHIEN
            , pb_nyc.TENPHONGBAN as PHONGBAN_YEUCAU
            , bs_cd.TENNHANVIEN as TEN_BS_CD
            --, dvyc.* 
            from TT_DVYEUCAU dvyc
            left join TM_DICHVU DV on DV.DICHVU_ID = dvyc.DICHVU_ID
            LEFT JOIN TM_NHOMDICHVU NDV ON NDV.NHOMDICHVU_ID = DV.NHOMDICHVU_ID
            LEFT JOIN TM_PHONGBAN pb_nyc ON pb_nyc.PHONGBAN_ID = dvyc.NOIYEUCAU_ID
            LEFT JOIN TM_NHANVIEN bs_cd ON bs_cd.NHANVIEN_ID = dvyc.BACSICHIDINH_ID
            LEFT JOIN TT_BENHNHAN bn ON bn.BENHNHAN_ID = dvyc.BENHNHAN_ID
                        where 
                        (CAST(bn.MAYTE AS NVARCHAR(50)) = '{{MAYTE}}' or CAST(dvyc.TIEPNHAN_ID AS NVARCHAR(50)) = '{{TIEPNHAN_ID}})')
            AND (CONVERT(DATE, dvyc.NGAYGIOYEUCAU) BETWEEN '{{FROM_DATE}}T00:00:00' AND '{{TO_DATE}}T23:59:59.997')
            and dvyc.DICHVU_ID in (
                SELECT 
                DICHVU_ID
                FROM TM_DICHVU DV
                LEFT JOIN TM_NHOMDICHVU NDV ON NDV.NHOMDICHVU_ID = DV.NHOMDICHVU_ID
                WHERE LEFT(NDV.MANHOMDICHVU, 2) = '01'
                AND DV.MADICHVU NOT LIKE N'%.%'
            )
            and dvyc.DUOCPHEPTHUCHIEN = 1
            """,
                "status": 1,
                "description": "",
                "is_used": "",
                "type_config": "SQL_STATEMENT_CONFIG_XN"
            }
        )
        # =========================== SQL =========================== #
        config = ConfigApp.objects.get_or_create(
            id=3,
            defaults={
                "name_config": "LIST_ROLE_FOR_XN_NHAN_MAU",
                "value": """["NV_THUTHUAT","NV_GPB"]""",
                "status": 1,
                "description": "",
                "is_used": "",
                "type_config": "XN_ROLE_NHANMAU_CONFIG"
            }

        )

        config = ConfigApp.objects.get_or_create(
            id=4,
            defaults={
                "name_config": "OBJ_PARAMS_SEARCH_XN_ALL",
                "value": """{
      "MAYTE": "",
      "TIEPNHAN_ID": "",
      "FROM_DATE": new Date().toISOString().split('T')[0],
      "TO_DATE": new Date().toISOString().split('T')[0],
      "page": "1",
      "limit": "100",
      "ordering": "-NGAYTAO"
    }""",
                "status": 1,
                "description": "",
                "is_used": "",
                "type_config": "XN_FORM_SEARCH_NHANMAU_CONFIG"
            }

        )

        config = ConfigApp.objects.get_or_create(
            id=5,
            defaults={
                "name_config": "OBJ_PARAMS_SEARCH_MAPPING_LABEL_XN_ALL",
                "value": """{
        "MAYTE": "Mã Y Tế",
        "TIEPNHAN_ID": "TIEPNHAN ID",
        "FROM_DATE": "From Date",
        "TO_DATE": "To Date",
        "page": "Page",
        "limit": "Limit",
        "ordering": "Ordering"
    }""",
                "status": 1,
                "description": "",
                "is_used": "",
                "type_config": "XN_FORM_SEARCH_NHANMAU_CONFIG"
            }
        )

        config = ConfigApp.objects.get_or_create(
            id=6,
            defaults={
                "name_config": "OBJ_MAPPING_TABLE_COLUMN_XN_ALL",
                "value": """{
        "SOPHIEUYEUCAU": "Request No.",
        "TENDICHVU": "Service Name",
        "TENNHOMDICHVU": "Service Group",
        "NGAYGIOYEUCAU": "Request Date",
        "TRANGTHAI": "Status",
        "PHONGBAN_YEUCAU": "Request Dept.",
        "TEN_BS_CD": "Ordering Doctor",
        "TENNHOMDICHVU": "Tên nhóm dịch vụ",
        "actions": "Actions"
    }""",
                "status": 1,
                "description": "",
                "is_used": "",
                "type_config": "XN_TABLE_VIEW_NHANMAU_CONFIG"
            }
        )
        
        # =========================== SQL CHECK ACTION XN =========================== #
        config = ConfigApp.objects.get_or_create(
            id=7,
            defaults={
                "name_config": "SQL_CHECK_EDIT_DVYEUCAU",
                "value": """
                SELECT DISTINCT TOP 1 
                    CASE 
                        WHEN TRANGTHAI IN ('CHUAKETQUA') AND DUOCPHEPTHUCHIEN = 1 THEN 'TRUE'
                        ELSE 'FALSE'
                    END AS EDIT_CHECK,
                    CASE 
                        WHEN TRANGTHAI IN ('CHUAKETQUA') AND DUOCPHEPTHUCHIEN = 1 THEN N'Kiểm tra thành công!'
                        WHEN DUOCPHEPTHUCHIEN = 0 THEN N'Dịch vụ chưa được phép thực hiện!'
                        WHEN TRANGTHAI IN ('DALAYMAU') AND DUOCPHEPTHUCHIEN = 1 THEN N'Xét nghiệm này đã được lấy mẫu!'
                        WHEN TRANGTHAI IN ('CHOXEM') AND DUOCPHEPTHUCHIEN = 1 THEN N'Xét nghiệm này đang chờ xem kết quả!'
                        WHEN TRANGTHAI IN ('HOANTAT') AND DUOCPHEPTHUCHIEN = 1 THEN N'Xét nghiệm này đã hoàn tất!'
                        ELSE 'FALSE'
                    END AS MESSAGE_CHECK,
                    DVYEUCAU_ID,
                    TRANGTHAI,
                    DUOCPHEPTHUCHIEN
                    --, *
                FROM TT_DVYEUCAU
                WHERE 
                CAST(DVYEUCAU_ID AS NVARCHAR(50)) = '{{DVYEUCAU_ID}}' 
                """,
                "status": 1,
                "description": "",
                "is_used": "",
                "type_config": "SQL_STATEMENT_CHECK_ACTION_CONFIG_XN"
            }
        )
    except Exception as e:
        print(e)
