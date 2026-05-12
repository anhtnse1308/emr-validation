from dataclasses import dataclass, field, fields
from typing import Optional, ClassVar, Dict, Any
import re
from model.BHYTBase import BHYTBase

# ===========================================================================
# BẢNG 5 – Diễn biến lâm sàng
# ===========================================================================
 
@dataclass
class Bang5_DienBienLamSang(BHYTBase):
    """Bảng 5. Chỉ tiêu chi tiết diễn biến lâm sàng."""
 
    MA_LK: Optional[str] = None
    STT: Optional[str] = None
    DIEN_BIEN_LS: Optional[str] = None
    GIAI_DOAN_BENH: Optional[str] = None
    HOI_CHAN: Optional[str] = None
    PHAU_THUAT: Optional[str] = None
    THOI_DIEM_DBLS: Optional[str] = None
    NGUOI_THUC_HIEN: Optional[str] = None
    DU_PHONG: Optional[str] = None
 
    _MAX_LEN: ClassVar[Dict[str, Optional[int]]] = {
        "MA_LK": 100, "STT": 10,
        "THOI_DIEM_DBLS": 12, "NGUOI_THUC_HIEN": 255,
    }
    _NUMERIC: ClassVar[set] = {"STT"}
    _DATE12: ClassVar[set] = {"THOI_DIEM_DBLS"}