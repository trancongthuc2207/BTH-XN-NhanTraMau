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
            , pb_nth.TENPHONGBAN as PHONGBAN_THUCHIEN
            , bs_cd.TENNHANVIEN as TEN_BS_CD
            --, dvyc.* 
            from TT_DVYEUCAU dvyc
            left join TM_DICHVU DV on DV.DICHVU_ID = dvyc.DICHVU_ID
            LEFT JOIN TM_NHOMDICHVU NDV ON NDV.NHOMDICHVU_ID = DV.NHOMDICHVU_ID
            LEFT JOIN TM_PHONGBAN pb_nyc ON pb_nyc.PHONGBAN_ID = dvyc.NOIYEUCAU_ID
            LEFT JOIN TM_PHONGBAN pb_nth ON pb_nth.PHONGBAN_ID = dvyc.NOITHUCHIEN_ID
            LEFT JOIN TM_NHANVIEN bs_cd ON bs_cd.NHANVIEN_ID = dvyc.BACSICHIDINH_ID
            LEFT JOIN TT_BENHNHAN bn ON bn.BENHNHAN_ID = dvyc.BENHNHAN_ID
            LEFT JOIN TT_TIEPNHAN tt ON tt.TIEPNHAN_ID = dvyc.TIEPNHAN_ID
                        where 
                        (
                            CAST(bn.MAYTE AS NVARCHAR(50)) = '{{MAYTE}}' or CAST(dvyc.TIEPNHAN_ID AS NVARCHAR(50)) = '{{TIEPNHAN_ID}}'
                            or CAST(tt.SOTIEPNHAN AS NVARCHAR(150)) = '{{SOTIEPNHAN}}'
                        )
            AND lower(pb_nth.TENPHONGBAN) like lower(N'%{{PHONGBAN_THUCHIEN}}%')
            AND lower(pb_nyc.TENPHONGBAN) like lower(N'%{{PHONGBAN_YEUCAU}}%')
            AND lower(dv.TENDICHVU) like lower(N'%{{TENDICHVU}}%')
            AND (CONVERT(DATE, dvyc.NGAYGIOYEUCAU) BETWEEN '{{FROM_DATE}}T00:00:00' AND '{{TO_DATE}}T23:59:59.997')
            and dvyc.DICHVU_ID in (
                SELECT 
                DICHVU_ID
                FROM TM_DICHVU DV
                LEFT JOIN TM_NHOMDICHVU NDV ON NDV.NHOMDICHVU_ID = DV.NHOMDICHVU_ID
                WHERE LEFT(NDV.MANHOMDICHVU, 2) = '01'
                AND DV.MADICHVU NOT LIKE N'%.%'
            )
            and dvyc.DUOCPHEPTHUCHIEN in (0,1)
            """,
                "status": 1,
                "description": "",
                "is_used": "",
                "type_config": "SQL_STATEMENT_CONFIG_XN",
                "description": "SQL Lấy các chỉ định xn theo tiêu chí (sẽ mapping với OBJ_PARAMS_SEARCH_XN_ALL)"
            },
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
                "type_config": "SQL_STATEMENT_CONFIG_XN",
            },
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
                "type_config": "XN_ROLE_NHANMAU_CONFIG",
                "description": "Danh sách code role để đăng nhập vào ghi nhận mẫu"
            },
        )

        config = ConfigApp.objects.get_or_create(
            id=4,
            defaults={
                "name_config": "OBJ_PARAMS_SEARCH_XN_ALL",
                "value": """{
      "MAYTE": "",
      "TIEPNHAN_ID": "",
      "SOTIEPNHAN": "",
      "TENDICHVU": "",
      "PHONGBAN_THUCHIEN": "",
      "PHONGBAN_YEUCAU": "",
      "FROM_DATE": new Date().toISOString().split('T')[0],
      "TO_DATE": new Date().toISOString().split('T')[0],
      "page": "1",
      "limit": "100",
      "ordering": "-NGAYTAO"
    }""",
                "status": 1,
                "description": "",
                "is_used": "",
                "type_config": "XN_FORM_SEARCH_NHANMAU_CONFIG",
                "description": "Danh sách các biến tìm kiếm ở màn hình xn main"
            },
        )

        config = ConfigApp.objects.get_or_create(
            id=5,
            defaults={
                "name_config": "OBJ_PARAMS_SEARCH_MAPPING_LABEL_XN_ALL",
                "value": """{
        "MAYTE": "Mã Y Tế",
        "TIEPNHAN_ID": "Tiếp nhận ID",
        "SOTIEPNHAN": "Số Tiếp Nhận",
        "TENDICHVU": "Tên Dịch Vụ",
        "PHONGBAN_YEUCAU": "Nơi Chỉ Định",
        "PHONGBAN_THUCHIEN": "Nơi Thực Hiện",
        "FROM_DATE": "Ngày chỉ định từ",
        "TO_DATE": "Đến ngày",
        "page": "Trang",
        "limit": "Giới hạn",
        "ordering": "Sắp xếp"
    }""",
                "status": 1,
                "description": "",
                "is_used": "",
                "type_config": "XN_FORM_SEARCH_NHANMAU_CONFIG",
                "description": "Danh sách mapping các biến tìm kiếm và tên ở màn hình xn main"
            },
        )

        config = ConfigApp.objects.get_or_create(
            id=6,
            defaults={
                "name_config": "OBJ_MAPPING_TABLE_COLUMN_XN_ALL",
                "value": """{
        "SOPHIEUYEUCAU": "Số phiếu",
        "MAYTE": "Mã Y Tế",
        "TENBENHNHAN": "Tên Bệnh Nhân",
        "TENDICHVU": "Tên Dịch Vụ",
        "TENNHOMDICHVU": "Nhóm Dịch Vụ",
        "NGAYGIOYEUCAU": "Ngày Giờ Chỉ Định",
        "NGAYDUKIEN_THUCHIEN": "Ngày Giờ Dự Kiến TH",
        "TRANGTHAI": "Trạng Thái",
        "DUOCPHEPTHUCHIEN": "Được Phép Thực Hiện",
        "PHONGBAN_YEUCAU": "Khoa Chỉ Định",
        "PHONGBAN_THUCHIEN": "Khoa Thực Hiện",
        "TEN_BS_CD": "Bác Sĩ Chỉ Định",
        "actions": "Actions"
    }""",
                "status": 1,
                "description": "",
                "is_used": "",
                "type_config": "XN_TABLE_VIEW_NHANMAU_CONFIG",
                "description": "Danh sách tên cột mapping với data trả về (giữ actions, k đc xóa)"
            },
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
                "type_config": "SQL_STATEMENT_CHECK_ACTION_CONFIG_XN",
                "description": "SQL kiểm tra chỉ định có được lấy mẫu hay k (chưa tính điều kiện ở code)"
            },
        )

        config = ConfigApp.objects.get_or_create(
            id=8,
            defaults={
                "name_config": "SQL_CHECK_EDIT_NHANMAU_DVYEUCAU",
                "value": """
                SELECT DISTINCT TOP 1 
                    CASE 
                        WHEN TRANGTHAI IN ('DALAYMAU') AND DUOCPHEPTHUCHIEN = 1 THEN 'TRUE'
                        ELSE 'FALSE'
                    END AS EDIT_CHECK,
                    CASE 
                        WHEN TRANGTHAI IN ('DALAYMAU') AND DUOCPHEPTHUCHIEN = 1 THEN N'Kiểm tra thành công!'
                        WHEN DUOCPHEPTHUCHIEN = 0 THEN N'Dịch vụ chưa được phép thực hiện!'
                        WHEN TRANGTHAI IN ('CHUAKETQUA') AND DUOCPHEPTHUCHIEN = 1 THEN N'Xét nghiệm này chưa được lấy mẫu!' -- CHUAKETQUA
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
                "type_config": "SQL_STATEMENT_CHECK_ACTION_CONFIG_XN",
                "description": "SQL kiểm tra chỉ định có được nhận mẫu hay k (chưa tính điều kiện ở code)"
            },
        )

        config = ConfigApp.objects.get_or_create(
            id=9,
            defaults={
                "name_config": "SQL_UPDATE_TRANGTHAI_DVYEUCAU_XN",
                "value": """
                UPDATE TT_DVYEUCAU
                SET TRANGTHAI = N'{{TRANGTHAI_UPDATED}}' -- CHUAKETQUA or DALAYMAU
                WHERE CAST(DVYEUCAU_ID AS NVARCHAR(50)) = '{{DVYEUCAU_ID}}'
                """,
                "status": 1,
                "description": "",
                "is_used": "",
                "type_config": "SQL_STATEMENT_CHECK_ACTION_CONFIG_XN",
                "description": "SQL cập nhật trạng thái"
            },
        )

        config = ConfigApp.objects.get_or_create(
            id=10,
            defaults={
                "name_config": "OBJ_MAPPING_TABLE_VIEW_DETAIL_COLUMN_XN_ALL",
                "value": """
                {
        "user_infor.first_name": "Tên",
        "type": "Loại Ghi Nhận",
        "user_infor.department_name": "Nhân Viên K/P",
        "created_date": "Ngày Giờ Thực Hiện"
      }
                """,
                "status": 1,
                "description": "",
                "is_used": "",
                "type_config": "XN_TABLE_VIEW_DETAIL_GHINHAN_CONFIG",
                "description": "Đây là danh sách cột mapping để hiện thị chi tiết."
            },
        )

        config = ConfigApp.objects.get_or_create(
            id=11,
            defaults={
                "name_config": "LIST_SORT_FOR_FILTER_XN_ALL",
                "value": """
                [
                { value: '-NGAYTAO', text: 'Thời gian tạo gần đây' },
                { value: 'NGAYTAO', text: 'Thời gian tạo xa nhất' },
                { value: '-NGAYGIOYEUCAU ', text: 'Thời gian chỉ định gần đây' },
                { value: 'NGAYGIOYEUCAU ', text: 'Thời gian chỉ định xa nhất' },
                { value: '-NGAYDUKIEN_THUCHIEN ', text: 'Thời gian dự kiến thực hiện gần đây' },
                { value: 'NGAYDUKIEN_THUCHIEN ', text: 'Thời gian dự kiến thực hiện xa nhất' },
                ]
                """,
                "status": 1,
                "description": "",
                "is_used": "",
                "type_config": "XN_LIST_SORT_CONFIG",
                "description": "Danh sách sắp xếp ở màn hình main ghi nhận xn."
            },
        )

        config = ConfigApp.objects.get_or_create(
            id=12,
            defaults={
                "name_config": "LIST_COLUMN_EXCEPT_OF_CLIENT_XN_ALL",
                "value": """
                ['TRANGTHAI', 'DUOCPHEPTHUCHIEN', 'ANOTHER_KEY']
                """,
                "status": 1,
                "description": "",
                "is_used": "",
                "type_config": "XN_LIST_NOT_SHOW_CONFIG",
                "description": "Đây là danh sách cột được thể hiện ở nhân viên is_staff = 1 và client sẽ không thấy."
            },
        )
        
        config = ConfigApp.objects.get_or_create(
            id=13,
            defaults={
                "name_config": "LIST_CODE_PB_RENDER_BUTTON_THUCHIEN_LAYMAU",
                "value": """
                ['PKTT', 'GPB', 'ANOTHER_KEY']
                """,
                "status": 1,
                "description": "",
                "is_used": "",
                "type_config": "XN_LIST_PB_CONFIG",
                "description": "Đây là danh sách phòng ban được hiện Nút Lấy mẫu"
            },
        )
        
        config = ConfigApp.objects.get_or_create(
            id=14,
            defaults={
                "name_config": "LIST_CODE_PB_RENDER_BUTTON_THUCHIEN_NHANMAU",
                "value": """
                ['PKTT', 'GPB', 'ANOTHER_KEY']
                """,
                "status": 1,
                "description": "",
                "is_used": "",
                "type_config": "XN_LIST_PB_CONFIG",
                "description": "Đây là danh sách phòng ban được hiện Nút Nhận mẫu"
            },
        )
    except Exception as e:
        print(e)
