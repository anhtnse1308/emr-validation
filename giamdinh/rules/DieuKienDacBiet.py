"""
Rule – Điều kiện đặc biệt (nhiều mã lý do)
Các chuyên đề từ Phụ lục 02 PDF 477 không thuộc nhóm DVKT-trong-quy-trình
mà cần kiểm tra điều kiện lâm sàng, tuổi BN, loại hình KCB.

KT23  / D011.1  – DVKT chuyên khoa Nhi cho BN > 16 tuổi
KT47  / S006.122 – Vận động trị liệu hô hấp không phải bệnh phổi mạn (COPD/bệnh phổi mạn giai đoạn ổn định)
KT57  / S006.117 – Định lượng SCC không phải ung thư cổ tử cung / ung thư phổi
KT79  / S006.1   – PHCN cho BN ung thư (chống chỉ định)
KT84  / S011.1   – Nội soi tiêu hóa (TQDDTT) cho BN suy tim
KT144 / S018.4   – Tiêm/truyền TM, thay băng... cho BN nội trú (chỉ áp dụng ngoại trú)
KT147 / S016.12  – DVKT PHCN vượt số lượng cho phép/ngày
KT166 / T001.3   – Hút đờm qua NKQ/canuyn không có thở máy
"""

from collections import defaultdict
from giamdinh.GiamDinhBase import GiamDinhBase, GiamDinhError
from giamdinh.ICDHelper import ICDHelper

# ---------------------------------------------------------------------------
# KT23 – DVKT chuyên khoa Nhi cho BN > 16 tuổi (D011.1)
# TT 43/2013/TT-BYT
# ---------------------------------------------------------------------------
MA_DVKT_NHI_PREFIXES = ("35.NHI", "nhi.")   # placeholder – cần map theo danh mục Nhi
MA_DVKT_NHI = {
    "35.001", "35.002", "35.003",   # DVKT chuyên khoa Nhi (placeholder)
}
TUOI_NHI_MAX = 16   # BN > 16 tuổi không được dùng mã Nhi

# ---------------------------------------------------------------------------
# KT47 – Vận động trị liệu hô hấp (S006.122)
# Chỉ áp dụng COPD hoặc bệnh phổi mạn giai đoạn ổn định
# QĐ 1981/QĐ-BYT ngày 05/06/2014
# ---------------------------------------------------------------------------
MA_VD_TL_HO_HAP = {
    "40.1981", "40.198100",   # Vận động trị liệu hô hấp (placeholder)
    "34.001",  "34.00100",
}
ICD_COPD_PHOI_MAN = {"J44", "J41", "J42", "J43", "J47", "J84"}

# ---------------------------------------------------------------------------
# KT57 – Định lượng SCC (S006.117)
# Chỉ thanh toán ung thư cổ tử cung (C53) hoặc ung thư phổi (C33, C34)
# TT 35/TT-BYT
# ---------------------------------------------------------------------------
MA_XN_SCC = {
    "09.SCC1", "09.SCC100",   # Định lượng SCC (placeholder)
    "09.200",  "09.20000",
}
ICD_SCC_DUOC_PHEP = {"C53", "C33", "C34"}

# ---------------------------------------------------------------------------
# KT79 – PHCN cho BN ung thư (S006.1)
# QĐ 54/QĐ-BYT + QĐ 5737/QĐ-BYT
# ---------------------------------------------------------------------------
MA_PHCN_PREFIXES = ("34.", "33.")   # nhóm PHCN
ICD_UNG_THU = {f"C{i:02d}" for i in range(0, 98)}   # C00-C97

# ---------------------------------------------------------------------------
# KT84 – Nội soi TQDDTT cho BN suy tim (S011.1)
# QĐ 3805/QĐ-BYT ngày 25/9/2014 (QT số 14, 15, 63, 64)
# ---------------------------------------------------------------------------
MA_NS_TQDDTT = {
    "36.010", "36.011", "36.01000", "36.01100",   # NS chẩn đoán
    "36.014", "36.015", "36.01400", "36.01500",   # QT 63, 64
}
ICD_SUY_TIM = {"I50"}

# ---------------------------------------------------------------------------
# KT144 – Tiêm/truyền/thay băng/cắt chỉ... cho BN nội trú (S018.4)
# TT 50/2017/TT-BYT – Chỉ áp dụng ngoại trú
# ---------------------------------------------------------------------------
MA_NGOAITRU_ONLY = {
    "41.001", "41.00100",   # Tiêm bắp
    "41.002", "41.00200",   # Tiêm tĩnh mạch
    "41.003", "41.00300",   # Truyền TM
    "41.010", "41.01000",   # Tháo bột
    "41.020", "41.02000",   # Cắt chỉ
}
MA_LOAI_KCB_NOI_TRU = {"03", "04", "06"}

# ---------------------------------------------------------------------------
# KT147 – PHCN vượt số lượng/ngày (S016.12)
# TT 50/2017/TT-BYT Danh mục 2 STT 18
# ---------------------------------------------------------------------------
MA_PHCN_GIOI_HAN: dict[str, int] = {
    # ma_dvkt → số lần tối đa / ngày
    "34.018": 1,   # Vận động trị liệu hô hấp (STT 18 Danh mục 2 TT50)
    "34.01800": 1,
    # Thêm các mã PHCN có giới hạn/ngày theo danh mục TT50
}

# ---------------------------------------------------------------------------
# KT166 – Hút đờm qua NKQ/canuyn không có thở máy (T001.3)
# ---------------------------------------------------------------------------
MA_HUT_DOM_NKQ = {
    "41.HUT1", "41.HUT100",   # Hút đờm qua NKQ/canuyn kín (placeholder)
    "41.050",  "41.05000",
}
MA_THO_MAY = {
    "41.TM1", "41.TM100",     # Thở máy các loại (placeholder)
    "41.100", "41.10000", "41.10001", "41.10002",
}

# Căn cứ
_CC = {
    "KT23":  "TT 43/2013/TT-BYT",
    "KT47":  "QĐ 1981/QĐ-BYT ngày 05/06/2014 (QTKT Nội khoa Hô hấp)",
    "KT57":  "TT 35/TT-BYT (Danh mục DVKT BHYT)",
    "KT79":  "QĐ 54/QĐ-BYT ngày 06/01/2014 + QĐ 5737/QĐ-BYT ngày 22/12/2017",
    "KT84":  "QĐ 3805/QĐ-BYT ngày 25/9/2014 (QT số 14, 15, 63, 64)",
    "KT144": "TT 50/2017/TT-BYT",
    "KT147": "TT 50/2017/TT-BYT Danh mục 2 STT 18",
    "KT166": "Phụ lục 02 CV /GĐĐT-NVGĐ tháng 12/2022 – KT166",
}


def _tinh_tuoi(ngay_sinh: str, ngay_kham: str) -> int | None:
    """Tính tuổi BN tại thời điểm khám. Trả None nếu không parse được."""
    try:
        ns = str(ngay_sinh or "")[:8]
        nk = str(ngay_kham  or "")[:8]
        if len(ns) < 8 or len(nk) < 8:
            return None
        year_sinh = int(ns[:4]);  year_kham = int(nk[:4])
        month_sinh = int(ns[4:6]); month_kham = int(nk[4:6])
        day_sinh = int(ns[6:8]);   day_kham  = int(nk[6:8])
        tuoi = year_kham - year_sinh
        if (month_kham, day_kham) < (month_sinh, day_sinh):
            tuoi -= 1
        return tuoi
    except (ValueError, TypeError):
        return None


class DieuKienDacBiet(GiamDinhBase):
    """
    Các rule điều kiện đặc biệt từ Phụ lục 02 PDF 477.
    Mỗi rule là 1 method _check_KTxxx riêng → dễ bật/tắt từng rule.
    """

    def check(self, all_objects: dict) -> list[GiamDinhError]:
        errors: list[GiamDinhError] = []
        errors.extend(self._check_kt23(all_objects))
        errors.extend(self._check_kt47(all_objects))
        errors.extend(self._check_kt57(all_objects))
        errors.extend(self._check_kt79(all_objects))
        errors.extend(self._check_kt84(all_objects))
        errors.extend(self._check_kt144(all_objects))
        errors.extend(self._check_kt147(all_objects))
        errors.extend(self._check_kt166(all_objects))
        return errors

    # ------------------------------------------------------------------
    # KT23 – DVKT Nhi cho BN > 16 tuổi
    # ------------------------------------------------------------------
    def _check_kt23(self, all_objects: dict) -> list[GiamDinhError]:
        errors = []
        xml1_map = {
            getattr(r, "MA_LK", "") or "": r
            for _, r in self._get_rows(all_objects, "XML1")
        }
        for row_excel, rec in self._get_rows(all_objects, "XML3"):
            ma_lk = (getattr(rec, "MA_LK",      None) or "").strip()
            ma_dv  = (getattr(rec, "MA_DICH_VU", None) or "").strip()
            if not ma_lk or not ma_dv:
                continue
            is_nhi = ma_dv in MA_DVKT_NHI or any(
                ma_dv.startswith(p) for p in MA_DVKT_NHI_PREFIXES
            )
            if not is_nhi:
                continue
            rec1 = xml1_map.get(ma_lk)
            if not rec1:
                continue
            ngay_sinh = getattr(rec1, "NGAY_SINH", "") or ""
            ngay_vao  = getattr(rec1, "NGAY_VAO",  "") or ""
            tuoi = _tinh_tuoi(ngay_sinh, ngay_vao)
            if tuoi is not None and tuoi > TUOI_NHI_MAX:
                errors.append(GiamDinhError(
                    sheet="XML3", ma_lk=ma_lk, row_excel=row_excel,
                    ma_ly_do="D011.1",
                    mo_ta=(
                        f"DVKT chuyên khoa Nhi '{ma_dv}' áp dụng cho BN "
                        f"{tuoi} tuổi (> {TUOI_NHI_MAX} tuổi). "
                        "Không được thanh toán theo mã và giá Nhi."
                    ),
                    can_cu=_CC["KT23"], ma_dich_vu=ma_dv,
                ))
        return errors

    # ------------------------------------------------------------------
    # KT47 – Vận động trị liệu hô hấp không phải COPD/bệnh phổi mạn
    # ------------------------------------------------------------------
    def _check_kt47(self, all_objects: dict) -> list[GiamDinhError]:
        errors = []
        icd_map = {
            getattr(r, "MA_LK", "") or "": ICDHelper.from_record(r)
            for _, r in self._get_rows(all_objects, "XML1")
        }
        for row_excel, rec in self._get_rows(all_objects, "XML3"):
            ma_lk = (getattr(rec, "MA_LK",      None) or "").strip()
            ma_dv  = (getattr(rec, "MA_DICH_VU", None) or "").strip()
            if not ma_lk or ma_dv not in MA_VD_TL_HO_HAP:
                continue
            icd = icd_map.get(ma_lk, ICDHelper("", ""))
            if not icd.has_any(ICD_COPD_PHOI_MAN):
                errors.append(GiamDinhError(
                    sheet="XML3", ma_lk=ma_lk, row_excel=row_excel,
                    ma_ly_do="S006.122",
                    mo_ta=(
                        f"DVKT Vận động trị liệu hô hấp '{ma_dv}' chỉ định cho BN "
                        f"không mắc COPD/bệnh phổi mạn giai đoạn ổn định. {icd}"
                    ),
                    can_cu=_CC["KT47"], ma_dich_vu=ma_dv,
                ))
        return errors

    # ------------------------------------------------------------------
    # KT57 – Định lượng SCC không phải ung thư CTC / ung thư phổi
    # ------------------------------------------------------------------
    def _check_kt57(self, all_objects: dict) -> list[GiamDinhError]:
        errors = []
        icd_map = {
            getattr(r, "MA_LK", "") or "": ICDHelper.from_record(r)
            for _, r in self._get_rows(all_objects, "XML1")
        }
        for row_excel, rec in self._get_rows(all_objects, "XML3"):
            ma_lk = (getattr(rec, "MA_LK",      None) or "").strip()
            ma_dv  = (getattr(rec, "MA_DICH_VU", None) or "").strip()
            if not ma_lk or ma_dv not in MA_XN_SCC:
                continue
            icd = icd_map.get(ma_lk, ICDHelper("", ""))
            if not icd.has_any(ICD_SCC_DUOC_PHEP):
                errors.append(GiamDinhError(
                    sheet="XML3", ma_lk=ma_lk, row_excel=row_excel,
                    ma_ly_do="S006.117",
                    mo_ta=(
                        f"Xét nghiệm Định lượng SCC '{ma_dv}' chỉ định cho BN "
                        "không có chẩn đoán ung thư cổ tử cung (C53) "
                        f"hoặc ung thư phổi (C33/C34). {icd}"
                    ),
                    can_cu=_CC["KT57"], ma_dich_vu=ma_dv,
                ))
        return errors

    # ------------------------------------------------------------------
    # KT79 – PHCN cho BN ung thư
    # ------------------------------------------------------------------
    def _check_kt79(self, all_objects: dict) -> list[GiamDinhError]:
        errors = []
        icd_map = {
            getattr(r, "MA_LK", "") or "": ICDHelper.from_record(r)
            for _, r in self._get_rows(all_objects, "XML1")
        }
        for row_excel, rec in self._get_rows(all_objects, "XML3"):
            ma_lk = (getattr(rec, "MA_LK",      None) or "").strip()
            ma_dv  = (getattr(rec, "MA_DICH_VU", None) or "").strip()
            if not ma_lk or not ma_dv:
                continue
            is_phcn = any(ma_dv.startswith(p) for p in MA_PHCN_PREFIXES)
            if not is_phcn:
                continue
            icd = icd_map.get(ma_lk, ICDHelper("", ""))
            if icd.has_any(ICD_UNG_THU):
                errors.append(GiamDinhError(
                    sheet="XML3", ma_lk=ma_lk, row_excel=row_excel,
                    ma_ly_do="S006.1",
                    mo_ta=(
                        f"DVKT PHCN '{ma_dv}' bị chống chỉ định: "
                        f"BN có chẩn đoán khối u ác tính. {icd}"
                    ),
                    can_cu=_CC["KT79"], ma_dich_vu=ma_dv,
                ))
        return errors

    # ------------------------------------------------------------------
    # KT84 – Nội soi TQDDTT cho BN suy tim
    # ------------------------------------------------------------------
    def _check_kt84(self, all_objects: dict) -> list[GiamDinhError]:
        errors = []
        icd_map = {
            getattr(r, "MA_LK", "") or "": ICDHelper.from_record(r)
            for _, r in self._get_rows(all_objects, "XML1")
        }
        for row_excel, rec in self._get_rows(all_objects, "XML3"):
            ma_lk = (getattr(rec, "MA_LK",      None) or "").strip()
            ma_dv  = (getattr(rec, "MA_DICH_VU", None) or "").strip()
            if not ma_lk or ma_dv not in MA_NS_TQDDTT:
                continue
            icd = icd_map.get(ma_lk, ICDHelper("", ""))
            if icd.has_any(ICD_SUY_TIM):
                errors.append(GiamDinhError(
                    sheet="XML3", ma_lk=ma_lk, row_excel=row_excel,
                    ma_ly_do="S011.1",
                    mo_ta=(
                        f"Nội soi TQDDTT '{ma_dv}' chống chỉ định: "
                        f"BN có chẩn đoán suy tim (I50). {icd}"
                    ),
                    can_cu=_CC["KT84"], ma_dich_vu=ma_dv,
                ))
        return errors

    # ------------------------------------------------------------------
    # KT144 – Tiêm/truyền/thay băng... cho BN nội trú
    # ------------------------------------------------------------------
    def _check_kt144(self, all_objects: dict) -> list[GiamDinhError]:
        errors = []
        # MA_LK → MA_LOAI_KCB
        loai_kcb_map = {
            getattr(r, "MA_LK", "") or "": (getattr(r, "MA_LOAI_KCB", "") or "").strip()
            for _, r in self._get_rows(all_objects, "XML1")
        }
        for row_excel, rec in self._get_rows(all_objects, "XML3"):
            ma_lk = (getattr(rec, "MA_LK",      None) or "").strip()
            ma_dv  = (getattr(rec, "MA_DICH_VU", None) or "").strip()
            if not ma_lk or ma_dv not in MA_NGOAITRU_ONLY:
                continue
            loai = loai_kcb_map.get(ma_lk, "")
            if loai in MA_LOAI_KCB_NOI_TRU:
                errors.append(GiamDinhError(
                    sheet="XML3", ma_lk=ma_lk, row_excel=row_excel,
                    ma_ly_do="S018.4",
                    mo_ta=(
                        f"DVKT '{ma_dv}' (tiêm/truyền/thay băng/cắt chỉ...) "
                        f"chỉ áp dụng cho BN ngoại trú. "
                        f"Lần khám này là nội trú (MA_LOAI_KCB={loai}). "
                        "Không thanh toán riêng khi BN nội trú."
                    ),
                    can_cu=_CC["KT144"], ma_dich_vu=ma_dv,
                ))
        return errors

    # ------------------------------------------------------------------
    # KT147 – DVKT PHCN vượt số lượng/ngày
    # ------------------------------------------------------------------
    def _check_kt147(self, all_objects: dict) -> list[GiamDinhError]:
        errors = []
        groups: dict[tuple, list] = defaultdict(list)
        for row_excel, rec in self._get_rows(all_objects, "XML3"):
            ma_lk = (getattr(rec, "MA_LK",      None) or "").strip()
            ma_dv  = (getattr(rec, "MA_DICH_VU", None) or "").strip()
            ngay   = str(getattr(rec, "NGAY_TH_YL", None) or "")[:8]
            if ma_dv in MA_PHCN_GIOI_HAN and ma_lk:
                groups[(ma_lk, ma_dv, ngay)].append((row_excel, rec))

        for (ma_lk, ma_dv, ngay), rows in groups.items():
            max_lan = MA_PHCN_GIOI_HAN[ma_dv]
            if len(rows) > max_lan:
                for row_excel, rec in rows[max_lan:]:
                    errors.append(GiamDinhError(
                        sheet="XML3", ma_lk=ma_lk, row_excel=row_excel,
                        ma_ly_do="S016.12",
                        mo_ta=(
                            f"DVKT PHCN '{ma_dv}' thực hiện {len(rows)} lần "
                            f"ngày {ngay}, vượt mức tối đa {max_lan} lần/ngày."
                        ),
                        can_cu=_CC["KT147"], ma_dich_vu=ma_dv,
                    ))
        return errors

    # ------------------------------------------------------------------
    # KT166 – Hút đờm qua NKQ/canuyn không có thở máy
    # ------------------------------------------------------------------
    def _check_kt166(self, all_objects: dict) -> list[GiamDinhError]:
        errors = []
        # MA_LK có DVKT thở máy
        lk_co_tho_may: set[str] = set()
        for _, rec in self._get_rows(all_objects, "XML3"):
            ma_lk = (getattr(rec, "MA_LK",      None) or "").strip()
            ma_dv  = (getattr(rec, "MA_DICH_VU", None) or "").strip()
            if ma_lk and ma_dv in MA_THO_MAY:
                lk_co_tho_may.add(ma_lk)

        for row_excel, rec in self._get_rows(all_objects, "XML3"):
            ma_lk = (getattr(rec, "MA_LK",      None) or "").strip()
            ma_dv  = (getattr(rec, "MA_DICH_VU", None) or "").strip()
            if ma_lk and ma_dv in MA_HUT_DOM_NKQ and ma_lk not in lk_co_tho_may:
                errors.append(GiamDinhError(
                    sheet="XML3", ma_lk=ma_lk, row_excel=row_excel,
                    ma_ly_do="T001.3",
                    mo_ta=(
                        f"DVKT Hút đờm qua NKQ/canuyn '{ma_dv}' thực hiện cho BN "
                        "không có DVKT thở máy trong cùng lần khám. "
                        "Không thanh toán khi BN không sử dụng thở máy."
                    ),
                    can_cu=_CC["KT166"], ma_dich_vu=ma_dv,
                ))
        return errors