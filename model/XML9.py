from dataclasses import dataclass, field, fields
from typing import Optional, ClassVar, Dict, Any
import re
from model.BHYTBase import BHYTBase

# ===========================================================================
# BẢNG 9 – Giấy chứng sinh
# Cập nhật theo QĐ 4750/QĐ-BYT:
#   - Thêm field SINHCON_DUOI32TUAN (STT 27)
#   - Implement validate() đầy đủ
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
    SO_CCCD_NND: Optional[str] = None       # [đổi -> Chuỗi, size=n]
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
    TINH_TRANG_CON: Optional[str] = None    # [size=n]
    SINHCON_PHAUTHUAT: Optional[str] = None
    SINHCON_DUOI32TUAN: Optional[str] = None  # [QĐ 4750 bổ sung – STT 27]
    GHI_CHU: Optional[str] = None           # [size=n]
    NGUOI_DO_DE: Optional[str] = None
    NGUOI_GHI_PHIEU: Optional[str] = None
    NGAY_CT: Optional[str] = None
    SO: Optional[str] = None
    QUYEN_SO: Optional[str] = None
    MA_TTDV: Optional[str] = None           # [đổi -> Chuỗi, size -> 255]
    DU_PHONG: Optional[str] = None          # [QĐ 4750 bổ sung]

    _MAX_LEN: ClassVar[Dict[str, Optional[int]]] = {
        "MA_LK": 100, "MA_BHXH_NND": 10, "MA_THE_NND": 15, "HO_TEN_NND": 255,
        "NGAYSINH_NND": 8, "MA_DANTOC_NND": 2,
        # SO_CCCD_NND: size=n → không giới hạn, bỏ khỏi _MAX_LEN
        "NGAYCAP_CCCD_NND": 8, "NOICAP_CCCD_NND": 1024, "NOI_CU_TRU_NND": 1024,
        "MA_QUOCTICH": 3, "MATINH_CU_TRU": 3, "MAHUYEN_CU_TRU": 3,
        "MAXA_CU_TRU": 5, "HO_TEN_CHA": 255, "MA_THE_TAM": 15,
        "HO_TEN_CON": 255, "GIOI_TINH_CON": 1, "SO_CON": 2,
        "LAN_SINH": 2, "SO_CON_SONG": 2, "CAN_NANG_CON": 10,
        "NGAY_SINH_CON": 12, "NOI_SINH_CON": 1024,
        # TINH_TRANG_CON: size=n → không giới hạn
        "SINHCON_PHAUTHUAT": 1, "SINHCON_DUOI32TUAN": 1,
        # GHI_CHU: size=n → không giới hạn
        "NGUOI_DO_DE": 255, "NGUOI_GHI_PHIEU": 255,
        "NGAY_CT": 8, "SO": 200, "QUYEN_SO": 200, "MA_TTDV": 255,
        # DU_PHONG: size=n → không giới hạn
    }
    _NUMERIC: ClassVar[set] = {
        "GIOI_TINH_CON", "SO_CON", "LAN_SINH", "SO_CON_SONG",
        "CAN_NANG_CON", "SINHCON_PHAUTHUAT", "SINHCON_DUOI32TUAN",
    }
    _DATE12: ClassVar[set] = {"NGAY_SINH_CON"}
    _DATE8: ClassVar[set] = {"NGAYSINH_NND", "NGAYCAP_CCCD_NND", "NGAY_CT"}

    # -----------------------------------------------------------------------
    # validate() – Logic nghiệp vụ Bảng 9
    # Base class tự xử lý _MAX_LEN, _NUMERIC, _DATE12, _DATE8.
    # Override bổ sung: bắt buộc, enum, cross-field.
    # -----------------------------------------------------------------------
    def validate(self) -> list[str]:
        errs: list[str] = super().validate()

        # ==================================================================
        # 1. MA_LK – bắt buộc
        # ==================================================================
        if not self.MA_LK:
            errs.append("MA_LK: bắt buộc, không được để trống")

        # ==================================================================
        # 18. GIOI_TINH_CON – Số, 1 ký tự, enum {1, 2, 3}
        #    1=Nam / 2=Nữ / 3=Chưa xác định
        # ==================================================================
        gt_con = self._to_int(self.GIOI_TINH_CON)
        if self.GIOI_TINH_CON is not None and gt_con not in {1, 2, 3}:
            errs.append(
                f"GIOI_TINH_CON: '{self.GIOI_TINH_CON}' không hợp lệ "
                "(cần 1=Nam / 2=Nữ / 3=Chưa xác định)"
            )

        # ==================================================================
        # 19. SO_CON – Số, max 2 ký tự, >= 1
        # ==================================================================
        so_con = self._to_int(self.SO_CON)
        if self.SO_CON is not None and so_con is not None and so_con < 1:
            errs.append(
                f"SO_CON: '{self.SO_CON}' phải >= 1"
            )

        # ==================================================================
        # 20. LAN_SINH – Số, max 2 ký tự, >= 1
        # ==================================================================
        lan_sinh = self._to_int(self.LAN_SINH)
        if self.LAN_SINH is not None and lan_sinh is not None and lan_sinh < 1:
            errs.append(
                f"LAN_SINH: '{self.LAN_SINH}' phải >= 1 (tính cả lần sinh này)"
            )

        # ==================================================================
        # 21. SO_CON_SONG – Số, max 2 ký tự, >= 0
        #    Tính cả trẻ sinh ra lần này → có thể = 0 nếu trẻ chết ngay
        # ==================================================================
        so_con_song = self._to_int(self.SO_CON_SONG)
        if self.SO_CON_SONG is not None and so_con_song is not None and so_con_song < 0:
            errs.append(
                f"SO_CON_SONG: '{self.SO_CON_SONG}' không được âm"
            )

        # ==================================================================
        # 22. CAN_NANG_CON – Số, max 10 ký tự, tính theo gram, > 0
        # ==================================================================
        can_nang = self._to_float(self.CAN_NANG_CON)
        if self.CAN_NANG_CON is not None and can_nang is not None and can_nang <= 0:
            errs.append(
                f"CAN_NANG_CON: '{self.CAN_NANG_CON}' phải > 0 (đơn vị gram)"
            )

        # ==================================================================
        # 26. SINHCON_PHAUTHUAT – Số, 1 ký tự, enum {0, 1}
        #    1=sinh con phải phẫu thuật / 0=không phải phẫu thuật
        # ==================================================================
        phauthuat = self._to_int(self.SINHCON_PHAUTHUAT)
        if self.SINHCON_PHAUTHUAT is not None and phauthuat not in {0, 1}:
            errs.append(
                f"SINHCON_PHAUTHUAT: '{self.SINHCON_PHAUTHUAT}' không hợp lệ "
                "(cần 0=không phẫu thuật / 1=có phẫu thuật)"
            )

        # ==================================================================
        # 27. SINHCON_DUOI32TUAN – Số, 1 ký tự, enum {0, 1}  [QĐ 4750 bổ sung]
        #    1=sinh con dưới 32 tuần tuổi / 0=không
        # ==================================================================
        duoi32tuan = self._to_int(self.SINHCON_DUOI32TUAN)
        if self.SINHCON_DUOI32TUAN is not None and duoi32tuan not in {0, 1}:
            errs.append(
                f"SINHCON_DUOI32TUAN: '{self.SINHCON_DUOI32TUAN}' không hợp lệ "
                "(cần 0=không / 1=sinh con dưới 32 tuần tuổi)"
            )

        # ==================================================================
        # 28. GHI_CHU – cross-field bắt buộc khi có phẫu thuật / dưới 32 tuần
        #    Theo spec: phải ghi rõ 1 trong 3 nội dung:
        #      "Sinh con phải phẫu thuật"
        #      "Sinh con dưới 32 tuần tuổi"
        #      "Phẫu thuật, sinh con dưới 32 tuần tuổi"
        # ==================================================================
        _GHI_CHU_REQUIRED_VALUES = {
            "sinh con phải phẫu thuật",
            "sinh con dưới 32 tuần tuổi",
            "phẫu thuật, sinh con dưới 32 tuần tuổi",
        }
        need_ghi_chu = (phauthuat == 1) or (duoi32tuan == 1)
        if need_ghi_chu:
            if not self.GHI_CHU:
                errs.append(
                    "GHI_CHU: bắt buộc khi SINHCON_PHAUTHUAT=1 hoặc SINHCON_DUOI32TUAN=1. "
                    "Phải ghi rõ: \"Sinh con phải phẫu thuật\" hoặc "
                    "\"Sinh con dưới 32 tuần tuổi\" hoặc "
                    "\"Phẫu thuật, sinh con dưới 32 tuần tuổi\""
                )
            else:
                ghi_chu_norm = str(self.GHI_CHU).strip().lower()
                if ghi_chu_norm not in _GHI_CHU_REQUIRED_VALUES:
                    errs.append(
                        f"GHI_CHU: '{self.GHI_CHU}' không đúng nội dung quy định. "
                        "Phải là (không phân biệt hoa thường): "
                        "\"Sinh con phải phẫu thuật\" / "
                        "\"Sinh con dưới 32 tuần tuổi\" / "
                        "\"Phẫu thuật, sinh con dưới 32 tuần tuổi\""
                    )

        # ==================================================================
        # Cross-field: SINHCON_PHAUTHUAT=1 & SINHCON_DUOI32TUAN=1
        #    → GHI_CHU phải ghi đủ cả hai nội dung (mã 3)
        # ==================================================================
        if phauthuat == 1 and duoi32tuan == 1 and self.GHI_CHU:
            ghi_chu_norm = str(self.GHI_CHU).strip().lower()
            if ghi_chu_norm != "phẫu thuật, sinh con dưới 32 tuần tuổi":
                errs.append(
                    f"GHI_CHU: khi cả SINHCON_PHAUTHUAT=1 và SINHCON_DUOI32TUAN=1, "
                    "phải ghi: \"Phẫu thuật, sinh con dưới 32 tuần tuổi\""
                )

        return errs