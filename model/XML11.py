from dataclasses import dataclass, field, fields
from typing import Optional, ClassVar, Dict, Any
import re
from datetime import datetime
from model.BHYTBase import BHYTBase

# ===========================================================================
# BẢNG 11 – Giấy chứng nhận nghỉ việc hưởng BHXH
# Cập nhật theo QĐ 4750/QĐ-BYT:
#   - CHAN_DOAN_RV : sửa đổi toàn bộ diễn giải (dưỡng thai / bệnh dài ngày)
#   - PP_DIEUTRI   : sửa → nội khoa / ngoại khoa / xạ trị / hoá trị / xạ trị+nội khoa
#   - MA_TTDV      : đổi kiểu Chuỗi, diễn giải mới (mã GPHN người ký)
#   - MA_BS        : tăng size 255, diễn giải mới (mã GPHN bác sĩ)
#   - DU_PHONG     : bổ sung trường dự phòng
#   - Implement validate() đầy đủ
# ===========================================================================

@dataclass
class Bang11_GiayNghiHuongBHXH(BHYTBase):
    """Bảng 11. Chỉ tiêu dữ liệu giấy chứng nhận nghỉ việc hưởng BHXH."""

    MA_LK: Optional[str] = None
    SO_CT: Optional[str] = None
    SO_SERI: Optional[str] = None
    SO_KCB: Optional[str] = None
    DON_VI: Optional[str] = None
    MA_BHXH: Optional[str] = None           # [đổi -> Chuỗi]
    MA_THE_BHYT: Optional[str] = None       # [size=n; multi-value ";"]
    CHAN_DOAN_RV: Optional[str] = None      # [size=n; QĐ 4750: dưỡng thai / bệnh dài ngày]
    PP_DIEUTRI: Optional[str] = None        # [size=n; QĐ 4750: nội khoa/ngoại khoa/xạ trị/hoá trị/xạ trị+nội khoa]
    MA_DINH_CHI_THAI: Optional[str] = None  # [Số; 0=không / 1=đình chỉ thai nghén]
    NGUYENNHAN_DINHCHI: Optional[str] = None  # [size=n; bắt buộc khi MA_DINH_CHI_THAI=1]
    TUOI_THAI: Optional[str] = None         # [Số, 1–42 tuần; bắt buộc khi MA_DINH_CHI_THAI=1]
    SO_NGAY_NGHI: Optional[str] = None      # [Số, max 3 ký tự; max 30 ngày/lần (lao: 180, sẩy thai ≥13t: 50)]
    TU_NGAY: Optional[str] = None           # [DATE8; trùng ngày đến khám]
    DEN_NGAY: Optional[str] = None          # [DATE8]
    HO_TEN_CHA: Optional[str] = None
    HO_TEN_ME: Optional[str] = None
    MA_TTDV: Optional[str] = None           # [đổi -> Chuỗi, size=255; mã GPHN người đứng đầu ký]
    MA_BS: Optional[str] = None             # [size=255; mã GPHN bác sĩ ký]
    NGAY_CT: Optional[str] = None           # [DATE8; trùng ngày đến khám hoặc ngày cuối đợt]
    MA_THE_TAM: Optional[str] = None
    MAU_SO: Optional[str] = None            # [Chuỗi, size=5; mặc định "CT07"]
    DU_PHONG: Optional[str] = None          # [size=n; QĐ 4750 bổ sung]

    _MAX_LEN: ClassVar[Dict[str, Optional[int]]] = {
        "MA_LK": 100, "SO_CT": 200, "SO_SERI": 200, "SO_KCB": 200,
        "DON_VI": 1024, "MA_BHXH": 10,
        # MA_THE_BHYT, CHAN_DOAN_RV, PP_DIEUTRI,
        # NGUYENNHAN_DINHCHI, DU_PHONG: size=n → không giới hạn
        "MA_DINH_CHI_THAI": 1, "TUOI_THAI": 2, "SO_NGAY_NGHI": 3,
        "TU_NGAY": 8, "DEN_NGAY": 8,
        "HO_TEN_CHA": 255, "HO_TEN_ME": 255,
        "MA_TTDV": 255, "MA_BS": 255, "NGAY_CT": 8,
        "MA_THE_TAM": 15, "MAU_SO": 5,
    }
    _NUMERIC: ClassVar[set] = {"MA_DINH_CHI_THAI", "TUOI_THAI", "SO_NGAY_NGHI"}
    _DATE8: ClassVar[set] = {"TU_NGAY", "DEN_NGAY", "NGAY_CT"}

    # Enum hợp lệ cho PP_DIEUTRI (QĐ 4750)
    _PP_DIEUTRI_VALID: ClassVar[set] = {
        "nội khoa", "ngoại khoa", "xạ trị",
        "hoá trị", "hóa trị",
        "xạ trị + nội khoa",
    }

    # -----------------------------------------------------------------------
    # validate() – Logic nghiệp vụ Bảng 11
    # Base class tự xử lý _MAX_LEN, _NUMERIC, _DATE8.
    # Override: bắt buộc, enum, nhóm đình chỉ thai, khoảng ngày, SO_NGAY.
    # -----------------------------------------------------------------------
    def validate(self) -> list[str]:
        errs: list[str] = super().validate()

        # ==================================================================
        # 1. MA_LK – bắt buộc
        # ==================================================================
        if not self.MA_LK:
            errs.append("MA_LK: bắt buộc, không được để trống")

        # ==================================================================
        # 8. CHAN_DOAN_RV – bắt buộc
        #    QĐ 4750: nếu điều trị dưỡng thai → phải chứa cụm từ "dưỡng thai"
        #    (không thể tự động phát hiện case dưỡng thai từ dữ liệu,
        #     nên chỉ kiểm tra trường bắt buộc không trống)
        # ==================================================================
        if not self.CHAN_DOAN_RV:
            errs.append("CHAN_DOAN_RV: bắt buộc, không được để trống")

        # ==================================================================
        # 9. PP_DIEUTRI – QĐ 4750: phải là 1 trong 5 giá trị chuẩn
        # ==================================================================
        if self.PP_DIEUTRI:
            pp_norm = str(self.PP_DIEUTRI).strip().lower()
            if pp_norm not in self._PP_DIEUTRI_VALID:
                errs.append(
                    f"PP_DIEUTRI: '{self.PP_DIEUTRI}' không hợp lệ theo QĐ 4750. "
                    "Chỉ chấp nhận: nội khoa / ngoại khoa / xạ trị / "
                    "hoá trị / xạ trị + nội khoa"
                )

        # ==================================================================
        # 10. MA_DINH_CHI_THAI – Số, 1 ký tự, enum {0, 1}
        # ==================================================================
        ma_dct = self._to_int(self.MA_DINH_CHI_THAI)
        if self.MA_DINH_CHI_THAI is not None and ma_dct not in {0, 1}:
            errs.append(
                f"MA_DINH_CHI_THAI: '{self.MA_DINH_CHI_THAI}' không hợp lệ "
                "(cần 0=không đình chỉ / 1=đình chỉ thai nghén)"
            )

        # ==================================================================
        # Nhóm đình chỉ thai: khi MA_DINH_CHI_THAI = 1
        #   → NGUYENNHAN_DINHCHI và TUOI_THAI bắt buộc
        # ==================================================================
        if ma_dct == 1:
            if not self.NGUYENNHAN_DINHCHI:
                errs.append(
                    "NGUYENNHAN_DINHCHI: bắt buộc khi MA_DINH_CHI_THAI = 1"
                )
            if not self.TUOI_THAI:
                errs.append(
                    "TUOI_THAI: bắt buộc khi MA_DINH_CHI_THAI = 1"
                )

        # ==================================================================
        # 12. TUOI_THAI – Số, 1–42 tuần
        # ==================================================================
        tuoi_thai = self._to_int(self.TUOI_THAI)
        if self.TUOI_THAI is not None and tuoi_thai is not None:
            if not (1 <= tuoi_thai <= 42):
                errs.append(
                    f"TUOI_THAI: '{self.TUOI_THAI}' không hợp lệ, "
                    "tuổi thai phải trong khoảng 1–42 tuần"
                )

        # ==================================================================
        # 13. SO_NGAY_NGHI – Số nguyên dương, max phụ thuộc case lâm sàng:
        #    - Thông thường       : tối đa 30 ngày/lần
        #    - Điều trị lao       : tối đa 180 ngày/lần
        #    - Sẩy/phá/nạo/hút thai ≥13 tuần: tối đa 50 ngày/lần
        #    Lưu ý: không thể xác định case từ dữ liệu đơn thuần
        #    → chỉ validate > 0 và cảnh báo khi vượt 180 (tuyệt đối tối đa)
        # ==================================================================
        so_ngay = self._to_int(self.SO_NGAY_NGHI)
        if self.SO_NGAY_NGHI is not None and so_ngay is not None:
            if so_ngay < 1:
                errs.append(
                    f"SO_NGAY_NGHI: '{self.SO_NGAY_NGHI}' phải >= 1"
                )
            elif so_ngay > 180:
                errs.append(
                    f"SO_NGAY_NGHI: '{self.SO_NGAY_NGHI}' vượt quá 180 ngày "
                    "(tối đa tuyệt đối theo TT 18/2022/TT-BYT)"
                )
            elif so_ngay > 50:
                errs.append(
                    f"SO_NGAY_NGHI: '{self.SO_NGAY_NGHI}' vượt 50 ngày – "
                    "chỉ hợp lệ với bệnh lao (tối đa 180 ngày), "
                    "kiểm tra lại chẩn đoán"
                )
            elif so_ngay > 30:
                errs.append(
                    f"SO_NGAY_NGHI: '{self.SO_NGAY_NGHI}' vượt 30 ngày – "
                    "chỉ hợp lệ với sẩy/phá/nạo/hút thai ≥13 tuần (tối đa 50) "
                    "hoặc bệnh lao (tối đa 180), kiểm tra lại chẩn đoán"
                )

        # ==================================================================
        # 14–15. TU_NGAY, DEN_NGAY – DATE8, DEN_NGAY >= TU_NGAY
        # ==================================================================
        dt_tu  = self._parse_date8(self.TU_NGAY)
        dt_den = self._parse_date8(self.DEN_NGAY)

        if self.TU_NGAY and dt_tu is None:
            errs.append(
                f"TU_NGAY: '{self.TU_NGAY}' không phải ngày hợp lệ (định dạng yyyymmdd)"
            )
        if self.DEN_NGAY and dt_den is None:
            errs.append(
                f"DEN_NGAY: '{self.DEN_NGAY}' không phải ngày hợp lệ (định dạng yyyymmdd)"
            )
        if isinstance(dt_tu, datetime) and isinstance(dt_den, datetime):
            if dt_den < dt_tu:
                errs.append(
                    f"DEN_NGAY ({self.DEN_NGAY}) không được trước "
                    f"TU_NGAY ({self.TU_NGAY})"
                )
            # Cross-field: SO_NGAY_NGHI phải = DEN_NGAY - TU_NGAY + 1
            if so_ngay is not None and so_ngay >= 1:
                expected = (dt_den.date() - dt_tu.date()).days + 1
                if expected != so_ngay:
                    errs.append(
                        f"SO_NGAY_NGHI: kỳ vọng {expected} ngày "
                        f"(DEN_NGAY − TU_NGAY + 1, tính cả 2 đầu), "
                        f"thực tế {so_ngay}"
                    )

        # ==================================================================
        # 20. NGAY_CT – DATE8
        #    Phải trùng với TU_NGAY (khám 1 ngày)
        #    hoặc nằm trong [TU_NGAY, DEN_NGAY] (khám nhiều ngày)
        # ==================================================================
        dt_ct = self._parse_date8(self.NGAY_CT)
        if self.NGAY_CT and dt_ct is None:
            errs.append(
                f"NGAY_CT: '{self.NGAY_CT}' không phải ngày hợp lệ (định dạng yyyymmdd)"
            )
        if isinstance(dt_ct, datetime):
            if isinstance(dt_tu, datetime) and dt_ct.date() < dt_tu.date():
                errs.append(
                    f"NGAY_CT ({self.NGAY_CT}) không được trước "
                    f"ngày bắt đầu hưởng chế độ TU_NGAY ({self.TU_NGAY})"
                )
            if isinstance(dt_den, datetime) and dt_ct.date() > dt_den.date():
                errs.append(
                    f"NGAY_CT ({self.NGAY_CT}) không được sau "
                    f"ngày kết thúc hưởng chế độ DEN_NGAY ({self.DEN_NGAY})"
                )

        # ==================================================================
        # 22. MAU_SO – nếu điền phải là "CT07" (mặc định hệ thống tự điền)
        # ==================================================================
        if self.MAU_SO and str(self.MAU_SO).strip().upper() != "CT07":
            errs.append(
                f"MAU_SO: '{self.MAU_SO}' không hợp lệ. "
                "Giấy nghỉ hưởng BHXH phải dùng mẫu CT07 "
                "(để trống thì hệ thống tự điền CT07)"
            )

        return errs