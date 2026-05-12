from dataclasses import dataclass, field, fields
from typing import Optional, ClassVar, Dict, Any
import re
from model.BHYTBase import BHYTBase

# ===========================================================================
# BẢNG 10 – Giấy nghỉ dưỡng thai
# ===========================================================================
 
@dataclass
class Bang10_GiayNghiDuongThai(BHYTBase):
    """Bảng 10. Chỉ tiêu dữ liệu giấy chứng nhận nghỉ dưỡng thai."""
 
    MA_LK: Optional[str] = None
    SO_SERI: Optional[str] = None
    SO_CT: Optional[str] = None
    SO_NGAY: Optional[str] = None
    DON_VI: Optional[str] = None
    CHAN_DOAN_RV: Optional[str] = None
    TU_NGAY: Optional[str] = None
    DEN_NGAY: Optional[str] = None
    MA_TTDV: Optional[str] = None           # [đổi -> Chuỗi, size -> 255]
    TEN_BS: Optional[str] = None
    MA_BS: Optional[str] = None             # [size -> 255]
    NGAY_CT: Optional[str] = None
    DU_PHONG: Optional[str] = None
 
    _MAX_LEN: ClassVar[Dict[str, Optional[int]]] = {
        "MA_LK": 100, "SO_SERI": 200, "SO_CT": 200, "SO_NGAY": 3,
        "DON_VI": 1024, "TU_NGAY": 8, "DEN_NGAY": 8,
        "MA_TTDV": 255, "TEN_BS": 255, "MA_BS": 255, "NGAY_CT": 8,
    }
    _NUMERIC: ClassVar[set] = {"SO_NGAY"}
    _DATE8: ClassVar[set] = {"TU_NGAY", "DEN_NGAY", "NGAY_CT"}