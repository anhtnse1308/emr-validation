"""
Rule I.1 – Chống chỉ định kỹ thuật (mã từ chối S011.1)
Căn cứ: QĐ 25/QĐ-BYT ngày 03/01/2014

a) Chụp cộng hưởng từ / can thiệp dưới CHT: chống chỉ định BN đã đặt máy tạo nhịp tim
b) Chụp CT động mạch vành: chống chỉ định suy thận, rung nhĩ (trừ đã hết), hen phế quản
"""

from giamdinh.GiamDinhBase import GiamDinhBase, GiamDinhError
from giamdinh.ICDHelper import ICDHelper

# ---------------------------------------------------------------------------
# Mã DVKT
# ---------------------------------------------------------------------------
MA_CHT_PREFIXES = (
    "18.50", "18.51", "18.52", "18.53", "18.54", "18.55",
    "18.56", "18.57", "18.58", "18.59", "18.60", "18.61",
    "18.62", "18.63", "18.64", "18.65", "18.66", "18.67",
    "18.68", "18.69", "18.70",
)

MA_CT_DONG_MACH_VANH = {"18.32", "18.32.01", "18.32.02"}

# ---------------------------------------------------------------------------
# ICD-10
# ---------------------------------------------------------------------------
ICD_MAY_TAO_NHIP  = {"Z95.0", "Z95", "T82.1"}
ICD_SUY_THAN      = {"N17", "N18", "N19"}
ICD_RUNG_NHI      = {"I48"}
ICD_HEN_PHE_QUAN  = {"J45", "J46"}

CAN_CU = "QĐ 25/QĐ-BYT ngày 03/01/2014 (QTKT Chẩn đoán hình ảnh & Điện quang can thiệp)"


def _is_cht(ma_dv: str) -> bool:
    return any(ma_dv.strip().startswith(p) for p in MA_CHT_PREFIXES)


def _is_ct_dmv(ma_dv: str) -> bool:
    return ma_dv.strip() in MA_CT_DONG_MACH_VANH


class ChongChiDinh(GiamDinhBase):
    """Rule I.1: DVKT có chống chỉ định với bệnh lý của BN. Mã: S011.1"""

    def check(self, all_objects: dict) -> list[GiamDinhError]:
        errors: list[GiamDinhError] = []

        # MA_LK → ICDHelper
        icd_map: dict[str, ICDHelper] = {}
        for _, rec in self._get_rows(all_objects, "XML1"):
            ma_lk = getattr(rec, "MA_LK", None) or ""
            if ma_lk:
                icd_map[ma_lk] = ICDHelper.from_record(rec)

        for row_excel, rec in self._get_rows(all_objects, "XML3"):
            ma_lk = getattr(rec, "MA_LK", None) or ""
            ma_dv = (getattr(rec, "MA_DICH_VU", None) or "").strip()
            if not ma_lk or not ma_dv:
                continue

            icd = icd_map.get(ma_lk)
            if not icd:
                continue

            # a) CHT → máy tạo nhịp
            if _is_cht(ma_dv) and icd.has_any(ICD_MAY_TAO_NHIP):
                errors.append(GiamDinhError(
                    sheet="XML3", ma_lk=ma_lk, row_excel=row_excel,
                    ma_ly_do="S011.1",
                    mo_ta=(
                        f"Chụp CHT '{ma_dv}' chống chỉ định tuyệt đối: "
                        f"BN đã đặt máy tạo nhịp tim. {icd}"
                    ),
                    can_cu=CAN_CU, ma_dich_vu=ma_dv,
                ))

            # b) CT ĐMV → suy thận / rung nhĩ / hen
            if _is_ct_dmv(ma_dv):
                reasons = []
                if icd.has_any(ICD_SUY_THAN):      reasons.append("suy thận")
                if icd.has_any(ICD_RUNG_NHI):      reasons.append("rung nhĩ")
                if icd.has_any(ICD_HEN_PHE_QUAN):  reasons.append("hen phế quản")
                if reasons:
                    errors.append(GiamDinhError(
                        sheet="XML3", ma_lk=ma_lk, row_excel=row_excel,
                        ma_ly_do="S011.1",
                        mo_ta=(
                            f"Chụp CT ĐMV '{ma_dv}' chống chỉ định: "
                            f"{', '.join(reasons)}. {icd}. "
                            "Lưu ý ngoại lệ: suy thận chạy thận ngay sau / "
                            "rung nhĩ đã điều trị hết → cần kiểm tra HSBA."
                        ),
                        can_cu=CAN_CU, ma_dich_vu=ma_dv,
                    ))

        return errors