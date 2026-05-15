from dataclasses import dataclass, field, fields
from typing import Optional, ClassVar, Dict, Any
import re
from datetime import datetime
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
    # -----------------------------------------------------------------------
    # validate() – Logic nghiệp vụ Bảng 8
    # -----------------------------------------------------------------------
    def validate(self) -> list[str]:
        errs: list[str] = []

        # ==================================================================
        # 1. MA_LK – bắt buộc
        # ==================================================================
        if not self.MA_LK:
            errs.append("MA_LK: bắt buộc, không được để trống")

        # ==================================================================
        # 2. MA_LOAI_KCB – Chuỗi, max 2
        #    Enum hợp lệ (QĐ 4750 bổ sung 05, 06, 08, 09):
        #      02: ngoại trú | 03: nội trú | 04: nội trú ban ngày
        #      05: ngoại trú mạn tính (có khám + thuốc)
        #      06: lưu tại TYT/PKĐKKV
        #      08: ngoại trú mạn tính (có DVKT/thuốc)
        #      09: nội trú dưới 4 giờ
        #    Lưu ý: Bảng 8 CHỈ gửi khi MA_LOAI_KCB ∈ {03, 04, 06}
        # ==================================================================
        _LOAI_KCB_VALID   = {"02", "03", "04", "05", "06", "08", "09"}
        _LOAI_KCB_BANG8   = {"03", "04", "06"}

        if self.MA_LOAI_KCB:
            loai = str(self.MA_LOAI_KCB).strip().zfill(2)
            if loai not in _LOAI_KCB_VALID:
                errs.append(
                    f"MA_LOAI_KCB: '{self.MA_LOAI_KCB}' không hợp lệ. "
                    f"Chỉ chấp nhận {sorted(_LOAI_KCB_VALID)}"
                )
            elif loai not in _LOAI_KCB_BANG8:
                errs.append(
                    f"MA_LOAI_KCB: '{self.MA_LOAI_KCB}' – Bảng 8 chỉ gửi khi "
                    "MA_LOAI_KCB ∈ {03 (nội trú), 04 (nội trú ban ngày), 06 (lưu TYT/PKĐKKV)}"
                )

        # ==================================================================
        # 7-8. NGAY_VAO, NGAY_RA – parse + NGAY_RA >= NGAY_VAO
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
        # 17. KET_QUA_DTRI – Số, 1 ký tự, enum {1..8}
        #    QĐ 4750 bổ sung mã 8: Tử vong ngoại viện
        #    BUG cũ: chỉ validate 1..7
        # ==================================================================
        _KET_QUA_VALID = {1, 2, 3, 4, 5, 6, 7, 8}
        ket_qua = self._to_int(self.KET_QUA_DTRI)
        if self.KET_QUA_DTRI is not None and ket_qua is not None:
            if ket_qua not in _KET_QUA_VALID:
                errs.append(
                    f"KET_QUA_DTRI: '{self.KET_QUA_DTRI}' không hợp lệ. "
                    "Chỉ chấp nhận 1(Khỏi) 2(Đỡ) 3(Không đổi) 4(Nặng hơn) "
                    "5(Tử vong tại KBCB) 6(Tiên lượng nặng xin về) "
                    "7(Chưa xác định) 8(Tử vong ngoại viện)"
                )

        # ==================================================================
        # Nhóm con chết (14–16): NGAY_SINHCON, NGAY_CONCHET, SO_CONCHET
        #    Phải nhất quán: nếu có 1 → phải có đủ 3
        #    NGAY_CONCHET >= NGAY_SINHCON
        #    SO_CONCHET >= 1
        # ==================================================================
        dt_sinh = self._parse_date8(self.NGAY_SINHCON)
        dt_chet = self._parse_date8(self.NGAY_CONCHET)
        so_con  = self._to_int(self.SO_CONCHET)

        has_sinh = bool(self.NGAY_SINHCON) and self.NGAY_SINHCON != ''
        has_chet = bool(self.NGAY_CONCHET) and self.NGAY_CONCHET != ''
        has_so   = self.SO_CONCHET is not None and self.SO_CONCHET != ''

        if self.NGAY_SINHCON and dt_sinh is None:
            errs.append(
                f"NGAY_SINHCON: '{self.NGAY_SINHCON}' không phải ngày hợp lệ "
                "(định dạng yyyymmdd)"
            )
        if self.NGAY_CONCHET and dt_chet is None:
            errs.append(
                f"NGAY_CONCHET: '{self.NGAY_CONCHET}' không phải ngày hợp lệ "
                "(định dạng yyyymmdd)"
            )

        # Nếu bất kỳ field nào có → cả nhóm phải đủ
        if has_sinh or has_chet or has_so:
            if (not has_sinh and has_chet) or (not has_sinh and has_so):
                errs.append(
                    "NGAY_SINHCON: bắt buộc khi có thông tin con chết "
                    "(NGAY_CONCHET hoặc SO_CONCHET đã được ghi)"
                )
            if has_so and not has_chet:
                errs.append(
                    "NGAY_CONCHET: bắt buộc khi có thông tin con chết "
                    "(NGAY_SINHCON và SO_CONCHET đã được ghi)"
                )
            if has_chet and not has_so:
                errs.append(
                    "SO_CONCHET: bắt buộc khi có thông tin con chết "
                    "(NGAY_SINHCON và NGAY_CONCHET đã được ghi)"
                )

        # NGAY_CONCHET >= NGAY_SINHCON
        if isinstance(dt_sinh, datetime) and isinstance(dt_chet, datetime) and dt_chet < dt_sinh:
            errs.append(
                f"NGAY_CONCHET ({self.NGAY_CONCHET}) không được trước "
                f"NGAY_SINHCON ({self.NGAY_SINHCON})"
            )

        # SO_CONCHET >= 1
        if has_so and so_con is not None and so_con < 1:
            errs.append(
                f"SO_CONCHET: '{self.SO_CONCHET}' phải >= 1"
            )

        # NGAY_SINHCON phải trong khoảng NGAY_VAO..NGAY_RA
        if isinstance(dt_sinh, datetime) and isinstance(dt_vao, datetime) and dt_sinh.date() < dt_vao.date():
            errs.append(
                f"NGAY_SINHCON ({self.NGAY_SINHCON}) không được trước "
                f"NGAY_VAO ({str(self.NGAY_VAO)[:8]})"
            )
        if isinstance(dt_sinh, datetime) and isinstance(dt_ra, datetime) and dt_sinh.date() > dt_ra.date():
            errs.append(
                f"NGAY_SINHCON ({self.NGAY_SINHCON}) không được sau "
                f"NGAY_RA ({str(self.NGAY_RA)[:8]})"
            )

        # ==================================================================
        # 20. NGAY_CT – DATE8, >= NGAY_RA (ngày)
        # ==================================================================
        dt_ct = self._parse_date8(self.NGAY_CT)
        if self.NGAY_CT and dt_ct is None:
            errs.append(
                f"NGAY_CT: '{self.NGAY_CT}' không phải ngày hợp lệ "
                "(định dạng yyyymmdd)"
            )
        if isinstance(dt_ct, datetime) and isinstance(dt_ra, datetime) and dt_ct.date() < dt_ra.date():
            errs.append(
                f"NGAY_CT ({self.NGAY_CT}) không được trước ngày ra viện "
                f"NGAY_RA ({str(self.NGAY_RA)[:8]})"
            )

        return errs