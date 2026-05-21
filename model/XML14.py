from dataclasses import dataclass, field, fields
from typing import Optional, ClassVar, Dict, Any
import re
from datetime import datetime
from model.BHYTBase import BHYTBase

# ===========================================================================
# BẢNG 14 – Giấy hẹn khám lại
# Cập nhật theo QĐ 4750/QĐ-BYT:
#   - NGAY_HEN_KL : size 12→8; đổi định dạng yyyymmddHHMM → yyyymmdd (đã đúng)
#   - MA_BAC_SI   : diễn giải mới – mã GPHN; huy động: GPHN.HD.XXXXX
#   - MA_TTDV     : diễn giải mới – mã GPHN người ký; đổi kiểu Chuỗi (đã đúng)
#   - DU_PHONG    : bổ sung – lưu chữ ký số KBCB (đã có)
#   - STT 14      : bị bỏ trong spec (nhảy 13→15), model không bị ảnh hưởng
#   - Ghi chú spec: chỉ gửi khi có hẹn khám lại
#   - Implement validate() đầy đủ
# ===========================================================================

@dataclass
class Bang14_GiayHenKhamLai(BHYTBase):
    """Bảng 14. Chỉ tiêu dữ liệu giấy hẹn khám lại."""

    MA_LK: Optional[str] = None
    SO_GIAYHEN_KL: Optional[str] = None
    MA_CSKCB: Optional[str] = None          # [size=5; mã CS cấp giấy hẹn]
    HO_TEN: Optional[str] = None
    NGAY_SINH: Optional[str] = None
    GIOI_TINH: Optional[str] = None
    DIA_CHI: Optional[str] = None
    MA_THE_BHYT: Optional[str] = None       # [size=n]
    GT_THE_DEN: Optional[str] = None        # [size=n]
    NGAY_VAO: Optional[str] = None
    NGAY_VAO_NOI_TRU: Optional[str] = None
    NGAY_RA: Optional[str] = None
    NGAY_HEN_KL: Optional[str] = None       # [QĐ 4750: size 12→8; yyyymmdd]
    # STT 14: bị bỏ trong QĐ 4750 (spec nhảy từ 13→15)
    CHAN_DOAN_RV: Optional[str] = None      # [size=n]
    MA_BENH_CHINH: Optional[str] = None
    MA_BENH_KT: Optional[str] = None
    MA_BENH_YHCT: Optional[str] = None
    MA_DOITUONG_KCB: Optional[str] = None
    MA_BAC_SI: Optional[str] = None         # [size=255; mã GPHN; huy động: GPHN.HD.XXXXX]
    MA_TTDV: Optional[str] = None           # [đổi -> Chuỗi, size=255; mã GPHN người ký]
    NGAY_CT: Optional[str] = None           # [DATE8; ngày cấp giấy hẹn]
    DU_PHONG: Optional[str] = None          # [size=n; QĐ 4750: lưu chữ ký số KBCB]

    _MAX_LEN: ClassVar[Dict[str, Optional[int]]] = {
        "MA_LK": 100, "SO_GIAYHEN_KL": 50, "MA_CSKCB": 5,
        "HO_TEN": 255, "NGAY_SINH": 12, "GIOI_TINH": 1,
        "DIA_CHI": 1024, "NGAY_VAO": 12, "NGAY_VAO_NOI_TRU": 12,
        "NGAY_RA": 12, "NGAY_HEN_KL": 8,
        # MA_THE_BHYT, GT_THE_DEN, CHAN_DOAN_RV, DU_PHONG: size=n
        "MA_BENH_CHINH": 7, "MA_BENH_KT": 100, "MA_BENH_YHCT": 255,
        "MA_DOITUONG_KCB": 4, "MA_BAC_SI": 255, "MA_TTDV": 255,
        "NGAY_CT": 8,
    }
    _NUMERIC: ClassVar[set] = {"GIOI_TINH"}
    _DATE12: ClassVar[set] = {"NGAY_SINH", "NGAY_VAO", "NGAY_VAO_NOI_TRU", "NGAY_RA"}
    _DATE8: ClassVar[set] = {"NGAY_HEN_KL", "NGAY_CT"}

    # -----------------------------------------------------------------------
    # validate() – Logic nghiệp vụ Bảng 14
    # Base class tự xử lý _MAX_LEN, _NUMERIC, _DATE12, _DATE8.
    # Override: bắt buộc, enum, cross-field ngày, MA_BAC_SI format.
    # -----------------------------------------------------------------------
    def validate(self) -> list[str]:
        errs: list[str] = super().validate()

        # ==================================================================
        # 1. MA_LK – bắt buộc
        # ==================================================================
        if not self.MA_LK:
            errs.append("MA_LK: bắt buộc, không được để trống")

        # ==================================================================
        # 3. MA_CSKCB – đúng 5 ký tự
        # ==================================================================
        if self.MA_CSKCB and len(str(self.MA_CSKCB).strip()) != 5:
            errs.append(
                f"MA_CSKCB: '{self.MA_CSKCB}' phải đúng 5 ký tự, "
                f"nhận {len(str(self.MA_CSKCB).strip())} ký tự"
            )

        # ==================================================================
        # 6. GIOI_TINH – Số, 1 ký tự, enum {1=Nam / 2=Nữ / 3=Chưa XĐ}
        # ==================================================================
        gt = self._to_int(self.GIOI_TINH)
        if self.GIOI_TINH is not None and gt not in {1, 2, 3}:
            errs.append(
                f"GIOI_TINH: '{self.GIOI_TINH}' không hợp lệ "
                "(cần 1=Nam / 2=Nữ / 3=Chưa xác định)"
            )

        # ==================================================================
        # Cross-field: NGAY_RA >= NGAY_VAO
        # ==================================================================
        dt_vao = self._parse_date12(self.NGAY_VAO)
        dt_ra  = self._parse_date12(self.NGAY_RA)

        if isinstance(dt_vao, datetime) and isinstance(dt_ra, datetime):
            if dt_ra < dt_vao:
                errs.append(
                    f"NGAY_RA ({self.NGAY_RA}) không được trước "
                    f"NGAY_VAO ({self.NGAY_VAO})"
                )

        # ==================================================================
        # 13. NGAY_HEN_KL – DATE8 (base xử lý), phải >= NGAY_RA (ngày)
        #     Lý do: hẹn khám lại phải sau hoặc bằng ngày ra viện/kết thúc KCB
        # ==================================================================
        dt_hen = self._parse_date8(self.NGAY_HEN_KL)
        if self.NGAY_HEN_KL and dt_hen is None:
            errs.append(
                f"NGAY_HEN_KL: '{self.NGAY_HEN_KL}' không phải ngày hợp lệ "
                "(định dạng yyyymmdd)"
            )
        if isinstance(dt_hen, datetime) and isinstance(dt_ra, datetime):
            if dt_hen.date() < dt_ra.date():
                errs.append(
                    f"NGAY_HEN_KL ({self.NGAY_HEN_KL}) không được trước "
                    f"ngày ra viện NGAY_RA ({str(self.NGAY_RA)[:8]})"
                )

        # ==================================================================
        # 15. MA_BENH_CHINH – chỉ 1 mã ICD-10, không chứa ";"
        # ==================================================================
        if self.MA_BENH_CHINH and ";" in str(self.MA_BENH_CHINH):
            errs.append(
                f"MA_BENH_CHINH: '{self.MA_BENH_CHINH}' chỉ được 1 mã ICD-10 "
                "(không dùng dấu ';')"
            )

        # ==================================================================
        # 20. MA_BAC_SI – Chuỗi, max 255
        #     QĐ 4750: mã GPHN người hành nghề chỉ định hẹn lại
        #     Huy động/điều động: GPHN.HD.XXXXX
        #       XXXXX = mã 5 ký tự CS KBCB cử đi
        #            hoặc TT_XXX (2 ký tự mã tỉnh + XXX khi không đăng ký HN)
        # ==================================================================
        if self.MA_BAC_SI:
            val = str(self.MA_BAC_SI).strip()
            if "." in val:
                parts = val.split(".")
                if len(parts) != 3:
                    errs.append(
                        f"MA_BAC_SI: '{val}' sai định dạng. "
                        "Huy động/điều động phải là <GPHN>.HD.<MaCsKbcb>"
                    )
                else:
                    gphn, loai, ma_cs = parts
                    if not gphn.strip():
                        errs.append(
                            f"MA_BAC_SI: thiếu mã GPHN trong '{val}'"
                        )
                    if loai.upper() != "HD":
                        errs.append(
                            f"MA_BAC_SI: loại '{loai}' không hợp lệ trong '{val}'. "
                            "Bảng 14 chỉ dùng HD (huy động/điều động)"
                        )
                    if not ma_cs.strip():
                        errs.append(
                            f"MA_BAC_SI: thiếu mã cơ sở KBCB trong '{val}'"
                        )

        # ==================================================================
        # 22. NGAY_CT – DATE8, >= NGAY_RA (ngày cấp giấy hẹn >= ngày ra)
        # ==================================================================
        dt_ct = self._parse_date8(self.NGAY_CT)
        if self.NGAY_CT and dt_ct is None:
            errs.append(
                f"NGAY_CT: '{self.NGAY_CT}' không phải ngày hợp lệ "
                "(định dạng yyyymmdd)"
            )
        if isinstance(dt_ct, datetime) and isinstance(dt_ra, datetime):
            if dt_ct.date() < dt_ra.date():
                errs.append(
                    f"NGAY_CT ({self.NGAY_CT}) không được trước "
                    f"ngày ra viện NGAY_RA ({str(self.NGAY_RA)[:8]})"
                )

        return errs