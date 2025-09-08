from rest_framework import serializers
from .models import *
from .queries.db_tables.db_tables import *
from django.conf import settings
from general_utils.utils import *
from IT_OAUTH.serializers import UserBaseShow

baseUrl = settings.HOST + "static/"

##################################################################################################################


class DictionarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Dictionary
        fields = "__all__"


class DictionaryKeyValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dictionary
        fields = ["key", "value", "description",
                  "type", "sort_index", "active"]


##################################################################################################################


class GhiNhanMauXetNghiemSerializer(serializers.ModelSerializer):
    class Meta:
        model = GhiNhanMauXetNghiem
        fields = "__all__"


class GhiNhanMauXetNghiemLessDataSerializer(serializers.ModelSerializer):
    user_infor = serializers.SerializerMethodField()

    def get_user_infor(self, GhiNhanMauXetNghiem):
        data = {}
        if GhiNhanMauXetNghiem.user:
            try:
                data = UserBaseShow(GhiNhanMauXetNghiem.user).data
            except Exception as e:
                data = None
        return data

    class Meta:
        model = GhiNhanMauXetNghiem
        fields = [
            "id",
            "DVYEUCAU_ID",
            "BENHNHAN_ID",
            "TRANGTHAI",
            "TRANGTHAI_UPDATED",
            "type",
            "note",
            "sort_index",
            "active",
            "created_date",
            "updated_date"
        ] + ["user_infor"]


##################################################################################################################


class IPManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = IPManager
        fields = "__all__"


##################################################################################################################


def serialize_request(request):
    META = None
    if hasattr(request, "META"):
        META = {key: request.META.get(key, None) for key in request.META}

    # Serialize as usual
    serialized_request = {
        "method": request.method,
        "path": request.path,
        "headers": {key: value for key, value in request.headers.items()},
        "META": META,
    }
    # Dump the serialized request as a JSON string
    string_json = json.dumps(serialized_request, indent=2)
    return string_json
