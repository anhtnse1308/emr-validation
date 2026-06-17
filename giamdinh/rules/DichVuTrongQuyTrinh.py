"""
Rule I.2 – Dịch vụ kỹ thuật nằm trong quy trình của DVKT khác (mã từ chối S054.1)
Căn cứ:
  - QĐ 3983/QĐ-BYT ngày 03/10/2014 (QTKT Nội khoa Tim mạch)
  - QĐ 3906/QĐ-BYT ngày 12/10/2012 (QTKT Nhãn khoa)
  - QĐ 25/QĐ-BYT ngày 03/01/2014 (QTKT Chẩn đoán hình ảnh)
  - QĐ 654/QĐ-BYT ngày 24/02/2014 (QTKT Nội khoa Cơ Xương Khớp)

Nguyên tắc: nếu trong cùng 1 MA_LK có cả DVKT "cha" và DVKT "con",
thì dịch vụ "con" không được thanh toán riêng.

Detect: group XML3 theo MA_LK, kiểm tra tập MA_DICH_VU trong từng nhóm.
"""

from collections import defaultdict
from giamdinh.GiamDinhBase import GiamDinhBase, GiamDinhError

# ---------------------------------------------------------------------------
# Bảng quy tắc: (set mã DVKT cha, set mã DVKT con, mô tả, căn cứ)
# Thêm rule mới tại đây khi có văn bản mới – không cần sửa logic check()
# ---------------------------------------------------------------------------
CONCURRENT_RULES: list[tuple[set, set, str, str]] = [

    # -----------------------------------------------------------------------
    # Tim mạch – QĐ 3983/QĐ-BYT
    # -----------------------------------------------------------------------
    (
        # Cha: Nong và đặt stent động mạch vành (Quy trình số 22)
        {
            "17.106", "17.107", "17.108",  # Nong + đặt stent ĐMV (nhiều biến thể)
            "17.10600", "17.10601", "17.10602",
        },
        # Con: Chụp động mạch vành dưới DSA
        {
            "17.060", "17.061", "17.062",
            "17.06000", "17.06001",
        },
        "Chụp động mạch vành dưới DSA là bước trong quy trình Nong+đặt stent ĐMV (QT số 22). "
        "Không thanh toán Chụp ĐMV khi thực hiện đồng thời Nong+đặt stent ĐMV.",
        "QĐ 3983/QĐ-BYT ngày 03/10/2014 (QT số 22) + QĐ 7435/QĐ-BYT ngày 14/12/2018",
    ),
    (
        # Cha: Chụp, nong và đặt stent động mạch vành (cùng nhóm trên)
        {
            "17.106", "17.107", "17.108",
            "17.10600", "17.10601", "17.10602",
        },
        # Con: Hút huyết khối trong động mạch vành
        {
            "17.085", "17.086",
            "17.08500", "17.08600",
        },
        "Hút huyết khối ĐMV đồng thời Chụp/nong/đặt stent ĐMV: "
        "vật tư lấy huyết khối đã tính trong gói dịch vụ. Không thanh toán riêng Hút huyết khối.",
        "QĐ 3983/QĐ-BYT ngày 03/10/2014 (QT số 22) + QĐ 7435/QĐ-BYT ngày 14/12/2018",
    ),

    # -----------------------------------------------------------------------
    # Nhãn khoa – QĐ 3906/QĐ-BYT ngày 12/10/2012
    # -----------------------------------------------------------------------
    (
        # Cha: Phẫu thuật cắt bè củng giác mạc (QT số 8)
        {
            "27.008", "27.00800", "27.00801",
        },
        # Con: Phẫu thuật cắt mống mắt chu biên
        {
            "27.015", "27.01500", "27.01501",
        },
        "Cắt mống mắt chu biên là bước trong quy trình Cắt bè củng giác mạc (QT số 8). "
        "Không thanh toán Cắt mống mắt chu biên khi thực hiện đồng thời.",
        "QĐ 3906/QĐ-BYT ngày 12/10/2012 (QT số 8)",
    ),
    (
        # Cha: Phẫu thuật lấy thủy tinh thể trong bao (QT số 69)
        {
            "27.069", "27.06900", "27.06901",
        },
        # Con: Phẫu thuật cắt mống mắt chu biên
        {
            "27.015", "27.01500", "27.01501",
        },
        "Cắt mống mắt chu biên là bước trong quy trình Lấy TTT trong bao (QT số 69). "
        "Không thanh toán Cắt mống mắt chu biên khi thực hiện đồng thời.",
        "QĐ 3906/QĐ-BYT ngày 12/10/2012 (QT số 69)",
    ),

    # -----------------------------------------------------------------------
    # Chẩn đoán hình ảnh / Can thiệp – QĐ 25/QĐ-BYT + QĐ 654/QĐ-BYT
    # -----------------------------------------------------------------------
    (
        # Cha: Chọc sinh thiết u/hạch dưới SA (QT 145, 146, 163)
        {
            "18.145", "18.146", "18.163",
            "18.14500", "18.14600", "18.16300",
        },
        # Con: Siêu âm hạch u
        {
            "18.SAU", "18.009", "18.00900",
            "18.010", "18.01000",
        },
        "Siêu âm hạch/u là bước trong quy trình Chọc sinh thiết u/hạch dưới SA (QT 145,146,163). "
        "Không thanh toán SA hạch/u khi thực hiện đồng thời.",
        "QĐ 25/QĐ-BYT ngày 03/01/2014 (QT 145, 146, 163)",
    ),
    (
        # Cha: Chọc nang tuyến giáp dưới SA (QT 150)
        {
            "18.150", "18.15000",
        },
        # Con: Siêu âm tuyến giáp
        {
            "18.011", "18.01100",
            "18.012", "18.01200",
        },
        "Siêu âm tuyến giáp là bước trong quy trình Chọc nang tuyến giáp dưới SA (QT 150). "
        "Không thanh toán SA tuyến giáp khi thực hiện đồng thời.",
        "QĐ 25/QĐ-BYT ngày 03/01/2014 (QT 150)",
    ),
    (
        # Cha: Tiêm gân / Chọc hút dịch khớp / Tiêm khớp dưới SA
        {
            "18.164", "18.165",            # QĐ 25/QĐ-BYT QT 164, 165
            *{f"18.{i:03d}" for i in range(73, 86)},  # QĐ 654/QĐ-BYT QT 73-85
        },
        # Con: Siêu âm khớp / phần mềm
        {
            "18.020", "18.021", "18.022",
            "18.02000", "18.02100", "18.02200",
        },
        "Siêu âm khớp/phần mềm là bước trong quy trình Tiêm gân/khớp dưới SA hoặc Chọc hút dịch khớp. "
        "Không thanh toán SA khớp/phần mềm khi thực hiện đồng thời.",
        "QĐ 25/QĐ-BYT ngày 03/01/2014 (QT 164, 165) + QĐ 654/QĐ-BYT ngày 24/02/2014 (QT 73-85)",
    ),
]


class DichVuTrongQuyTrinh(GiamDinhBase):
    """
    Rule I.2: Từ chối DVKT "con" khi thực hiện đồng thời DVKT "cha".
    Mã từ chối: S054.1
    """

    def check(self, all_objects: dict) -> list[GiamDinhError]:
        errors: list[GiamDinhError] = []

        rows_xml3 = self._get_rows(all_objects, "XML3")
        groups = self._group_by_ma_lk(rows_xml3)

        for ma_lk, rows in groups.items():
            if not ma_lk:
                continue

            # Tập mã DVKT trong lần khám này
            dv_set = {
                (getattr(r, "MA_DICH_VU", None) or "").strip()
                for _, r in rows
            }

            for cha_set, con_set, mo_ta, can_cu in CONCURRENT_RULES:
                # Có bất kỳ dịch vụ cha nào?
                if not dv_set.intersection(cha_set):
                    continue
                # Có bất kỳ dịch vụ con nào bị từ chối?
                matched_con = dv_set.intersection(con_set)
                if not matched_con:
                    continue

                # Tìm các dòng chứa dịch vụ con → tạo lỗi
                for row_excel, rec in rows:
                    ma_dv = (getattr(rec, "MA_DICH_VU", None) or "").strip()
                    if ma_dv in matched_con:
                        errors.append(GiamDinhError(
                            sheet="XML3",
                            ma_lk=ma_lk,
                            row_excel=row_excel,
                            ma_ly_do="S054.1",
                            mo_ta=mo_ta,
                            can_cu=can_cu,
                            ma_dich_vu=ma_dv,
                        ))

        return errors

# ===========================================================================
# BỔ SUNG TỪ PDF 477 – Thông báo chuyên đề tháng 12/2022
# ===========================================================================
CONCURRENT_RULES += [

    # -----------------------------------------------------------------------
    # KT01_7 – Ngoại khoa tiêu hóa – QĐ 201/QĐ-BYT ngày 16/01/2014 (QT số 23)
    # -----------------------------------------------------------------------
    (
        # Cha: Phẫu thuật khâu lỗ thủng dạ dày hành tá tràng
        {"20.023", "20.02300", "20.02301"},
        # Con: Mở bụng thăm dò, lau rửa ổ bụng, đặt dẫn lưu
        {"20.001", "20.00100", "20.00101", "20.002", "20.00200"},
        "Mở bụng thăm dò/lau rửa ổ bụng/đặt dẫn lưu là bước trong quy trình "
        "Khâu lỗ thủng dạ dày hành tá tràng (QT số 23). Không thanh toán riêng.",
        "QĐ 201/QĐ-BYT ngày 16/01/2014 (QT ngoại khoa tiêu hóa, QT số 23)",
    ),

    # -----------------------------------------------------------------------
    # KT01_1 – Tai mũi họng
    # -----------------------------------------------------------------------
    (
        # Cha: Phẫu thuật tạo hình tai giữa
        {"22.050", "22.05000", "22.05001", "22.05002"},
        # Con: Mở sào bào
        {"22.010", "22.01000", "22.01001"},
        "Mở sào bào là bước trong quy trình PT tạo hình tai giữa. "
        "Không thanh toán Mở sào bào khi thực hiện đồng thời.",
        "Phụ lục 02 CV /GĐĐT-NVGĐ tháng 12/2022 – KT01_1 (S054.1)",
    ),

    # -----------------------------------------------------------------------
    # KT01_2 – Tai mũi họng
    # -----------------------------------------------------------------------
    (
        # Cha: Phẫu thuật mở sụn giáp dây thanh
        {"22.070", "22.07000", "22.07001"},
        # Con: Phẫu thuật mở khí quản
        {"22.005", "22.00500", "22.00501"},
        "PT mở khí quản là bước trong quy trình PT mở sụn giáp dây thanh. "
        "Không thanh toán PT mở khí quản khi thực hiện đồng thời.",
        "Phụ lục 02 CV /GĐĐT-NVGĐ tháng 12/2022 – KT01_2 (S054.1)",
    ),

    # -----------------------------------------------------------------------
    # KT01_3 – Ngoại khoa tổng quát
    # -----------------------------------------------------------------------
    (
        # Cha: Phẫu thuật thoát vị bẹn
        {"20.100", "20.10000", "20.10001", "20.10002"},
        # Con: Cắt nang thừng tinh
        {"20.110", "20.11000", "20.11001"},
        "Cắt nang thừng tinh là bước trong quy trình PT thoát vị bẹn. "
        "Không thanh toán Cắt nang thừng tinh khi thực hiện đồng thời.",
        "Phụ lục 02 CV /GĐĐT-NVGĐ tháng 12/2022 – KT01_3 (S054.1)",
    ),

    # -----------------------------------------------------------------------
    # KT01_4 – Vi sinh
    # -----------------------------------------------------------------------
    (
        # Cha: Vi khuẩn nuôi cấy định danh
        {"09.050", "09.05000", "09.05001", "09.05002"},
        # Con: Vi khuẩn nhuộm soi
        {"09.010", "09.01000", "09.01001"},
        "Vi khuẩn nhuộm soi là bước trong quy trình Vi khuẩn nuôi cấy định danh. "
        "Không thanh toán Nhuộm soi khi thực hiện đồng thời.",
        "Phụ lục 02 CV /GĐĐT-NVGĐ tháng 12/2022 – KT01_4 (S054.1)",
    ),

    # -----------------------------------------------------------------------
    # KT01_5 – Phẫu thuật thần kinh
    # -----------------------------------------------------------------------
    (
        # Cha: Phẫu thuật u não các loại
        {"23.050", "23.051", "23.052", "23.05000", "23.05100", "23.05200"},
        # Con: PT vá màng cứng / tạo hình màng cứng
        {"23.010", "23.011", "23.01000", "23.01100"},
        "PT vá/tạo hình màng cứng là bước trong quy trình PT u não. "
        "Không thanh toán riêng.",
        "Phụ lục 02 CV /GĐĐT-NVGĐ tháng 12/2022 – KT01_5 (S054.1)",
    ),

    # -----------------------------------------------------------------------
    # KT01_6 – Ngoại khoa tiêu hóa
    # -----------------------------------------------------------------------
    (
        # Cha: Phẫu thuật dạ dày các loại
        {"20.030", "20.031", "20.032", "20.033",
         "20.03000", "20.03100", "20.03200", "20.03300"},
        # Con: Nạo vét hạch
        {"20.200", "20.20000", "20.20001"},
        "Nạo vét hạch là bước trong quy trình PT dạ dày. "
        "Không thanh toán Nạo vét hạch khi thực hiện đồng thời.",
        "Phụ lục 02 CV /GĐĐT-NVGĐ tháng 12/2022 – KT01_6 (S054.1)",
    ),

    # -----------------------------------------------------------------------
    # KT01_10 – Ngoại khoa gan mật
    # -----------------------------------------------------------------------
    (
        # Cha: Phẫu thuật gan các loại
        {"20.060", "20.061", "20.062",
         "20.06000", "20.06100", "20.06200"},
        # Con: Cắt túi mật
        {"20.070", "20.07000", "20.07001"},
        "Cắt túi mật là bước trong quy trình PT gan. "
        "Không thanh toán Cắt túi mật khi thực hiện đồng thời.",
        "Phụ lục 02 CV /GĐĐT-NVGĐ tháng 12/2022 – KT01_10 (S054.1)",
    ),

    # -----------------------------------------------------------------------
    # KT01_12 – Ngoại khoa cột sống
    # -----------------------------------------------------------------------
    (
        # Cha: Phẫu thuật cột sống các loại
        {"23.100", "23.101", "23.102", "23.103",
         "23.10000", "23.10100", "23.10200"},
        # Con: PT ghép xương
        {"23.200", "23.20000", "23.20001"},
        "PT ghép xương là bước trong quy trình PT cột sống. "
        "Không thanh toán PT ghép xương khi thực hiện đồng thời.",
        "Phụ lục 02 CV /GĐĐT-NVGĐ tháng 12/2022 – KT01_12 (S054.1)",
    ),

    # -----------------------------------------------------------------------
    # KT01_16 – Ngoại khoa ổ bụng
    # -----------------------------------------------------------------------
    (
        # Cha: PT cắt ruột thừa / PT chửa ngoài tử cung vỡ / PT lấy thai
        {"20.140", "20.14000",        # cắt ruột thừa
         "24.050", "24.05000",        # chửa ngoài TC vỡ
         "24.010", "24.01000"},       # lấy thai
        # Con: Dẫn lưu cùng đồ Douglas
        {"24.200", "24.20000", "24.20001"},
        "Dẫn lưu cùng đồ Douglas là bước trong quy trình PT cắt ruột thừa / "
        "chửa ngoài TC vỡ / lấy thai. Không thanh toán riêng.",
        "Phụ lục 02 CV /GĐĐT-NVGĐ tháng 12/2022 – KT01_16 (S054.1)",
    ),

    # -----------------------------------------------------------------------
    # KT01_18 – Nội soi tiêu hóa
    # -----------------------------------------------------------------------
    (
        # Cha: Nội soi can thiệp dạ dày tá tràng (cầm máu, cắt polyp, ...)
        {"36.050", "36.051", "36.052", "36.053",
         "36.05000", "36.05100", "36.05200"},
        # Con: Nội soi thực quản dạ dày tá tràng thường (chẩn đoán)
        {"36.010", "36.011",
         "36.01000", "36.01100"},
        "Nội soi chẩn đoán TQDDTT là bước trong quy trình Nội soi can thiệp DDTT. "
        "Không thanh toán Nội soi chẩn đoán khi thực hiện đồng thời can thiệp.",
        "Phụ lục 02 CV /GĐĐT-NVGĐ tháng 12/2022 – KT01_18 (S054.1)",
    ),

    # -----------------------------------------------------------------------
    # KT01_19 – Nội soi đại trực tràng
    # -----------------------------------------------------------------------
    (
        # Cha: Can thiệp ống tiêu hóa dưới (cắt polyp, cầm máu đại tràng, ...)
        {"36.070", "36.071", "36.072",
         "36.07000", "36.07100"},
        # Con: Nội soi đại trực tràng toàn bộ ống mềm (chẩn đoán)
        {"36.060", "36.06000", "36.06001"},
        "Nội soi đại trực tràng toàn bộ là bước trong quy trình Can thiệp ống tiêu hóa dưới. "
        "Không thanh toán Nội soi chẩn đoán khi thực hiện đồng thời can thiệp.",
        "Phụ lục 02 CV /GĐĐT-NVGĐ tháng 12/2022 – KT01_19 (S054.1)",
    ),

    # -----------------------------------------------------------------------
    # KT01_21 – Tiết niệu
    # -----------------------------------------------------------------------
    (
        # Cha: Nội soi tán sỏi niệu quản các loại
        {"28.050", "28.051", "28.052",
         "28.05000", "28.05100", "28.05200"},
        # Con: Đặt ống thông niệu quản qua nội soi (sond JJ)
        {"28.020", "28.02000", "28.02001"},
        "Đặt sond JJ là bước trong quy trình Nội soi tán sỏi niệu quản. "
        "Không thanh toán Đặt sond JJ khi thực hiện đồng thời.",
        "Phụ lục 02 CV /GĐĐT-NVGĐ tháng 12/2022 – KT01_21 (S054.1)",
    ),

    # -----------------------------------------------------------------------
    # KT189_2 – Tim mạch
    # -----------------------------------------------------------------------
    (
        # Cha: Lập trình máy tạo nhịp
        {"17.200", "17.20000", "17.20001"},
        # Con: Đo điện tâm đồ
        {"17.001", "17.00100"},
        "Đo điện tâm đồ là bước trong quy trình Lập trình máy tạo nhịp. "
        "Không thanh toán Đo ĐTĐ khi thực hiện đồng thời.",
        "Phụ lục 02 CV /GĐĐT-NVGĐ tháng 12/2022 – KT189_2 (S054.1)",
    ),

    # -----------------------------------------------------------------------
    # KT189_3 – Bỏng
    # -----------------------------------------------------------------------
    (
        # Cha: Rạch hoại tử bỏng giải thoát chèn ép (STT 106)
        {"31.106", "31.10600"},
        # Con: Thay băng bỏng
        {"31.001", "31.00100", "31.002", "31.00200"},
        "Thay băng bỏng là bước trong quy trình Rạch hoại tử bỏng giải thoát chèn ép. "
        "Không thanh toán Thay băng bỏng khi thực hiện đồng thời.",
        "Phụ lục 02 CV /GĐĐT-NVGĐ tháng 12/2022 – KT189_3 (S054.1)",
    ),

    # -----------------------------------------------------------------------
    # KT189_4 – Bỏng
    # -----------------------------------------------------------------------
    (
        # Cha: Khâu cầm máu/thắt mạch máu cấp cứu chảy máu trong bỏng sâu (STT 107)
        {"31.107", "31.10700"},
        # Con: Thay băng bỏng
        {"31.001", "31.00100", "31.002", "31.00200"},
        "Thay băng bỏng là bước trong quy trình Khâu cầm máu bỏng sâu. "
        "Không thanh toán Thay băng bỏng khi thực hiện đồng thời.",
        "Phụ lục 02 CV /GĐĐT-NVGĐ tháng 12/2022 – KT189_4 (S054.1)",
    ),

    # -----------------------------------------------------------------------
    # KT189_5 – Sản khoa
    # -----------------------------------------------------------------------
    (
        # Cha: Đẻ thường hoặc Đẻ khó
        {"24.001", "24.00100",   # Đẻ thường
         "24.002", "24.00200"},  # Đẻ khó
        # Con: Làm lại thành âm đạo, tầng sinh môn (STT 108)
        {"24.108", "24.10800"},
        "Làm lại thành âm đạo/tầng sinh môn là bước trong quy trình Đẻ thường/Đẻ khó. "
        "Không thanh toán riêng.",
        "Phụ lục 02 CV /GĐĐT-NVGĐ tháng 12/2022 – KT189_5 (S054.1)",
    ),

    # -----------------------------------------------------------------------
    # KT189_6 – Nhãn khoa (QĐ 3906/QĐ-BYT, QT số 88)
    # -----------------------------------------------------------------------
    (
        # Cha: Đo công suất TTT nhân tạo tự động bằng SA / bằng SA AB
        {"27.088", "27.08800", "27.08801"},
        # Con: Đo khúc xạ giác mạc Javal
        {"27.005", "27.00500"},
        "Đo khúc xạ giác mạc Javal là bước trong quy trình Tính công suất TTT (QT số 88). "
        "Không thanh toán Đo khúc xạ Javal khi thực hiện đồng thời.",
        "QĐ 3906/QĐ-BYT ngày 12/10/2012 (QT số 88) – KT189_6 (S054.1)",
    ),

    # -----------------------------------------------------------------------
    # KT189_7 – Thận nhân tạo cấp cứu (QĐ 2482/QĐ-BYT, QT số 26)
    # -----------------------------------------------------------------------
    (
        # Cha: Thận nhân tạo cấp cứu
        {"13.026", "13.02600", "13.02601"},
        # Con: Đặt catheter lọc máu cấp cứu
        {"13.001", "13.00100", "13.00101"},
        "Đặt catheter lọc máu cấp cứu là bước trong quy trình Thận nhân tạo cấp cứu (QT 26). "
        "Không thanh toán riêng Đặt catheter.",
        "QĐ 2482/QĐ-BYT ngày 13/4/2018 (QT 26) – KT189_7 (S054.1)",
    ),

    # -----------------------------------------------------------------------
    # KT189_8 – Cơ xương khớp (QĐ 654/QĐ-BYT, QT 9-23)
    # Hút dịch khớp → không thanh toán thêm Tiêm khớp cùng vị trí
    # -----------------------------------------------------------------------
    (
        # Cha: Hút dịch khớp (gối, cổ tay, háng, ...)
        {"15.009", "15.010", "15.011", "15.012", "15.013",
         "15.00900", "15.01000", "15.01100"},
        # Con: Tiêm khớp cùng vị trí
        {"15.020", "15.021", "15.022", "15.023", "15.024",
         "15.02000", "15.02100", "15.02200"},
        "Tiêm khớp là bước trong quy trình Hút dịch khớp (QT 9-23 QĐ 654/QĐ-BYT). "
        "Không thanh toán Tiêm khớp khi thực hiện đồng thời Hút dịch cùng vị trí.",
        "QĐ 654/QĐ-BYT ngày 24/02/2014 (QT 9-23) – KT189_8 (S054.1)",
    ),

    # -----------------------------------------------------------------------
    # KT189_9 – Phụ sản (QĐ 1377/QĐ-BYT, QT số 30)
    # -----------------------------------------------------------------------
    (
        # Cha: PT mở bụng cắt tử cung hoàn toàn + 2 phần phụ (QT 30)
        {"24.030", "24.03000", "24.03001"},
        # Con: PT mở bụng cắt u buồng trứng / cắt phần phụ
        {"24.040", "24.041",
         "24.04000", "24.04100"},
        "PT cắt u buồng trứng/phần phụ là bước trong quy trình PT cắt tử cung toàn bộ + 2 phần phụ "
        "(QT số 30 – tử cung bao gồm vòi TC và buồng trứng). Không thanh toán riêng.",
        "QĐ 1377/QĐ-BYT ngày 24/4/2013 (QT số 30) – KT189_9 (S054.1)",
    ),

    # -----------------------------------------------------------------------
    # KT32 – H. Pylori Ag test nhanh đồng thời nội soi dạ dày/tá tràng
    # Căn cứ: TT 39/2018/TT-BYT (STT 1673)
    # -----------------------------------------------------------------------
    (
        # Cha: Nội soi dạ dày hoặc tá tràng (chẩn đoán hoặc can thiệp)
        {"36.010", "36.011", "36.050", "36.051", "36.052",
         "36.01000", "36.01100", "36.05000", "36.05100"},
        # Con: HP Ag test nhanh
        {"09.1673", "09.167300"},
        "HP Ag test nhanh không được thanh toán khi thực hiện đồng thời Nội soi dạ dày/tá tràng "
        "theo điều kiện quy định tại TT 39/2018/TT-BYT (STT 1673).",
        "TT 39/2018/TT-BYT ngày 30/11/2018 (STT 1673) – KT32 (S023.1)",
    ),

    # -----------------------------------------------------------------------
    # KT118 – DVKT điều trị đích ung thư + thuốc điều trị đích
    # (detect cross XML3 + XML2 – xử lý riêng trong DieuKienDacBiet.py)
    # Ghi nhận tại đây để tham khảo, logic phức tạp hơn cần cross-sheet
    # -----------------------------------------------------------------------
]