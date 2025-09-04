from rest_framework import serializers
from .models import *
from .queries.db_tables.db_tables import *
from django.conf import settings

baseUrl = settings.HOST + "static/"


##################################################################################################################

# --------- NHAPKHOA --------- #
## SHOW
class NhapKhoaBaseShow(serializers.Serializer):
    # Class attribute
    ID = serializers.CharField(max_length=256)
    MABN = serializers.CharField(max_length=256)
    HOTEN = serializers.CharField(max_length=256)
    NGAYSINH = serializers.CharField(max_length=256)
    NAMSINH = serializers.CharField(max_length=256)
    PHAI = serializers.IntegerField()
    MAQL = serializers.CharField(max_length=256)
    MAKP = serializers.CharField(max_length=256)
    NGAY = serializers.DateTimeField()
    KHOACHUYEN = serializers.CharField(max_length=256)
    CHANDOAN = serializers.CharField(max_length=256)
    MAICD = serializers.CharField(max_length=256)

    def to_representation(self, instance):
        # Serialize a single CustomClass instance
        # print(instance[0])
        return {
            'ID': instance[0],
            'MABN': instance[1],
            'HOTEN': instance[2],
            'NGAYSINH': instance[3],
            'NAMSINH': instance[4],
            'PHAI': instance[5],
            'MAQL': instance[6],
            'MAKP': instance[7],
            'NGAY': instance[8],
            'KHOACHUYEN': instance[9],
            'CHANDOAN': instance[10],
            'MAICD': instance[11],
        }

    def to_internal_value(self, data):
        # Deserialize data into a single CustomClass instance
        return NhapKhoa(**data)


class NhapKhoaListBaseShow(serializers.ListSerializer):
    child = NhapKhoaBaseShow()

    def to_representation(self, data):
        # Serialize a list of CustomClass instances
        return [self.child.to_representation(item) for item in data]

    def to_internal_value(self, data):
        # Deserialize a list of data into a list of CustomClass instances
        return [self.child.to_internal_value(item) for item in data]

