from dataclasses import dataclass, field, fields
from typing import Optional, ClassVar, Dict, Any
import re
from model.BHYTBase import BHYTBase

# ===========================================================================
# BẢNG 8 – Tóm tắt HSBA
# ===========================================================================
 
@dataclass
class Bang8_TomTatHSBA(BHYTBase):
    """Bảng 8. Chỉ tiêu dữ liệu tóm tắt hồ sơ bệnh án."""
 
    MA_LK: Optional[str] = None
    MA_LOAI_KCB: Optional[str] = None       # [đổi -> Chuỗi]
    HO_TEN_CHA: Optional[str] = None
    HO_TEN_ME: Optional[str] = None
    NGUOI_GIAM_HO: Optional[str] = None
    DON_VI: Optional[str] = None
    NGAY_VAO: Optional[str] = None
    NGAY_RA: Optional[str] = None
    CHAN_DOAN_VAO: Optional[str] = None
    CHAN_DOAN_RV: Optional[str] = None
    QT_BENHLY: Optional[str] = None
    TOMTAT_KQ: Optional[str] = None
    PP_DIEUTRI: Optional[str] = None
    NGAY_SINHCON: Optional[str] = None
    NGAY_CONCHET: Optional[str] = None
    SO_CONCHET: Optional[str] = None
    KET_QUA_DTRI: Optional[str] = None
    GHI_CHU: Optional[str] = None
    MA_TTDV: Optional[str] = None           # [đổi -> Chuỗi, size -> 255]
    NGAY_CT: Optional[str] = None
    MA_THE_TAM: Optional[str] = None
    DU_PHONG: Optional[str] = None
 
    _MAX_LEN: ClassVar[Dict[str, Optional[int]]] = {
        "MA_LK": 100, "MA_LOAI_KCB": 2,
        "HO_TEN_CHA": 255, "HO_TEN_ME": 255, "NGUOI_GIAM_HO": 255,
        "DON_VI": 1024, "NGAY_VAO": 12, "NGAY_RA": 12,
        "NGAY_SINHCON": 8, "NGAY_CONCHET": 8, "SO_CONCHET": 2,
        "KET_QUA_DTRI": 1, "MA_TTDV": 255, "NGAY_CT": 8, "MA_THE_TAM": 15,
    }
    _NUMERIC: ClassVar[set] = {"SO_CONCHET", "KET_QUA_DTRI"}
    _DATE12: ClassVar[set] = {"NGAY_VAO", "NGAY_RA"}
    _DATE8: ClassVar[set] = {"NGAY_SINHCON", "NGAY_CONCHET", "NGAY_CT"}