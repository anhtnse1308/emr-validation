"""
Rule I.1 – Chống chỉ định kỹ thuật (mã từ chối S011.1)
Căn cứ: QĐ 25/QĐ-BYT ngày 03/01/2014

a) Chụp cộng hưởng từ / can thiệp dưới CHT: chống chỉ định BN đã đặt máy tạo nhịp tim
b) Chụp CT động mạch vành: chống chỉ định suy thận, rung nhĩ (trừ đã hết), hen phế quản

Logic detect:
  - Kiểm tra ICD-10 trong MA_BENH_CHINH / MA_BENH_KT của XML1 (Bảng 1)
  - Kiểm tra MA_DICH_VU trong XML3 (Bảng 3) cùng MA_LK
  - Cross: nếu BN cùng lần khám có cả DVKT bị CCI lẫn bệnh CCI → từ chối DVKT
"""

from collections import defaultdict
from giamdinh.GiamDinhBase import GiamDinhBase, GiamDinhError

# ---------------------------------------------------------------------------
# Mã DVKT thuộc nhóm Chụp CHT (STT 78-144 và 174-179 QĐ 25/QĐ-BYT)
# Prefix mã theo danh mục BHYT: 18.xxx (chẩn đoán hình ảnh) bắt đầu bằng các pattern
# Thực tế cần map đầy đủ từ danh mục; đây là bộ mã mẫu phổ biến
# ---------------------------------------------------------------------------
MA_CHT_PREFIXES = (
    "18.50",   # MRI não, cột sống
    "18.51",
    "18.52",
    "18.53",
    "18.54",
    "18.55",
    "18.56",
    "18.57",
    "18.58",
    "18.59",
    "18.60",
    "18.61",
    "18.62",
    "18.63",
    "18.64",
    "18.65",
    "18.66",
    "18.67",
    "18.68",
    "18.69",
    "18.70",   # Can thiệp dưới CHT
)

# Mã DVKT Chụp CT động mạch vành (STT 47 QĐ 25/QĐ-BYT)
MA_CT_DONG_MACH_VANH = {
    "18.32",   # Chụp CLVT động mạch vành
    "18.32.01",
    "18.32.02",
}

# ICD-10 liên quan máy tạo nhịp
ICD_MAY_TAO_NHIP = {
    "Z95.0",  # máy tạo nhịp tim
    "Z95",
    "T82.1",  # biến chứng thiết bị tim mạch
}

# ICD-10 chống chỉ định CT động mạch vành
ICD_SUY_THAN = {
    "N17", "N18", "N19",        # Suy thận cấp/mạn/không xác định
    "N17.0", "N17.1", "N17.2",
    "N18.1", "N18.2", "N18.3", "N18.4", "N18.5", "N18.9",
}
ICD_RUNG_NHI = {
    "I48",    # Rung nhĩ và cuồng nhĩ
    "I48.0", "I48.1", "I48.2", "I48.9",
}
ICD_HEN_PHE_QUAN = {
    "J45",    # Hen phế quản
    "J45.0", "J45.1", "J45.8", "J45.9",
    "J46",    # Trạng thái hen ác tính
}

CAN_CU_QD25 = "QĐ 25/QĐ-BYT ngày 03/01/2014 (Hướng dẫn QTKT Chẩn đoán hình ảnh & Điện quang can thiệp)"


def _icd_match(icd_val: str, icd_set: set) -> bool:
    """So khớp mã ICD-10 – chấp nhận multi-value phân cách ';'."""
    if not icd_val:
        return False
    codes = [c.strip() for c in str(icd_val).split(";") if c.strip()]
    for code in codes:
        if code in icd_set:
            return True
        # So khớp prefix (N18 match với N18.5)
        for ref in icd_set:
            if code.startswith(ref) or ref.startswith(code):
                return True
    return False


def _is_cht(ma_dich_vu: str) -> bool:
    if not ma_dich_vu:
        return False
    return any(ma_dich_vu.strip().startswith(p) for p in MA_CHT_PREFIXES)


def _is_ct_dmv(ma_dich_vu: str) -> bool:
    if not ma_dich_vu:
        return False
    return ma_dich_vu.strip() in MA_CT_DONG_MACH_VANH


class ChongChiDinh(GiamDinhBase):
    """
    Rule I.1: Từ chối DVKT có chống chỉ định với bệnh lý của BN.
    Mã từ chối: S011.1
    """

    def check(self, all_objects: dict) -> list[GiamDinhError]:
        errors: list[GiamDinhError] = []

        # Lấy thông tin chẩn đoán từ XML1 (Bảng 1 - Tổng hợp KCB)
        # Key: MA_LK → (MA_BENH_CHINH, MA_BENH_KT)
        diag_map: dict[str, tuple] = {}
        for _, rec in self._get_rows(all_objects, "XML1"):
            ma_lk = getattr(rec, "MA_LK", None) or ""
            if ma_lk:
                diag_map[ma_lk] = (
                    getattr(rec, "MA_BENH_CHINH", "") or "",
                    getattr(rec, "MA_BENH_KT", "") or "",
                )

        # Kiểm tra từng dịch vụ trong XML3 (Bảng 3 - DVKT)
        for row_excel, rec in self._get_rows(all_objects, "XML3"):
            ma_lk = getattr(rec, "MA_LK", None) or ""
            ma_dv = getattr(rec, "MA_DICH_VU", None) or ""
            if not ma_lk or not ma_dv:
                continue

            chinh, kt = diag_map.get(ma_lk, ("", ""))

            # ---------------------------------------------------------------
            # a) CHT → chống chỉ định máy tạo nhịp
            # ---------------------------------------------------------------
            if _is_cht(ma_dv):
                if _icd_match(chinh, ICD_MAY_TAO_NHIP) or _icd_match(kt, ICD_MAY_TAO_NHIP):
                    errors.append(GiamDinhError(
                        sheet="XML3",
                        ma_lk=ma_lk,
                        row_excel=row_excel,
                        ma_ly_do="S011.1",
                        mo_ta=(
                            f"Dịch vụ Chụp cộng hưởng từ '{ma_dv}' bị chống chỉ định "
                            f"tuyệt đối: bệnh nhân đã có máy tạo nhịp tim "
                            f"(ICD chính: {chinh} | ICD kèm: {kt}). "
                            "Từ chối thanh toán DVKT."
                        ),
                        can_cu=CAN_CU_QD25,
                        ma_dich_vu=ma_dv,
                    ))

            # ---------------------------------------------------------------
            # b) CT động mạch vành → chống chỉ định suy thận, rung nhĩ, hen
            # ---------------------------------------------------------------
            if _is_ct_dmv(ma_dv):
                cci_reasons = []
                if _icd_match(chinh, ICD_SUY_THAN) or _icd_match(kt, ICD_SUY_THAN):
                    cci_reasons.append("suy thận")
                if _icd_match(chinh, ICD_RUNG_NHI) or _icd_match(kt, ICD_RUNG_NHI):
                    cci_reasons.append("rung nhĩ")
                if _icd_match(chinh, ICD_HEN_PHE_QUAN) or _icd_match(kt, ICD_HEN_PHE_QUAN):
                    cci_reasons.append("hen phế quản")

                if cci_reasons:
                    errors.append(GiamDinhError(
                        sheet="XML3",
                        ma_lk=ma_lk,
                        row_excel=row_excel,
                        ma_ly_do="S011.1",
                        mo_ta=(
                            f"Dịch vụ Chụp CT động mạch vành '{ma_dv}' bị chống chỉ định: "
                            f"{', '.join(cci_reasons)} "
                            f"(ICD chính: {chinh} | ICD kèm: {kt}). "
                            "Lưu ý: suy thận chạy thận ngay sau, rung nhĩ đã điều trị hết "
                            "→ không từ chối. Cần kiểm tra HSBA trước khi xử lý."
                        ),
                        can_cu=CAN_CU_QD25,
                        ma_dich_vu=ma_dv,
                    ))

        return errors