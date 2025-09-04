def BaseDataRespone():
    data = {
        "data": {},
        "message": "",
        "status_code": 200
    }
    # res['data'] = UserBaseShow(request.user).data
    # res['message'] = "Lấy dữ liệu thành công!"
    # res['result'] = 1
    # res['status_code'] = 200
    return data


MESSAGE = {
    # ---------------------------- #
    # ---------------------------- #
    # ---------- MESSAGE --------- #
    # ---------------------------- #
    # ---------------------------- #
    # ------- Message Room ------- #
    # SAFE
    "MS_FIND_ROOM_SUCCESS": "Tìm thành công!",
    "MS_CREATE_ROOM_SUCCESS": "Tạo thành công!",
    # MACRO
    "MS_NOT_FIND_ROOM": "Không tìm thấy phòng chat!",
    "MS_NOT_FIND_ROOM_ALL": "Hiện bạn không có phòng chat nào!",
    # BUG
    "MS_NOT_FIND_MEMBER_ROOM": "Không tìm thấy thành viên",

    # ------- Message USER ------- #
    # SAFE

    # BUG
    "MS_NOT_FIND_USER_AUTHEN": "Người dùng chưa đăng nhập",
    # Register
    "MS_CREATE_USER_SUCCESSFULLY": lambda username: f"Tạo thành công tài khoản {username}!",
    "MS_USER_CREATE_DUPLICATE_USERNAME": "Hiện tên tài khoản này đã có người sử dụng!",

    # ----------- ROOM ----------- #
    # BUG
    "MS_ROOM_CREATE_FAIL_NOTIFY": "Tạo phòng hội thoại thất bại!",

    # ---------------------------- #
    # ---------------------------- #
    # ---------- SERVER ---------- #
    # ---------------------------- #
    # ---------------------------- #
    "MS_SERVER_MYSQL_FAIL": "Lỗi truy xuất đến cơ sở dữ liệu!!",

    # ---------------------------- #
    # ---------------------------- #
    # --------- LOGGING ---------- #
    # ---------------------------- #
    # ---------------------------- #
    # ----------- USER ----------- #
    "MS_USER_AUTHEN_SUCCESS": lambda username: f"{username} => Đăng nhập thành công!!",
    "MS_USER_AUTHEN_FAIL": "Đăng nhập không thành công",

    # ----------- ROOM ----------- #
    # BUG
    "MS_ROOM_CREATE_FAIL": "Lỗi tạo các thành viên trong phòng thoại => Delete phòng trò chuyện",
}
