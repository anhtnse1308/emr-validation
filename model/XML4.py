from dataclasses import dataclass, field, fields
from typing import Optional, ClassVar, Dict, Any
import re
from model.BHYTBase import BHYTBase

# ===========================================================================
# BẢNG 4 – Dịch vụ CLS
# ===========================================================================
 
@dataclass
class Bang4_DichVuCLS(BHYTBase):
    """Bảng 4. Chỉ tiêu chi tiết dịch vụ cận lâm sàng."""
 
    MA_LK: Optional[str] = None
    STT: Optional[str] = None
    MA_DICH_VU: Optional[str] = None        # [size -> 50]
    MA_CHI_SO: Optional[str] = None         # [size -> 255]
    TEN_CHI_SO: Optional[str] = None
    GIA_TRI: Optional[str] = None           # [size -> 255]
    DON_VI_DO: Optional[str] = None
    MO_TA: Optional[str] = None
    KET_LUAN: Optional[str] = None
    NGAY_KQ: Optional[str] = None
    MA_BS_DOC_KQ: Optional[str] = None
    DU_PHONG: Optional[str] = None
 
    _MAX_LEN: ClassVar[Dict[str, Optional[int]]] = {
        "MA_LK": 100, "STT": 10, "MA_DICH_VU": 50,
        "MA_CHI_SO": 255, "TEN_CHI_SO": 255, "GIA_TRI": 255,
        "DON_VI_DO": 50, "NGAY_KQ": 12, "MA_BS_DOC_KQ": 255,
    }
    _NUMERIC: ClassVar[set] = {"STT"}
    _DATE12: ClassVar[set] = {"NGAY_KQ"}