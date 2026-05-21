from dataclasses import dataclass, field, fields
from typing import Optional, ClassVar, Dict, Any
import re
from datetime import datetime
from model.BHYTBase import BHYTBase

# ===========================================================================
# BẢNG 10 – Giấy nghỉ dưỡng thai
# Cập nhật theo QĐ 4750/QĐ-BYT:
#   - MA_TTDV: đổi kiểu dữ liệu thành chuỗi (đã đúng)
#   - MA_BS: tăng kích thước tối đa 255 ký tự (đã đúng)
#   - CHAN_DOAN_RV: sửa diễn giải → bắt buộc ghi cụm từ "dưỡng thai"
#   - DU_PHONG: bổ sung trường dự phòng (đã có)
#   - Implement validate() đầy đủ
# ===========================================================================

@dataclass
class Bang10_GiayNghiDuongThai(BHYTBase):
    """Bảng 10. Chỉ tiêu dữ liệu giấy chứng nhận nghỉ dưỡng thai."""

    MA_LK: Optional[str] = None
    SO_SERI: Optional[str] = None
    SO_CT: Optional[str] = None
    SO_NGAY: Optional[str] = None           # SO_NGAY = DEN_NGAY - TU_NGAY (tính inclusive)
    DON_VI: Optional[str] = None
    CHAN_DOAN_RV: Optional[str] = None      # [size=n; QĐ 4750: bắt buộc chứa "dưỡng thai"]
    TU_NGAY: Optional[str] = None
    DEN_NGAY: Optional[str] = None
    MA_TTDV: Optional[str] = None           # [đổi -> Chuỗi, size -> 255]
    TEN_BS: Optional[str] = None
    MA_BS: Optional[str] = None             # [size -> 255]
    NGAY_CT: Optional[str] = None
    DU_PHONG: Optional[str] = None          # [size=n; QĐ 4750 bổ sung]

    _MAX_LEN: ClassVar[Dict[str, Optional[int]]] = {
        "MA_LK": 100, "SO_SERI": 200, "SO_CT": 200, "SO_NGAY": 3,
        "DON_VI": 1024, "TU_NGAY": 8, "DEN_NGAY": 8,
        "MA_TTDV": 255, "TEN_BS": 255, "MA_BS": 255, "NGAY_CT": 8,
        # CHAN_DOAN_RV, DU_PHONG: size=n → không giới hạn
    }
    _NUMERIC: ClassVar[set] = {"SO_NGAY"}
    _DATE8: ClassVar[set] = {"TU_NGAY", "DEN_NGAY", "NGAY_CT"}

    # -----------------------------------------------------------------------
    # validate() – Logic nghiệp vụ Bảng 10
    # Base class tự xử lý _MAX_LEN, _NUMERIC, _DATE8.
    # Override bổ sung: bắt buộc, khoảng thời gian, cross-field SO_NGAY.
    # -----------------------------------------------------------------------
    def validate(self) -> list[str]:
        errs: list[str] = super().validate()

        # ==================================================================
        # 1. MA_LK – bắt buộc
        # ==================================================================
        if not self.MA_LK:
            errs.append("MA_LK: bắt buộc, không được để trống")

        # ==================================================================
        # 4. SO_NGAY – số nguyên dương
        # ==================================================================
        so_ngay = self._to_int(self.SO_NGAY)
        if self.SO_NGAY is not None and so_ngay is not None and so_ngay < 1:
            errs.append(
                f"SO_NGAY: '{self.SO_NGAY}' phải là số nguyên dương >= 1"
            )

        # ==================================================================
        # 6. CHAN_DOAN_RV – QĐ 4750: bắt buộc chứa cụm từ "dưỡng thai"
        # ==================================================================
        if self.CHAN_DOAN_RV:
            if "dưỡng thai" not in str(self.CHAN_DOAN_RV).lower():
                errs.append(
                    f"CHAN_DOAN_RV: '{self.CHAN_DOAN_RV}' phải chứa cụm từ "
                    "\"dưỡng thai\" theo QĐ 4750/QĐ-BYT"
                )
        else:
            errs.append("CHAN_DOAN_RV: bắt buộc, không được để trống")

        # ==================================================================
        # 7-8. TU_NGAY, DEN_NGAY – parse + DEN_NGAY >= TU_NGAY
        # ==================================================================
        dt_tu  = self._parse_date8(self.TU_NGAY)
        dt_den = self._parse_date8(self.DEN_NGAY)

        if self.TU_NGAY and dt_tu is None:
            errs.append(
                f"TU_NGAY: '{self.TU_NGAY}' không phải ngày hợp lệ "
                "(định dạng yyyymmdd)"
            )
        if self.DEN_NGAY and dt_den is None:
            errs.append(
                f"DEN_NGAY: '{self.DEN_NGAY}' không phải ngày hợp lệ "
                "(định dạng yyyymmdd)"
            )
        if isinstance(dt_tu, datetime) and isinstance(dt_den, datetime):
            if dt_den < dt_tu:
                errs.append(
                    f"DEN_NGAY ({self.DEN_NGAY}) không được trước "
                    f"TU_NGAY ({self.TU_NGAY})"
                )

            # ==============================================================
            # Cross-field: SO_NGAY = (DEN_NGAY - TU_NGAY).days + 1
            #   Tính inclusive cả hai đầu, nhất quán với XML7.SO_NGAY_NGHI.
            #   VD theo spec: TU_NGAY=20180713, DEN_NGAY=20180811 → SO_NGAY=30
            # ==============================================================
            if so_ngay is not None and so_ngay >= 1:
                expected = (dt_den.date() - dt_tu.date()).days + 1
                if expected != so_ngay:
                    errs.append(
                        f"SO_NGAY: kỳ vọng {expected} ngày "
                        f"(DEN_NGAY - TU_NGAY + 1, tính cả 2 đầu), "
                        f"thực tế {so_ngay}"
                    )

        # ==================================================================
        # 12. NGAY_CT – DATE8, >= TU_NGAY
        #    Ngày cấp chứng từ không được trước ngày bắt đầu nghỉ
        # ==================================================================
        dt_ct = self._parse_date8(self.NGAY_CT)
        if self.NGAY_CT and dt_ct is None:
            errs.append(
                f"NGAY_CT: '{self.NGAY_CT}' không phải ngày hợp lệ "
                "(định dạng yyyymmdd)"
            )
        if isinstance(dt_ct, datetime) and isinstance(dt_tu, datetime):
            if dt_ct.date() < dt_tu.date():
                errs.append(
                    f"NGAY_CT ({self.NGAY_CT}) không được trước "
                    f"ngày bắt đầu nghỉ TU_NGAY ({self.TU_NGAY})"
                )

        return errs