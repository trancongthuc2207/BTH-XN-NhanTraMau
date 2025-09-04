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
            name_config="SQL_DS_DVYC_ALL",
            value="""
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
            TIEPNHAN_ID = {{TIEPNHAN_ID}}
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
            status=1,
            description="",
            is_used="",
            type_config="SQL_STATEMENT_CONFIG_XN"
        )
        
        config = ConfigApp.objects.get_or_create(
            id=2,
            name_config="SQL_DS_SOBENHAN",
            value="""
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
            TIEPNHAN_ID = {{TIEPNHAN_ID}}
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
            status=1,
            description="",
            is_used="",
            type_config="SQL_STATEMENT_CONFIG_XN"
        )
        # =========================== SQL =========================== #
        
    except Exception as e:
        print(e)
