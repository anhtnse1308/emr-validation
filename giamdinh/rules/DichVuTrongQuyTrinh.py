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
