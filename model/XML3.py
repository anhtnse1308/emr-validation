from dataclasses import dataclass, field, fields
from typing import Optional, ClassVar, Dict, Any
import re
from model.BHYTBase import BHYTBase

# ===========================================================================
# BẢNG 3 – DVKT & VTYT
# ===========================================================================
 
@dataclass
class Bang3_DVKT_VTYT(BHYTBase):
    """Bảng 3. Chỉ tiêu chi tiết dịch vụ kỹ thuật và vật tư y tế."""
 
    MA_LK: Optional[str] = None
    STT: Optional[str] = None
    MA_DICH_VU: Optional[str] = None
    MA_PTTT_QT: Optional[str] = None
    MA_VAT_TU: Optional[str] = None
    MA_NHOM: Optional[str] = None
    GOI_VTYT: Optional[str] = None
    TEN_VAT_TU: Optional[str] = None
    TEN_DICH_VU: Optional[str] = None
    MA_XANG_DAU: Optional[str] = None
    DON_VI_TINH: Optional[str] = None
    PHAM_VI: Optional[str] = None
    SO_LUONG: Optional[str] = None
    DON_GIA_BV: Optional[str] = None
    DON_GIA_BH: Optional[str] = None
    TT_THAU: Optional[str] = None           # [size -> 50]
    TYLE_TT_DV: Optional[str] = None
    TYLE_TT_BH: Optional[str] = None
    THANH_TIEN_BV: Optional[str] = None
    THANH_TIEN_BH: Optional[str] = None
    T_TRANTT: Optional[str] = None
    MUC_HUONG: Optional[str] = None
    T_NGUONKHAC_NSNN: Optional[str] = None
    T_NGUONKHAC_VTNN: Optional[str] = None
    T_NGUONKHAC_VTTN: Optional[str] = None
    T_NGUONKHAC_CL: Optional[str] = None
    T_NGUONKHAC: Optional[str] = None
    T_BNTT: Optional[str] = None
    T_BNCCT: Optional[str] = None
    T_BHTT: Optional[str] = None
    MA_KHOA: Optional[str] = None           # [size -> 50]
    MA_GIUONG: Optional[str] = None
    MA_BAC_SI: Optional[str] = None
    NGUOI_THUC_HIEN: Optional[str] = None
    MA_BENH: Optional[str] = None
    MA_BENH_YHCT: Optional[str] = None      # [size -> 150]
    NGAY_YL: Optional[str] = None
    NGAY_TH_YL: Optional[str] = None
    NGAY_KQ: Optional[str] = None
    MA_PTTT: Optional[str] = None
    VET_THUONG_TP: Optional[str] = None
    PP_VO_CAM: Optional[str] = None
    VI_TRI_TH_DVKT: Optional[str] = None
    MA_MAY: Optional[str] = None
    MA_HIEU_SP: Optional[str] = None
    TAI_SU_DUNG: Optional[str] = None
    DU_PHONG: Optional[str] = None
 
    _MAX_LEN: ClassVar[Dict[str, Optional[int]]] = {
        "MA_LK": 100, "STT": 10, "MA_DICH_VU": 50, "MA_PTTT_QT": 255,
        "MA_VAT_TU": 255, "MA_NHOM": 2, "GOI_VTYT": 3,
        "TEN_VAT_TU": 1024, "TEN_DICH_VU": 1024, "MA_XANG_DAU": 20,
        "DON_VI_TINH": 50, "PHAM_VI": 1, "SO_LUONG": 10,
        "DON_GIA_BV": 15, "DON_GIA_BH": 15, "TT_THAU": 50,
        "TYLE_TT_DV": 3, "TYLE_TT_BH": 3,
        "THANH_TIEN_BV": 15, "THANH_TIEN_BH": 15, "T_TRANTT": 15,
        "MUC_HUONG": 3,
        "T_NGUONKHAC_NSNN": 15, "T_NGUONKHAC_VTNN": 15,
        "T_NGUONKHAC_VTTN": 15, "T_NGUONKHAC_CL": 15, "T_NGUONKHAC": 15,
        "T_BNTT": 15, "T_BNCCT": 15, "T_BHTT": 15,
        "MA_KHOA": 50, "MA_GIUONG": 50, "MA_BAC_SI": 255,
        "NGUOI_THUC_HIEN": 255, "MA_BENH": 100, "MA_BENH_YHCT": 150,
        "NGAY_YL": 12, "NGAY_TH_YL": 12, "NGAY_KQ": 12,
        "MA_PTTT": 1, "VET_THUONG_TP": 1, "PP_VO_CAM": 1,
        "VI_TRI_TH_DVKT": 3, "MA_MAY": 1024, "MA_HIEU_SP": 255,
        "TAI_SU_DUNG": 1,
    }
    _NUMERIC: ClassVar[set] = {
        "STT", "MA_NHOM", "PHAM_VI", "SO_LUONG", "DON_GIA_BV", "DON_GIA_BH",
        "TYLE_TT_DV", "TYLE_TT_BH", "THANH_TIEN_BV", "THANH_TIEN_BH", "T_TRANTT",
        "MUC_HUONG", "T_NGUONKHAC_NSNN", "T_NGUONKHAC_VTNN", "T_NGUONKHAC_VTTN",
        "T_NGUONKHAC_CL", "T_NGUONKHAC", "T_BNTT", "T_BNCCT", "T_BHTT",
        "MA_PTTT", "VET_THUONG_TP", "PP_VO_CAM", "VI_TRI_TH_DVKT", "TAI_SU_DUNG",
    }
    _DATE12: ClassVar[set] = {"NGAY_YL", "NGAY_TH_YL", "NGAY_KQ"}