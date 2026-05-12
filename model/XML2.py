from dataclasses import dataclass, field, fields
from typing import Optional, ClassVar, Dict, Any
import re
from model.BHYTBase import BHYTBase

# ===========================================================================
# BẢNG 2 – Chi tiết thuốc
# ===========================================================================

@dataclass
class Bang2_Thuoc(BHYTBase):
    """Bảng 2. Chỉ tiêu chi tiết thuốc."""

    MA_LK: Optional[str] = None
    STT: Optional[str] = None
    MA_THUOC: Optional[str] = None
    MA_PP_CHEBIEN: Optional[str] = None
    MA_CSKCB_THUOC: Optional[str] = None
    MA_NHOM: Optional[str] = None
    TEN_THUOC: Optional[str] = None
    DON_VI_TINH: Optional[str] = None
    HAM_LUONG: Optional[str] = None
    DUONG_DUNG: Optional[str] = None
    DANG_BAO_CHE: Optional[str] = None
    LIEU_DUNG: Optional[str] = None
    CACH_DUNG: Optional[str] = None
    SO_DANG_KY: Optional[str] = None
    TT_THAU: Optional[str] = None
    PHAM_VI: Optional[str] = None
    TYLE_TT_BH: Optional[str] = None
    SO_LUONG: Optional[str] = None
    DON_GIA: Optional[str] = None
    THANH_TIEN_BV: Optional[str] = None
    THANH_TIEN_BH: Optional[str] = None
    T_NGUONKHAC_NSNN: Optional[str] = None
    T_NGUONKHAC_VTNN: Optional[str] = None
    T_NGUONKHAC_VTTN: Optional[str] = None
    T_NGUONKHAC_CL: Optional[str] = None
    T_NGUONKHAC: Optional[str] = None
    MUC_HUONG: Optional[str] = None
    T_BNTT: Optional[str] = None
    T_BNCCT: Optional[str] = None
    T_BHTT: Optional[str] = None
    MA_KHOA: Optional[str] = None           # [size -> 50]
    MA_BAC_SI: Optional[str] = None
    MA_DICH_VU: Optional[str] = None
    NGAY_YL: Optional[str] = None
    NGAY_TH_YL: Optional[str] = None
    MA_PTTT: Optional[str] = None
    NGUON_CTRA: Optional[str] = None
    VET_THUONG_TP: Optional[str] = None
    DU_PHONG: Optional[str] = None

    _MAX_LEN: ClassVar[Dict[str, Optional[int]]] = {
        "MA_LK": 100, "STT": 10, "MA_THUOC": 255, "MA_PP_CHEBIEN": 255,
        "MA_CSKCB_THUOC": 10, "MA_NHOM": 2, "TEN_THUOC": 1024,
        "DON_VI_TINH": 50, "HAM_LUONG": 1024, "DUONG_DUNG": 4,
        "DANG_BAO_CHE": 1024, "LIEU_DUNG": 1024, "CACH_DUNG": 1024,
        "SO_DANG_KY": 255, "TT_THAU": 50, "PHAM_VI": 1,
        "TYLE_TT_BH": 3, "SO_LUONG": 10, "DON_GIA": 15,
        "THANH_TIEN_BV": 15, "THANH_TIEN_BH": 15,
        "T_NGUONKHAC_NSNN": 15, "T_NGUONKHAC_VTNN": 15,
        "T_NGUONKHAC_VTTN": 15, "T_NGUONKHAC_CL": 15, "T_NGUONKHAC": 15,
        "MUC_HUONG": 3, "T_BNTT": 15, "T_BNCCT": 15, "T_BHTT": 15,
        "MA_KHOA": 50, "MA_BAC_SI": 255, "MA_DICH_VU": 255,
        "NGAY_YL": 12, "NGAY_TH_YL": 12,
        "MA_PTTT": 1, "NGUON_CTRA": 1, "VET_THUONG_TP": 1,
    }
    _NUMERIC: ClassVar[set] = {
        "STT", "MA_NHOM", "PHAM_VI", "TYLE_TT_BH", "SO_LUONG",
        "DON_GIA", "THANH_TIEN_BV", "THANH_TIEN_BH",
        "T_NGUONKHAC_NSNN", "T_NGUONKHAC_VTNN", "T_NGUONKHAC_VTTN",
        "T_NGUONKHAC_CL", "T_NGUONKHAC", "MUC_HUONG",
        "T_BNTT", "T_BNCCT", "T_BHTT",
        "MA_PTTT", "NGUON_CTRA", "VET_THUONG_TP",
    }
    _DATE12: ClassVar[set] = {"NGAY_YL", "NGAY_TH_YL"}

    def validate(self) -> list[str]:
        errors = super().validate()

        # ----------------------------------------------------------------
        # PHAM_VI: 1 = BHYT thanh toán / 2 = BN tự trả / 3 = QĐ, CA, CY
        # ----------------------------------------------------------------
        if self.PHAM_VI and self.PHAM_VI not in ("1", "2", "3"):
            errors.append(
                f"[PHAM_VI] Giá trị không hợp lệ: '{self.PHAM_VI}' "
                f"(cần 1=BHYT thanh toán / 2=BN tự trả / 3=QĐ,CA,CY)"
            )

        # ----------------------------------------------------------------
        # TYLE_TT_BH: số nguyên 0-100
        # ----------------------------------------------------------------
        if self.TYLE_TT_BH:
            try:
                v = int(self.TYLE_TT_BH)
                if not (0 <= v <= 100):
                    errors.append(
                        f"[TYLE_TT_BH] Ngoài khoảng hợp lệ: '{self.TYLE_TT_BH}' (cần 0-100)"
                    )
            except ValueError:
                pass  # đã được bắt ở _NUMERIC

        # ----------------------------------------------------------------
        # MUC_HUONG: số nguyên 0-100
        # ----------------------------------------------------------------
        if self.MUC_HUONG:
            try:
                v = int(self.MUC_HUONG)
                if not (0 <= v <= 100):
                    errors.append(
                        f"[MUC_HUONG] Ngoài khoảng hợp lệ: '{self.MUC_HUONG}' (cần 0-100)"
                    )
            except ValueError:
                pass  # đã được bắt ở _NUMERIC

        # ----------------------------------------------------------------
        # MA_PTTT: 1=Phí dịch vụ / 2=Định suất / 3=DRG
        # ----------------------------------------------------------------
        if self.MA_PTTT and self.MA_PTTT not in ("1", "2", "3"):
            errors.append(
                f"[MA_PTTT] Giá trị không hợp lệ: '{self.MA_PTTT}' "
                f"(cần 1=Phí DV / 2=Định suất / 3=DRG)"
            )

        # ----------------------------------------------------------------
        # NGUON_CTRA: 1=BHYT / 2=Dự án,viện trợ / 3=CTMTQG / 4=Khác
        # ----------------------------------------------------------------
        if self.NGUON_CTRA and self.NGUON_CTRA not in ("1", "2", "3", "4"):
            errors.append(
                f"[NGUON_CTRA] Giá trị không hợp lệ: '{self.NGUON_CTRA}' "
                f"(cần 1=BHYT / 2=Dự án,viện trợ / 3=CTMTQG / 4=Khác)"
            )

        # ----------------------------------------------------------------
        # VET_THUONG_TP: chỉ hợp lệ khi = "1" hoặc để trống
        # ----------------------------------------------------------------
        if self.VET_THUONG_TP and self.VET_THUONG_TP != "1":
            errors.append(
                f"[VET_THUONG_TP] Giá trị không hợp lệ: '{self.VET_THUONG_TP}' "
                f"(chỉ ghi '1' nếu là vết thương/bệnh tái phát của thương binh, để trống nếu không)"
            )

        return errors