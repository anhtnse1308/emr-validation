from dataclasses import dataclass, field, fields
from typing import Optional, ClassVar, Dict, Any
import re
from model.BHYTBase import BHYTBase

# ===========================================================================
# BẢNG 1 – Tổng hợp KCB
# ===========================================================================

@dataclass
class Bang1_TongHop(BHYTBase):
    """Bảng 1. Chỉ tiêu tổng hợp khám bệnh, chữa bệnh."""
 
    MA_LK: Optional[str] = None
    STT: Optional[str] = None
    MA_BN: Optional[str] = None
    HO_TEN: Optional[str] = None
    SO_CCCD: Optional[str] = None           # [đổi -> Chuỗi, size=n]
    NGAY_SINH: Optional[str] = None
    GIOI_TINH: Optional[str] = None
    NHOM_MAU: Optional[str] = None
    MA_QUOCTICH: Optional[str] = None       # [đổi -> Chuỗi]
    MA_DANTOC: Optional[str] = None         # [đổi -> Chuỗi]
    MA_NGHE_NGHIEP: Optional[str] = None    # [đổi -> Chuỗi]
    DIA_CHI: Optional[str] = None
    MATINH_CU_TRU: Optional[str] = None
    MAHUYEN_CU_TRU: Optional[str] = None
    MAXA_CU_TRU: Optional[str] = None
    DIEN_THOAI: Optional[str] = None        # [đổi -> Chuỗi]
    MA_THE_BHYT: Optional[str] = None       # [size=n]
    MA_DKBD: Optional[str] = None           # [size=n]
    GT_THE_TU: Optional[str] = None         # [size=n, multi-value ";"]
    GT_THE_DEN: Optional[str] = None        # [size=n, multi-value ";"]
    NGAY_MIEN_CCT: Optional[str] = None     # [8 ký tự yyyymmdd hoặc 12 ký tự yyyymmddHHMM]
    LY_DO_VV: Optional[str] = None
    LY_DO_VNT: Optional[str] = None
    MA_LY_DO_VNT: Optional[str] = None
    CHAN_DOAN_VAO: Optional[str] = None
    CHAN_DOAN_RV: Optional[str] = None
    MA_BENH_CHINH: Optional[str] = None
    MA_BENH_KT: Optional[str] = None
    MA_BENH_YHCT: Optional[str] = None      # [size -> 150]
    MA_PTTT_QT: Optional[str] = None
    MA_DOITUONG_KCB: Optional[str] = None   # [size -> 4]
    MA_NOI_DI: Optional[str] = None
    MA_NOI_DEN: Optional[str] = None
    MA_TAI_NAN: Optional[str] = None
    NGAY_VAO: Optional[str] = None
    NGAY_VAO_NOI_TRU: Optional[str] = None
    NGAY_RA: Optional[str] = None
    GIAY_CHUYEN_TUYEN: Optional[str] = None
    SO_NGAY_DTRI: Optional[str] = None
    PP_DIEU_TRI: Optional[str] = None
    KET_QUA_DTRI: Optional[str] = None
    MA_LOAI_RV: Optional[str] = None
    GHI_CHU: Optional[str] = None
    NGAY_TTOAN: Optional[str] = None
    T_THUOC: Optional[str] = None
    T_VTYT: Optional[str] = None
    T_TONGCHI_BV: Optional[str] = None
    T_TONGCHI_BH: Optional[str] = None
    T_BNTT: Optional[str] = None
    T_BNCCT: Optional[str] = None
    T_BHTT: Optional[str] = None
    T_NGUONKHAC: Optional[str] = None
    T_BHTT_GDV: Optional[str] = None
    NAM_QT: Optional[str] = None
    THANG_QT: Optional[str] = None
    MA_LOAI_KCB: Optional[str] = None       # [đổi -> Chuỗi]
    MA_KHOA: Optional[str] = None
    MA_CSKCB: Optional[str] = None
    MA_KHUVUC: Optional[str] = None
    CAN_NANG: Optional[str] = None
    CAN_NANG_CON: Optional[str] = None
    NAM_NAM_LIEN_TUC: Optional[str] = None
    NGAY_TAI_KHAM: Optional[str] = None
    MA_HSBA: Optional[str] = None
    MA_TTDV: Optional[str] = None           # [size -> 255]
    DU_PHONG: Optional[str] = None

    _MAX_LEN: ClassVar[Dict[str, Optional[int]]] = {
        "MA_LK": 100, "STT": 10, "MA_BN": 100, "HO_TEN": 255,
        # SO_CCCD: size=n → không giới hạn, bỏ khỏi _MAX_LEN
        "NGAY_SINH": 12, "GIOI_TINH": 1, "NHOM_MAU": 5,
        "MA_QUOCTICH": 3, "MA_DANTOC": 2, "MA_NGHE_NGHIEP": 2,
        "DIA_CHI": 1024, "MATINH_CU_TRU": 3, "MAHUYEN_CU_TRU": 3,
        "MAXA_CU_TRU": 5, "DIEN_THOAI": 15,
        # MA_THE_BHYT, MA_DKBD, GT_THE_TU, GT_THE_DEN: size=n → bỏ
        "MA_LY_DO_VNT": 5,
        "MA_BENH_CHINH": 7, "MA_BENH_KT": 100, "MA_BENH_YHCT": 150,
        "MA_PTTT_QT": 125, "MA_DOITUONG_KCB": 4,
        "MA_NOI_DI": 5, "MA_NOI_DEN": 5, "MA_TAI_NAN": 1,
        "NGAY_VAO": 12, "NGAY_VAO_NOI_TRU": 12, "NGAY_RA": 12,
        "GIAY_CHUYEN_TUYEN": 50, "SO_NGAY_DTRI": 3,
        "KET_QUA_DTRI": 1, "MA_LOAI_RV": 1,
        "NGAY_TTOAN": 12,
        "T_THUOC": 15, "T_VTYT": 15, "T_TONGCHI_BV": 15,
        "T_TONGCHI_BH": 15, "T_BNTT": 15, "T_BNCCT": 15,
        "T_BHTT": 15, "T_NGUONKHAC": 15, "T_BHTT_GDV": 15,
        "NAM_QT": 4, "THANG_QT": 2,
        "MA_LOAI_KCB": 2, "MA_KHOA": 50, "MA_CSKCB": 5,
        "MA_KHUVUC": 2, "CAN_NANG": 6, "CAN_NANG_CON": 100,
        "NAM_NAM_LIEN_TUC": 8, "NGAY_TAI_KHAM": 50,
        "MA_HSBA": 100, "MA_TTDV": 255,
    }
    _NUMERIC: ClassVar[set] = {
        "STT", "MA_TAI_NAN", "SO_NGAY_DTRI", "KET_QUA_DTRI", "MA_LOAI_RV",
        "T_THUOC", "T_VTYT", "T_TONGCHI_BV", "T_TONGCHI_BH",
        "T_BNTT", "T_BNCCT", "T_BHTT", "T_NGUONKHAC", "T_BHTT_GDV",
        "NAM_QT", "THANG_QT",
    }
    _DATE12: ClassVar[set] = {
        "NGAY_SINH", "NGAY_VAO", "NGAY_VAO_NOI_TRU",
        "NGAY_RA", "NGAY_TTOAN",
    }
    _DATE8: ClassVar[set] = {"GT_THE_TU", "GT_THE_DEN", "NAM_NAM_LIEN_TUC", "NGAY_TAI_KHAM"}

    _REQUIRED: ClassVar[set] = {"MA_LK"}

    def validate(self) -> list[str]:
        errors = super().validate()

        # ----------------------------------------------------------------
        # GIOI_TINH: 1/2/3
        # ----------------------------------------------------------------
        if self.GIOI_TINH and self.GIOI_TINH not in ("1", "2", "3"):
            errors.append(
                f"[GIOI_TINH] Giá trị không hợp lệ: '{self.GIOI_TINH}' (cần 1/2/3)"
            )

        # ----------------------------------------------------------------
        # KET_QUA_DTRI: 1-8 (QĐ 4750 bổ sung mã 8: Tử vong ngoại viện)
        # ----------------------------------------------------------------
        if self.KET_QUA_DTRI and self.KET_QUA_DTRI not in [str(i) for i in range(1, 9)]:
            errors.append(
                f"[KET_QUA_DTRI] Giá trị không hợp lệ: '{self.KET_QUA_DTRI}' "
                f"(cần 1-8; mã 8 = Tử vong ngoại viện theo QĐ 4750)"
            )

        # ----------------------------------------------------------------
        # MA_LOAI_RV: 1-5
        # ----------------------------------------------------------------
        if self.MA_LOAI_RV and self.MA_LOAI_RV not in [str(i) for i in range(1, 6)]:
            errors.append(
                f"[MA_LOAI_RV] Giá trị không hợp lệ: '{self.MA_LOAI_RV}' (cần 1-5)"
            )

        # ----------------------------------------------------------------
        # NGAY_MIEN_CCT: chấp nhận cả yyyymmdd (8 số) lẫn yyyymmddHHMM (12 số)
        # Lý do: QĐ 130 cho phép ghi 8 ký tự khi đã có giấy miễn CCT,
        #        12 ký tự khi chưa có giấy (xác định theo thời điểm cụ thể)
        # ----------------------------------------------------------------
        if self.NGAY_MIEN_CCT:
            val = str(self.NGAY_MIEN_CCT).strip()
            if not (re.fullmatch(r"\d{8}", val) or re.fullmatch(r"\d{12}", val)):
                errors.append(
                    f"[NGAY_MIEN_CCT] Sai định dạng – cần yyyymmdd (8 số) hoặc "
                    f"yyyymmddHHMM (12 số), nhận: '{val}'"
                )

        # ----------------------------------------------------------------
        # MA_BENH_CHINH: chỉ 1 mã ICD-10
        # ----------------------------------------------------------------
        if self.MA_BENH_CHINH and ";" in self.MA_BENH_CHINH:
            errors.append(
                f"[MA_BENH_CHINH] Chỉ được 1 mã ICD-10, nhận: '{self.MA_BENH_CHINH}'"
            )

        # ----------------------------------------------------------------
        # MA_LOAI_KCB: 2 ký tự số (01, 02, ... 09)
        # ----------------------------------------------------------------
        if self.MA_LOAI_KCB and not re.fullmatch(r"\d{2}", self.MA_LOAI_KCB):
            errors.append(
                f"[MA_LOAI_KCB] Cần 2 ký tự số (VD: 01, 05), nhận: '{self.MA_LOAI_KCB}'"
            )

        # ----------------------------------------------------------------
        # MA_CSKCB: đúng 5 ký tự
        # ----------------------------------------------------------------
        if self.MA_CSKCB and len(self.MA_CSKCB) != 5:
            errors.append(
                f"[MA_CSKCB] Cần 5 ký tự, nhận: '{self.MA_CSKCB}'"
            )

        # ----------------------------------------------------------------
        # MA_KHUVUC: chỉ chấp nhận K1 / K2 / K3
        # ----------------------------------------------------------------
        if self.MA_KHUVUC and self.MA_KHUVUC not in ("K1", "K2", "K3"):
            errors.append(
                f"[MA_KHUVUC] Giá trị không hợp lệ: '{self.MA_KHUVUC}' (cần K1/K2/K3)"
            )

        # ----------------------------------------------------------------
        # _REQUIRED
        # ----------------------------------------------------------------
        for f in fields(self):
            name = f.name
            val = getattr(self, name)
            val_str = "" if val is None else str(val).strip()
            if name in self._REQUIRED and not val_str:
                errors.append(f"[{name}] Bắt buộc nhập")

        return errors