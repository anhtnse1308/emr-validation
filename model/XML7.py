from dataclasses import dataclass, field, fields
from typing import Optional, ClassVar, Dict, Any
import re
from datetime import datetime
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
    # -----------------------------------------------------------------------
    # validate() – Logic nghiệp vụ Bảng 7
    # -----------------------------------------------------------------------
    def validate(self) -> list[str]:
        errs: list[str] = []

        # ==================================================================
        # 1. MA_LK – bắt buộc
        # ==================================================================
        if not self.MA_LK:
            errs.append("MA_LK: bắt buộc, không được để trống")

        # ==================================================================
        # 5-6. NGAY_VAO, NGAY_RA – DATE12, NGAY_RA >= NGAY_VAO
        # ==================================================================
        dt_vao = self._parse_date12(self.NGAY_VAO)
        dt_ra  = self._parse_date12(self.NGAY_RA)

        if self.NGAY_VAO and dt_vao is None:
            errs.append(
                f"NGAY_VAO: '{self.NGAY_VAO}' không phải ngày giờ hợp lệ "
                "(định dạng yyyymmddHHMM)"
            )
        if self.NGAY_RA and dt_ra is None:
            errs.append(
                f"NGAY_RA: '{self.NGAY_RA}' không phải ngày giờ hợp lệ "
                "(định dạng yyyymmddHHMM)"
            )
        if isinstance(dt_vao, datetime) and isinstance(dt_ra, datetime) and dt_ra < dt_vao:
            errs.append(
                f"NGAY_RA ({self.NGAY_RA}) không được trước NGAY_VAO ({self.NGAY_VAO})"
            )

        # ==================================================================
        # 7. MA_DINH_CHI_THAI – Số, 1 ký tự, enum {0, 1}
        # ==================================================================
        ma_dct = self._to_int(self.MA_DINH_CHI_THAI)
        if self.MA_DINH_CHI_THAI is not None and ma_dct not in {0, 1}:
            errs.append(
                f"MA_DINH_CHI_THAI: '{self.MA_DINH_CHI_THAI}' không hợp lệ, "
                "chỉ chấp nhận 0 (không đình chỉ) hoặc 1 (đình chỉ thai nghén)"
            )

        # ==================================================================
        # Nhóm đình chỉ thai: khi MA_DINH_CHI_THAI = 1
        #   → NGUYENNHAN_DINHCHI, THOIGIAN_DINHCHI, TUOI_THAI bắt buộc
        # ==================================================================
        if ma_dct == 1:
            if not self.NGUYENNHAN_DINHCHI:
                errs.append(
                    "NGUYENNHAN_DINHCHI: bắt buộc khi MA_DINH_CHI_THAI = 1"
                )
            if not self.THOIGIAN_DINHCHI:
                errs.append(
                    "THOIGIAN_DINHCHI: bắt buộc khi MA_DINH_CHI_THAI = 1"
                )
            if not self.TUOI_THAI:
                errs.append(
                    "TUOI_THAI: bắt buộc khi MA_DINH_CHI_THAI = 1"
                )

        # ==================================================================
        # 9. THOIGIAN_DINHCHI – validate ngày hợp lệ khi có
        # ==================================================================
        if self.THOIGIAN_DINHCHI:
            dt_dct = self._parse_date12(self.THOIGIAN_DINHCHI)
            if dt_dct is None:
                errs.append(
                    f"THOIGIAN_DINHCHI: '{self.THOIGIAN_DINHCHI}' "
                    "không phải ngày giờ hợp lệ (định dạng yyyymmddHHMM)"
                )
            # THOIGIAN_DINHCHI phải trong khoảng [NGAY_VAO, NGAY_RA]
            if isinstance(dt_dct, datetime) and isinstance(dt_vao, datetime) and dt_dct < dt_vao:
                errs.append(
                    f"THOIGIAN_DINHCHI ({self.THOIGIAN_DINHCHI}) "
                    f"không được trước NGAY_VAO ({self.NGAY_VAO})"
                )
            if isinstance(dt_dct, datetime) and isinstance(dt_ra, datetime) and dt_dct > dt_ra:
                errs.append(
                    f"THOIGIAN_DINHCHI ({self.THOIGIAN_DINHCHI}) "
                    f"không được sau NGAY_RA ({self.NGAY_RA})"
                )

        # ==================================================================
        # 10. TUOI_THAI – Số, 1–42 tuần
        # ==================================================================
        tuoi_thai = self._to_int(self.TUOI_THAI)
        if self.TUOI_THAI is not None and tuoi_thai is not None:
            if not (1 <= tuoi_thai <= 42):
                errs.append(
                    f"TUOI_THAI: '{self.TUOI_THAI}' không hợp lệ, "
                    "tuổi thai phải trong 1–42 tuần"
                )

        # ==================================================================
        # 17. NGAY_CT – DATE8, phải trùng ngày với NGAY_RA
        #    "Ngày chứng từ phải trùng với ngày ra viện"
        # ==================================================================
        dt_ct = self._parse_date8(self.NGAY_CT)
        if self.NGAY_CT and dt_ct is None:
            errs.append(
                f"NGAY_CT: '{self.NGAY_CT}' không phải ngày hợp lệ "
                "(định dạng yyyymmdd)"
            )
        if dt_ct and dt_ra:
            ngay_ra_date = dt_ra.date()
            if dt_ct.date() != ngay_ra_date:
                errs.append(
                    f"NGAY_CT ({self.NGAY_CT}) phải trùng với ngày ra viện "
                    f"NGAY_RA ({str(self.NGAY_RA)[:8]})"
                )

        # ==================================================================
        # 23. SO_NGAY_NGHI – Số, max 3 ký tự, >= 0
        # ==================================================================
        so_ngay_nghi = self._to_int(self.SO_NGAY_NGHI)
        if self.SO_NGAY_NGHI is not None and so_ngay_nghi is not None:
            if so_ngay_nghi < 0:
                errs.append(
                    f"SO_NGAY_NGHI: '{self.SO_NGAY_NGHI}' không được âm"
                )

        # ==================================================================
        # 24-25. NGOAITRU_TUNGAY / NGOAITRU_DENNGAY – DATE8
        #    - NGOAITRU_TUNGAY >= NGAY_RA (phần ngày)
        #    - NGOAITRU_DENNGAY >= NGOAITRU_TUNGAY
        #    - Khoảng ngày phải khớp SO_NGAY_NGHI
        # ==================================================================
        dt_tu  = self._parse_date8(self.NGOAITRU_TUNGAY)
        dt_den = self._parse_date8(self.NGOAITRU_DENNGAY)

        if self.NGOAITRU_TUNGAY and dt_tu is None:
            errs.append(
                f"NGOAITRU_TUNGAY: '{self.NGOAITRU_TUNGAY}' không phải ngày hợp lệ "
                "(định dạng yyyymmdd)"
            )
        if self.NGOAITRU_DENNGAY and dt_den is None:
            errs.append(
                f"NGOAITRU_DENNGAY: '{self.NGOAITRU_DENNGAY}' không phải ngày hợp lệ "
                "(định dạng yyyymmdd)"
            )

        # NGOAITRU_TUNGAY không được trước ngày ra viện
        if isinstance(dt_tu, datetime) and isinstance(dt_ra, datetime) and dt_tu.date() < dt_ra.date():
            errs.append(
                f"NGOAITRU_TUNGAY ({self.NGOAITRU_TUNGAY}) không được trước "
                f"ngày ra viện ({str(self.NGAY_RA)[:8]})"
            )

        # NGOAITRU_DENNGAY >= NGOAITRU_TUNGAY
        if isinstance(dt_tu, datetime) and isinstance(dt_den, datetime) and dt_den < dt_tu:
            errs.append(
                f"NGOAITRU_DENNGAY ({self.NGOAITRU_DENNGAY}) không được trước "
                f"NGOAITRU_TUNGAY ({self.NGOAITRU_TUNGAY})"
            )

        # Kiểm tra SO_NGAY_NGHI = DENNGAY - TUNGAY + 1
        if dt_tu and dt_den and so_ngay_nghi is not None and so_ngay_nghi > 0:
            expected_ngay = (dt_den.date() - dt_tu.date()).days + 1
            if expected_ngay != so_ngay_nghi:
                errs.append(
                    f"SO_NGAY_NGHI: kỳ vọng {expected_ngay} ngày "
                    f"(NGOAITRU_DENNGAY - NGOAITRU_TUNGAY + 1), "
                    f"thực tế {so_ngay_nghi}"
                )

        # Tính nhất quán: có ngày ngoại trú → phải có SO_NGAY_NGHI và ngược lại
        has_ngoaitru = bool(self.NGOAITRU_TUNGAY or self.NGOAITRU_DENNGAY)
        has_so_ngay  = so_ngay_nghi is not None and so_ngay_nghi > 0
        if has_ngoaitru and not has_so_ngay:
            errs.append(
                "SO_NGAY_NGHI: bắt buộc khi có NGOAITRU_TUNGAY/NGOAITRU_DENNGAY"
            )
        if has_so_ngay and not has_ngoaitru:
            errs.append(
                "NGOAITRU_TUNGAY / NGOAITRU_DENNGAY: bắt buộc khi SO_NGAY_NGHI > 0"
            )
        # Phải có đủ cả TUNGAY lẫn DENNGAY
        if bool(self.NGOAITRU_TUNGAY) != bool(self.NGOAITRU_DENNGAY):
            errs.append(
                "NGOAITRU_TUNGAY và NGOAITRU_DENNGAY: phải cùng có hoặc cùng để trống"
            )

        return errs