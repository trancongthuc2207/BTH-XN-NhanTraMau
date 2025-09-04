from rest_framework import serializers
from .models import *
from .queries.db_tables.db_tables import *
from django.conf import settings
from general_utils.utils import *


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
