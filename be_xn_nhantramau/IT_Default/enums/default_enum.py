from enum import Enum


class AbstractEnum(Enum):
    pass

    @classmethod
    def get_for_show(cls):  # Added 'cls' parameter
        # Changed 'this' to 'cls'
        list_sort_enum = [
            # Removed 'key' and 'sort'
            {"id": member.value["id"], "description": member.value["description"]}
            for member in cls
        ]
        return list_sort_enum

    @classmethod
    def get_all(cls):
        # This method returns all attributes of the enum members
        return [member.value for member in cls]


class DefaultEnum(Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class SortEnum(AbstractEnum):
    SORT_NHAP_PHONG_DESC = {
        "id": 1,
        "key": "created_date",
        "sort": "-",
        "description": "Ngày tạo gần đây",
    }

    SORT_NHAP_PHONG_ASC = {
        "id": 2,
        "key": "created_date",
        "sort": "",
        "description": "Ngày tạo lâu nhất",
    }
