from dataclasses import dataclass, field, fields
from typing import Optional, ClassVar, Dict, Any
import re
from model.BHYTBase import BHYTBase

# ===========================================================================
# BẢNG 13 – Giấy chuyển tuyến BHYT
# ===========================================================================
 
@dataclass
class Bang13_GiayChuyenTuyen(BHYTBase):
    """Bảng 13. Chỉ tiêu dữ liệu giấy chuyển tuyến/chuyển cơ sở KBCB BHYT."""
 
    MA_LK: Optional[str] = None
    SO_HOSO: Optional[str] = None
    SO_CHUYENTUYEN: Optional[str] = None
    GIAY_CHUYEN_TUYEN: Optional[str] = None
    MA_CSKCB: Optional[str] = None
    MA_NOI_DI: Optional[str] = None         # [size -> 100, renamed]
    MA_NOI_DEN: Optional[str] = None        # [renamed]
    HO_TEN: Optional[str] = None
    NGAY_SINH: Optional[str] = None
    GIOI_TINH: Optional[str] = None
    MA_QUOCTICH: Optional[str] = None
    MA_DANTOC: Optional[str] = None
    MA_NGHE_NGHIEP: Optional[str] = None
    DIA_CHI: Optional[str] = None
    MA_THE_BHYT: Optional[str] = None
    GT_THE_DEN: Optional[str] = None
    NGAY_VAO: Optional[str] = None
    NGAY_VAO_NOI_TRU: Optional[str] = None
    NGAY_RA: Optional[str] = None
    DAU_HIEU_LS: Optional[str] = None
    CHAN_DOAN_RV: Optional[str] = None
    QT_BENHLY: Optional[str] = None
    TOMTAT_KQ: Optional[str] = None
    PP_DIEUTRI: Optional[str] = None
    MA_BENH_CHINH: Optional[str] = None
    MA_BENH_KT: Optional[str] = None
    MA_BENH_YHCT: Optional[str] = None
    TEN_DICH_VU: Optional[str] = None
    TEN_THUOC: Optional[str] = None
    PP_DIEU_TRI: Optional[str] = None       # [renamed]
    MA_LOAI_RV: Optional[str] = None
    MA_LYDO_CT: Optional[str] = None
    HUONG_DIEU_TRI: Optional[str] = None
    PHUONGTIEN_VC: Optional[str] = None
    HOTEN_NGUOI_HT: Optional[str] = None
    CHUCDANH_NGUOI_HT: Optional[str] = None
    MA_BAC_SI: Optional[str] = None
    MA_TTDV: Optional[str] = None           # [đổi -> Chuỗi, size -> 255]
    DU_PHONG: Optional[str] = None
 
    _MAX_LEN: ClassVar[Dict[str, Optional[int]]] = {
        "MA_LK": 100, "SO_HOSO": 50, "SO_CHUYENTUYEN": 50,
        "GIAY_CHUYEN_TUYEN": 50, "MA_CSKCB": 5,
        "MA_NOI_DI": 100, "MA_NOI_DEN": 5,
        "HO_TEN": 255, "NGAY_SINH": 12, "GIOI_TINH": 1,
        "MA_QUOCTICH": 3, "MA_DANTOC": 2, "MA_NGHE_NGHIEP": 5,
        "DIA_CHI": 1024, "NGAY_VAO": 100, "NGAY_VAO_NOI_TRU": 12,
        "NGAY_RA": 100, "MA_BENH_CHINH": 7, "MA_BENH_KT": 100,
        "MA_BENH_YHCT": 255, "TEN_DICH_VU": 1024, "TEN_THUOC": 1024,
        "MA_LOAI_RV": 1, "MA_LYDO_CT": 1,
        "PHUONGTIEN_VC": 255, "HOTEN_NGUOI_HT": 255,
        "CHUCDANH_NGUOI_HT": 255, "MA_BAC_SI": 255, "MA_TTDV": 255,
    }
    _NUMERIC: ClassVar[set] = {"GIOI_TINH", "MA_LOAI_RV", "MA_LYDO_CT"}
    _DATE12: ClassVar[set] = {"NGAY_SINH", "NGAY_VAO_NOI_TRU"}