from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from django.apps import apps
from .models import *


@receiver(post_migrate)
def sync_new_app(sender, **kwargs):
    try:
        # Dictionary
        list_dict = [
            # FileInformation Dictionary
            Dictionary(key="FILE_TIEU_DE", value="Tên tiêu đề",
                       description="Tiêu đề", type="DICTIONARY_FILE_INFOR"),
            Dictionary(key="FILE_TOM_TAT", value="Tóm tắt",
                       description="Tóm tắt", type="DICTIONARY_FILE_INFOR"),
            Dictionary(key="FILE_SO_KY_HIEU", value="Số ký hiệu",
                       description="Danh mục loại thông tin", type="DICTIONARY_FILE_INFOR"),
            Dictionary(key="FILE_SO_BAN_HANH", value="Số ban hành",
                       description="Danh mục loại thông tin", type="DICTIONARY_FILE_INFOR"),
            Dictionary(key="FILE_NGAY_BAN_HANH", value="Ngày ban hành",
                       description="Danh mục loại thông tin", type="DICTIONARY_FILE_INFOR"),
            Dictionary(key="FILE_NGAY_HIEU_LUC", value="Ngày hiệu lực",
                       description="Danh mục loại thông tin", type="DICTIONARY_FILE_INFOR"),
            Dictionary(key="FILE_NGAY_HET_HIEU_LUC", value="Ngày hết hiệu lực",
                       description="Danh mục loại thông tin", type="DICTIONARY_FILE_INFOR"),
            Dictionary(key="FILE_NGAY_TAO", value="Ngày tạo",
                       description="Danh mục loại thông tin", type="DICTIONARY_FILE_INFOR"),
            Dictionary(key="FILE_SO_LUONG_XEM", value="Số lượng xem",
                       description="Tổng số lượng xem", type="DICTIONARY_FILE_INFOR"),
            Dictionary(key="FILE_SO_LUONG_TAI_XUONG", value="Số lượng tải xuống",
                       description="Tổng số lần được tải xuống", type="DICTIONARY_FILE_INFOR"),
            Dictionary(key="FILE_NGON_NGU", value="Ngôn ngữ",
                       description="Ngôn ngữ file", type="DICTIONARY_FILE_INFOR"),
            Dictionary(key="FILE_TAG", value="Tag",
                       description="Tag file", type="DICTIONARY_FILE_INFOR"),
            Dictionary(key="FILE_LIEN_QUAN", value="Liên quan",
                       description="Liên quan", type="DICTIONARY_FILE_INFOR"),
            # Thông tin người dùng
            Dictionary(key="FILE_ID_NGUOI_DUYET", value="Id người duyệt",
                       description="Id người duyệt", type="DICTIONARY_FILE_INFOR"),
            Dictionary(key="FILE_TEN_NGUOI_DUYET", value="Tên người duyệt",
                       description="Tên người duyệt", type="DICTIONARY_FILE_INFOR"),
            Dictionary(key="FILE_ID_NGUOI_TAO", value="Id người tạo",
                       description="Id người tạo", type="DICTIONARY_FILE_INFOR"),
            Dictionary(key="FILE_TEN_NGUOI_TAO", value="Tên người tạo",
                       description="Tên người tạo", type="DICTIONARY_FILE_INFOR"),
            Dictionary(key="FILE_ID_NGUOI_CAP_NHAT", value="Id người cập nhật",
                       description="Id người cập nhật", type="DICTIONARY_FILE_INFOR"),
            Dictionary(key="FILE_TEN_NGUOI_CAP_NHAT", value="Tên người cập nhật",
                       description="Tên người cập nhật", type="DICTIONARY_FILE_INFOR"),
            Dictionary(key="FILE_ID_NGUOI_DUYET_CAP_NHAT", value="Id người duyệt cập nhật",
                       description="Id người duyệt cập nhật", type="DICTIONARY_FILE_INFOR"),
            Dictionary(key="FILE_TEN_NGUOI_DUYET_CAP_NHAT", value="Tên người duyệt cập nhật",
                       description="Tên người duyệt cập nhật", type="DICTIONARY_FILE_INFOR"),
            Dictionary(key="FILE_ID_NGUOI_DUYET_CHINH", value="Id người duyệt chính",
                       description="Id người duyệt chính", type="DICTIONARY_FILE_INFOR"),
            Dictionary(key="FILE_TEN_NGUOI_DUYET_CHINH", value="Tên người duyệt chính",
                       description="Tên người duyệt chính", type="DICTIONARY_FILE_INFOR"),
            # Thông tin thêm
            Dictionary(key="FILE_TAC_GIA", value="Tác giả",
                       description="Tác giả của file", type="DICTIONARY_FILE_INFOR"),

        ]
        for dict_item in list_dict:
            if not Dictionary.objects.filter(key=dict_item.key).exists():
                dict_item.save()

        # Category file
        list_category = [
            FileCategory(name="Văn bản bệnh viện", code="VBBV",
                         description="All types of documents", key_category="VBBV"),
            FileCategory(name="Hệ thống quản lý chất lượng", code="HTQLCL",
                         description="All types of documents", key_category="HTQLCL"),
            FileCategory(name="Văn bản pháp luật", code="VBPL",
                         description="All types of documents", key_category="VBPL"),
            FileCategory(name="Nghiên cứu khoa học", code="NCKH",
                         description="All types of documents", key_category="NCKH"),
            FileCategory(name="Thư viện", code="TV",
                         description="All types of documents", key_category="TV"),
        ]
        for category in list_category:
            if not FileCategory.objects.filter(name=category.name).exists():
                category.save()

        # List Config System
        list_types = [
            FileType(name="Image", extension="jpg", description="Image files"),
            FileType(name="Document", extension="pdf",
                     description="PDF documents"),
            FileType(name="Audio", extension="mp3", description="Audio files"),
            FileType(name="Video", extension="mp4", description="Video files"),
            FileType(name="Archive", extension="zip",
                     description="Compressed files"),
        ]
        for file_type in list_types:
            if not FileType.objects.filter(name=file_type.name).exists():
                file_type.save()

    except Exception as e:
        print(e)
