"""
Rule – Giới hạn tần suất thực hiện DVKT trong ngày (mã từ chối S011.1, S016.47, D002.2)
Căn cứ:
  KT184 / S011.1  – AFB nhuộm trực tiếp: không quá 2 lần/ngày
                    QĐ 1314/QĐ-BYT ngày 24/3/2022 (Hướng dẫn CĐ-ĐT-DP bệnh lao)
  KT193 / S016.47 – Monitoring sản khoa (theo dõi tim thai + cơn co TC): 1 lần/ngày
                    QĐ 7435/QĐ-BYT ngày 14/12/2018 (STT 5356) + TT 13/2019/TT-BYT
  KT183 / D002.2  – Chụp CT có thuốc cản quang nhưng không kê thuốc cản quang
                    TT 13/2019/TT-BYT – Điều chỉnh về giá CT không thuốc cản quang

Logic detect (KT184, KT193):
  Group XML3 theo (MA_LK, NGAY_TH_YL[:8]), đếm số lần xuất hiện mã DVKT mục tiêu.

Logic detect (KT183):
  Tìm MA_LK có mã CT cản quang trong XML3 nhưng KHÔNG có thuốc cản quang trong XML2.
"""

from collections import defaultdict
from giamdinh.GiamDinhBase import GiamDinhBase, GiamDinhError

# ---------------------------------------------------------------------------
# KT184 – Mã DVKT xét nghiệm AFB nhuộm trực tiếp
# ---------------------------------------------------------------------------
MA_AFB = {
    "09.AFB1", "09.AFB2",           # placeholder – thay bằng mã thực tế
    "09.001", "09.00100",           # AFB trực tiếp nhuộm Ziehl-Neelsen
    "09.002", "09.00200",           # AFB trực tiếp nhuộm huỳnh quang
}
MAX_AFB_NGAY = 2

# ---------------------------------------------------------------------------
# KT193 – Mã DVKT Monitoring sản khoa (theo dõi tim thai + cơn co TC)
# ---------------------------------------------------------------------------
MA_MONITORING_SAN = {
    "35.5356", "35.535600",         # STT 5356 theo QĐ 7435/QĐ-BYT
    "35.001",  "35.00100",          # Monitoring sản khoa (placeholder)
}
MAX_MONITORING_NGAY = 1

# ---------------------------------------------------------------------------
# KT183 – CT có thuốc cản quang
# ---------------------------------------------------------------------------
# Mã DVKT "Chụp CT có thuốc cản quang" – prefix hoặc set cụ thể
MA_CT_CO_CAN_QUANG_PREFIXES = (
    "18.CT.CQ",     # placeholder prefix
)
MA_CT_CO_CAN_QUANG = {
    "18.100", "18.101", "18.102", "18.103", "18.104",   # CT đầu, ngực, bụng... có CQ
    "18.10000", "18.10100", "18.10200", "18.10300",
}

# Mã thuốc cản quang trong XML2 (MA_THUOC hoặc MA_NHOM)
MA_THUOC_CAN_QUANG = {
    "40.CQ1", "40.CQ2",             # placeholder
    "40.500", "40.501", "40.502",   # thuốc cản quang iod
    "40.503", "40.504",
}
MA_NHOM_CAN_QUANG = {"6"}           # MA_NHOM = 6 = thuốc cản quang (tham khảo)

CAN_CU_AFB        = "QĐ 1314/QĐ-BYT ngày 24/3/2022 (Hướng dẫn CĐ-ĐT-DP bệnh lao)"
CAN_CU_MONITORING = "QĐ 7435/QĐ-BYT ngày 14/12/2018 (STT 5356) + TT 13/2019/TT-BYT"
CAN_CU_CT_CQ      = "TT 13/2019/TT-BYT Phụ lục III – Điều chỉnh giá CT có/không cản quang"


def _ngay(ngay_str: str) -> str:
    """Lấy 8 ký tự ngày từ chuỗi DATE12 hoặc DATE8."""
    return str(ngay_str or "")[:8]


def _is_ct_co_cq(ma_dv: str) -> bool:
    ma_dv = ma_dv.strip()
    if ma_dv in MA_CT_CO_CAN_QUANG:
        return True
    return any(ma_dv.startswith(p) for p in MA_CT_CO_CAN_QUANG_PREFIXES)


class GioiHanTanSuat(GiamDinhBase):
    """
    Rule giới hạn tần suất DVKT trong ngày:
      KT184 – AFB ≤ 2 lần/ngày
      KT193 – Monitoring sản khoa ≤ 1 lần/ngày
      KT183 – CT cản quang nhưng không có thuốc cản quang
    """

    def check(self, all_objects: dict) -> list[GiamDinhError]:
        errors: list[GiamDinhError] = []
        errors.extend(self._check_tan_suat(all_objects))
        errors.extend(self._check_ct_can_quang(all_objects))
        return errors

    # ------------------------------------------------------------------
    # KT184 + KT193 – Đếm số lần DVKT trong ngày
    # ------------------------------------------------------------------
    def _check_tan_suat(self, all_objects: dict) -> list[GiamDinhError]:
        errors: list[GiamDinhError] = []

        TAN_SUAT_RULES = [
            (MA_AFB,            MAX_AFB_NGAY,        "S011.1",  CAN_CU_AFB,
             "Xét nghiệm AFB trực tiếp"),
            (MA_MONITORING_SAN, MAX_MONITORING_NGAY, "S016.47", CAN_CU_MONITORING,
             "Monitoring sản khoa (theo dõi tim thai + cơn co TC)"),
        ]

        rows_xml3 = self._get_rows(all_objects, "XML3")

        for ma_set, max_lan, ma_ly_do, can_cu, ten_dv in TAN_SUAT_RULES:
            # Group: (MA_LK, ngày) → list[(row_excel, rec)]
            groups: dict[tuple, list] = defaultdict(list)
            for row_excel, rec in rows_xml3:
                ma_dv  = (getattr(rec, "MA_DICH_VU",  None) or "").strip()
                ma_lk  = (getattr(rec, "MA_LK",       None) or "").strip()
                ngay   = _ngay(getattr(rec, "NGAY_TH_YL", None) or "")
                if ma_dv in ma_set and ma_lk:
                    groups[(ma_lk, ngay)].append((row_excel, rec))

            for (ma_lk, ngay), rows in groups.items():
                if len(rows) > max_lan:
                    # Báo lỗi trên các dòng thừa (từ lần max_lan+1 trở đi)
                    for row_excel, rec in rows[max_lan:]:
                        ma_dv = (getattr(rec, "MA_DICH_VU", None) or "").strip()
                        errors.append(GiamDinhError(
                            sheet="XML3",
                            ma_lk=ma_lk,
                            row_excel=row_excel,
                            ma_ly_do=ma_ly_do,
                            mo_ta=(
                                f"'{ten_dv}' thực hiện {len(rows)} lần "
                                f"trong ngày {ngay}, vượt mức tối đa "
                                f"{max_lan} lần/ngày. "
                                f"Lần thứ {rows.index((row_excel, rec)) + 1} bị từ chối."
                            ),
                            can_cu=can_cu,
                            ma_dich_vu=ma_dv,
                        ))

        return errors

    # ------------------------------------------------------------------
    # KT183 – CT có thuốc cản quang nhưng không kê thuốc cản quang
    # ------------------------------------------------------------------
    def _check_ct_can_quang(self, all_objects: dict) -> list[GiamDinhError]:
        errors: list[GiamDinhError] = []

        # Tập MA_LK có thuốc cản quang trong XML2
        lk_co_thuoc_cq: set[str] = set()
        for _, rec in self._get_rows(all_objects, "XML2"):
            ma_lk   = (getattr(rec, "MA_LK",    None) or "").strip()
            ma_thuoc = (getattr(rec, "MA_THUOC", None) or "").strip()
            ma_nhom  = str(getattr(rec, "MA_NHOM", None) or "").strip()
            if ma_lk and (ma_thuoc in MA_THUOC_CAN_QUANG or
                          ma_nhom in MA_NHOM_CAN_QUANG):
                lk_co_thuoc_cq.add(ma_lk)

        # Kiểm tra XML3: CT có CQ nhưng MA_LK không có thuốc CQ
        for row_excel, rec in self._get_rows(all_objects, "XML3"):
            ma_lk = (getattr(rec, "MA_LK",      None) or "").strip()
            ma_dv  = (getattr(rec, "MA_DICH_VU", None) or "").strip()
            if not ma_lk or not ma_dv:
                continue
            if _is_ct_co_cq(ma_dv) and ma_lk not in lk_co_thuoc_cq:
                errors.append(GiamDinhError(
                    sheet="XML3",
                    ma_lk=ma_lk,
                    row_excel=row_excel,
                    ma_ly_do="D002.2",
                    mo_ta=(
                        f"DVKT '{ma_dv}' là Chụp CT có thuốc cản quang nhưng "
                        "không có thuốc cản quang trong XML2 của lần khám này. "
                        "Điều chỉnh về giá CT không thuốc cản quang theo TT 13/2019."
                    ),
                    can_cu=CAN_CU_CT_CQ,
                    ma_dich_vu=ma_dv,
                ))

        return errors