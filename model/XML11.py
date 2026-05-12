from dataclasses import dataclass, field, fields
from typing import Optional, ClassVar, Dict, Any
import re
from model.BHYTBase import BHYTBase

# ===========================================================================
# BẢNG 11 – Giấy nghỉ hưởng BHXH
# ===========================================================================
 
@dataclass
class Bang11_GiayNghiHuongBHXH(BHYTBase):
    """Bảng 11. Chỉ tiêu dữ liệu giấy chứng nhận nghỉ việc hưởng BHXH."""
 
    MA_LK: Optional[str] = None
    SO_CT: Optional[str] = None
    SO_SERI: Optional[str] = None
    SO_KCB: Optional[str] = None
    DON_VI: Optional[str] = None
    MA_BHXH: Optional[str] = None           # [đổi -> Chuỗi]
    MA_THE_BHYT: Optional[str] = None
    CHAN_DOAN_RV: Optional[str] = None
    PP_DIEUTRI: Optional[str] = None
    MA_DINH_CHI_THAI: Optional[str] = None
    NGUYENNHAN_DINHCHI: Optional[str] = None
    TUOI_THAI: Optional[str] = None
    SO_NGAY_NGHI: Optional[str] = None
    TU_NGAY: Optional[str] = None
    DEN_NGAY: Optional[str] = None
    HO_TEN_CHA: Optional[str] = None
    HO_TEN_ME: Optional[str] = None
    MA_TTDV: Optional[str] = None           # [đổi -> Chuỗi, size -> 255]
    MA_BS: Optional[str] = None             # [size -> 255]
    NGAY_CT: Optional[str] = None
    MA_THE_TAM: Optional[str] = None
    MAU_SO: Optional[str] = None
    DU_PHONG: Optional[str] = None
 
    _MAX_LEN: ClassVar[Dict[str, Optional[int]]] = {
        "MA_LK": 100, "SO_CT": 200, "SO_SERI": 200, "SO_KCB": 200,
        "DON_VI": 1024, "MA_BHXH": 10,
        "MA_DINH_CHI_THAI": 1, "TUOI_THAI": 2, "SO_NGAY_NGHI": 3,
        "TU_NGAY": 8, "DEN_NGAY": 8,
        "HO_TEN_CHA": 255, "HO_TEN_ME": 255,
        "MA_TTDV": 255, "MA_BS": 255, "NGAY_CT": 8,
        "MA_THE_TAM": 15, "MAU_SO": 5,
    }
    _NUMERIC: ClassVar[set] = {"MA_DINH_CHI_THAI", "TUOI_THAI", "SO_NGAY_NGHI"}
    _DATE8: ClassVar[set] = {"TU_NGAY", "DEN_NGAY", "NGAY_CT"}