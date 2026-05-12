from dataclasses import dataclass, field, fields
from typing import Optional, ClassVar, Dict, Any
import re
from model.BHYTBase import BHYTBase

# ===========================================================================
# BẢNG 14 – Giấy hẹn khám lại
# ===========================================================================
 
@dataclass
class Bang14_GiayHenKhamLai(BHYTBase):
    """Bảng 14. Chỉ tiêu dữ liệu giấy hẹn khám lại."""
 
    MA_LK: Optional[str] = None
    SO_GIAYHEN_KL: Optional[str] = None
    MA_CSKCB: Optional[str] = None
    HO_TEN: Optional[str] = None
    NGAY_SINH: Optional[str] = None
    GIOI_TINH: Optional[str] = None
    DIA_CHI: Optional[str] = None
    MA_THE_BHYT: Optional[str] = None
    GT_THE_DEN: Optional[str] = None
    NGAY_VAO: Optional[str] = None
    NGAY_VAO_NOI_TRU: Optional[str] = None
    NGAY_RA: Optional[str] = None
    NGAY_HEN_KL: Optional[str] = None
    CHAN_DOAN_RV: Optional[str] = None
    MA_BENH_CHINH: Optional[str] = None
    MA_BENH_KT: Optional[str] = None
    MA_BENH_YHCT: Optional[str] = None
    MA_DOITUONG_KCB: Optional[str] = None
    MA_BAC_SI: Optional[str] = None
    MA_TTDV: Optional[str] = None           # [đổi -> Chuỗi, size -> 255]
    NGAY_CT: Optional[str] = None
    DU_PHONG: Optional[str] = None
 
    _MAX_LEN: ClassVar[Dict[str, Optional[int]]] = {
        "MA_LK": 100, "SO_GIAYHEN_KL": 50, "MA_CSKCB": 5,
        "HO_TEN": 255, "NGAY_SINH": 12, "GIOI_TINH": 1,
        "DIA_CHI": 1024, "NGAY_VAO": 12, "NGAY_VAO_NOI_TRU": 12,
        "NGAY_RA": 12, "NGAY_HEN_KL": 8,
        "MA_BENH_CHINH": 7, "MA_BENH_KT": 100, "MA_BENH_YHCT": 255,
        "MA_DOITUONG_KCB": 4, "MA_BAC_SI": 255, "MA_TTDV": 255,
        "NGAY_CT": 8,
    }
    _NUMERIC: ClassVar[set] = {"GIOI_TINH"}
    _DATE12: ClassVar[set] = {"NGAY_SINH", "NGAY_VAO", "NGAY_VAO_NOI_TRU", "NGAY_RA"}
    _DATE8: ClassVar[set] = {"NGAY_HEN_KL", "NGAY_CT"}