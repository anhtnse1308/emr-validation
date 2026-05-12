from dataclasses import dataclass, field, fields
from typing import Optional, ClassVar, Dict, Any
import re
from model.BHYTBase import BHYTBase

# ===========================================================================
# BẢNG 9 – Giấy chứng sinh
# ===========================================================================
 
@dataclass
class Bang9_GiayChungSinh(BHYTBase):
    """Bảng 9. Chỉ tiêu dữ liệu giấy chứng sinh."""
 
    MA_LK: Optional[str] = None
    MA_BHXH_NND: Optional[str] = None       # [đổi -> Chuỗi]
    MA_THE_NND: Optional[str] = None
    HO_TEN_NND: Optional[str] = None
    NGAYSINH_NND: Optional[str] = None
    MA_DANTOC_NND: Optional[str] = None     # [đổi -> Chuỗi]
    SO_CCCD_NND: Optional[str] = None       # [đổi -> Chuỗi]
    NGAYCAP_CCCD_NND: Optional[str] = None
    NOICAP_CCCD_NND: Optional[str] = None
    NOI_CU_TRU_NND: Optional[str] = None
    MA_QUOCTICH: Optional[str] = None       # [đổi -> Chuỗi]
    MATINH_CU_TRU: Optional[str] = None
    MAHUYEN_CU_TRU: Optional[str] = None
    MAXA_CU_TRU: Optional[str] = None
    HO_TEN_CHA: Optional[str] = None
    MA_THE_TAM: Optional[str] = None
    HO_TEN_CON: Optional[str] = None
    GIOI_TINH_CON: Optional[str] = None
    SO_CON: Optional[str] = None
    LAN_SINH: Optional[str] = None
    SO_CON_SONG: Optional[str] = None
    CAN_NANG_CON: Optional[str] = None
    NGAY_SINH_CON: Optional[str] = None
    NOI_SINH_CON: Optional[str] = None
    TINH_TRANG_CON: Optional[str] = None
    SINHCON_PHAUTHUAT: Optional[str] = None
    GHI_CHU: Optional[str] = None
    NGUOI_DO_DE: Optional[str] = None
    NGUOI_GHI_PHIEU: Optional[str] = None
    NGAY_CT: Optional[str] = None
    SO: Optional[str] = None
    QUYEN_SO: Optional[str] = None
    MA_TTDV: Optional[str] = None           # [đổi -> Chuỗi, size -> 255]
    DU_PHONG: Optional[str] = None
 
    _MAX_LEN: ClassVar[Dict[str, Optional[int]]] = {
        "MA_LK": 100, "MA_BHXH_NND": 10, "MA_THE_NND": 15, "HO_TEN_NND": 255,
        "NGAYSINH_NND": 8, "MA_DANTOC_NND": 2,
        "NGAYCAP_CCCD_NND": 8, "NOICAP_CCCD_NND": 1024, "NOI_CU_TRU_NND": 1024,
        "MA_QUOCTICH": 3, "MATINH_CU_TRU": 3, "MAHUYEN_CU_TRU": 3,
        "MAXA_CU_TRU": 5, "HO_TEN_CHA": 255, "MA_THE_TAM": 15,
        "HO_TEN_CON": 255, "GIOI_TINH_CON": 1, "SO_CON": 2,
        "LAN_SINH": 2, "SO_CON_SONG": 2, "CAN_NANG_CON": 10,
        "NGAY_SINH_CON": 12, "NOI_SINH_CON": 1024,
        "SINHCON_PHAUTHUAT": 1,
        "NGUOI_DO_DE": 255, "NGUOI_GHI_PHIEU": 255,
        "NGAY_CT": 8, "SO": 200, "QUYEN_SO": 200, "MA_TTDV": 255,
    }
    _NUMERIC: ClassVar[set] = {
        "GIOI_TINH_CON", "SO_CON", "LAN_SINH", "SO_CON_SONG",
        "CAN_NANG_CON", "SINHCON_PHAUTHUAT",
    }
    _DATE12: ClassVar[set] = {"NGAY_SINH_CON"}
    _DATE8: ClassVar[set] = {"NGAYSINH_NND", "NGAYCAP_CCCD_NND", "NGAY_CT"}