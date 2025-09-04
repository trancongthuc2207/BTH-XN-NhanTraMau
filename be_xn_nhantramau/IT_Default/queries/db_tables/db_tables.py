class NhapKhoa:
    # Class attribute
    ID = ''
    MABN = ''
    HOTEN = ''
    NGAYSINH = ''
    NAMSINH = ''
    PHAI = ''
    MAQL = ''
    MAKP = ''
    NGAY = ''
    KHOACHUYEN = ''
    CHANDOAN = ''
    MAICD = ''

    # Constructor method (initializer)
    def __init__(self, data_tuple):
        self.ID = data_tuple[0]  # Instance attribute
        self.MABN = data_tuple[1]
        self.HOTEN = data_tuple[2]
        self.NGAYSINH = data_tuple[3]
        self.NAMSINH = data_tuple[4]
        self.PHAI = data_tuple[5]
        self.MAQL = data_tuple[6]
        self.MAKP = data_tuple[7]
        self.NGAY = data_tuple[8]
        self.KHOACHUYEN = data_tuple[9]
        self.CHANDOAN = data_tuple[10]
        self.MAICD = data_tuple[11]
