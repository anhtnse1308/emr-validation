from dataclasses import dataclass, field, fields
from typing import Optional, ClassVar, Dict, Any
import re
from model.BHYTBase import BHYTBase

# ===========================================================================
# BẢNG 7 – Giấy ra viện
# ===========================================================================
 
@dataclass
class Bang7_GiayRaVien(BHYTBase):
    """Bảng 7. Chỉ tiêu dữ liệu giấy ra viện."""
 
    MA_LK: Optional[str] = None
    SO_LUU_TRU: Optional[str] = None
    MA_YTE: Optional[str] = None
    MA_KHOA_RV: Optional[str] = None
    NGAY_VAO: Optional[str] = None
    NGAY_RA: Optional[str] = None
    MA_DINH_CHI_THAI: Optional[str] = None
    NGUYENNHAN_DINHCHI: Optional[str] = None
    THOIGIAN_DINHCHI: Optional[str] = None
    TUOI_THAI: Optional[str] = None
    CHAN_DOAN_RV: Optional[str] = None
    PP_DIEUTRI: Optional[str] = None
    GHI_CHU: Optional[str] = None
    MA_TTDV: Optional[str] = None           # [đổi -> Chuỗi, size -> 255]
    MA_BS: Optional[str] = None             # [size -> 255]
    TEN_BS: Optional[str] = None
    NGAY_CT: Optional[str] = None
    MA_CHA: Optional[str] = None
    MA_ME: Optional[str] = None
    MA_THE_TAM: Optional[str] = None
    HO_TEN_CHA: Optional[str] = None
    HO_TEN_ME: Optional[str] = None
    SO_NGAY_NGHI: Optional[str] = None     # [size -> 3]
    NGOAITRU_TUNGAY: Optional[str] = None
    NGOAITRU_DENNGAY: Optional[str] = None
    DU_PHONG: Optional[str] = None
 
    _MAX_LEN: ClassVar[Dict[str, Optional[int]]] = {
        "MA_LK": 100, "SO_LUU_TRU": 200, "MA_YTE": 200, "MA_KHOA_RV": 200,
        "NGAY_VAO": 12, "NGAY_RA": 12, "MA_DINH_CHI_THAI": 1,
        "THOIGIAN_DINHCHI": 12, "TUOI_THAI": 2, "CHAN_DOAN_RV": 1500,
        "GHI_CHU": 1500, "MA_TTDV": 255, "MA_BS": 255, "TEN_BS": 255,
        "NGAY_CT": 8, "MA_CHA": 10, "MA_ME": 10, "MA_THE_TAM": 15,
        "HO_TEN_CHA": 255, "HO_TEN_ME": 255, "SO_NGAY_NGHI": 3,
        "NGOAITRU_TUNGAY": 8, "NGOAITRU_DENNGAY": 8,
    }
    _NUMERIC: ClassVar[set] = {"MA_DINH_CHI_THAI", "TUOI_THAI", "SO_NGAY_NGHI"}
    _DATE12: ClassVar[set] = {"NGAY_VAO", "NGAY_RA", "THOIGIAN_DINHCHI"}
    _DATE8: ClassVar[set] = {"NGAY_CT", "NGOAITRU_TUNGAY", "NGOAITRU_DENNGAY"}