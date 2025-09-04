import random
import string
from datetime import datetime
from ..models import *


def GenerateCodeRoom():
    code = (datetime.now().strftime(
        '%Y%m%d%H%M%S') + f'{random.randint(1, 99)}') + f'{random.choice(string.ascii_lowercase)}'
    return code


def GenerationSTT_Ngay_DGNK():
    # res
    res = {
        'data': '',
        'status': 0
    }
    # Code
    code = 'ERROR'
    # get date current for query
    current_date = datetime.now()
    formatted_date = current_date.strftime('%Y-%m-%d')
    try:
        list_filter = NKDanhGia.objects.filter(created_date__icontains=f'{formatted_date}') \
            .order_by('-created_date')
        list_filter = list_filter[:20]
        # Get danh sách NKDanhGia sắp xếp theo thời gian tạo
        len_ = len(list_filter)
        # print(list_filter.query)
        stt_ngay_temp = []
        if len_ > 0:
            # print('Đã có')
            stt_ngay_temp = list_filter[0].STT_NGAY.split('_')
            # Cập nhật + 1
            stt_ngay_temp[0] = str(int(stt_ngay_temp[0]) + 1)
        else:
            # print('Chưa có')
            stt_ngay_temp = ['1', current_date.strftime('%d%m%Y')]
        # print(stt_ngay_temp)
        code = f'{stt_ngay_temp[0]}_{stt_ngay_temp[1]}'

        # set result
        res['data'] = code
        res['status'] = 1

    except Exception as e:
        print(e)
        code += current_date.strftime('%Y%m%d%H%M%S')
        # set result
        res['data'] = code
        res['status'] = 0
    return res
