from dataclasses import dataclass, field, fields
from typing import Optional, ClassVar, Dict, Any
import re
from model.BHYTBase import BHYTBase

# ===========================================================================
# BẢNG 13 – Giấy chuyển tuyến / chuyển cơ sở KBCB BHYT
# Cập nhật theo QĐ 4750/QĐ-BYT:
#   - MA_NOI_DI   → đổi tên MA_CSKCB_DI  (size 100, multi-value ";")
#   - MA_NOI_DEN  → đổi tên MA_CSKCB_DEN (size 5)
#   - PP_DIEU_TRI → đổi tên TINH_TRANG_CT (size=n; tình trạng BN khi chuyển)
#   - TEN_DICH_VU : BỎ (STT 28)
#   - TEN_THUOC   : BỎ (STT 29)
#   - MA_BAC_SI   : diễn giải mới – mã GPHN; huy động/điều động: GPHN.HD.XXXXX
#   - MA_TTDV     : diễn giải mới – mã GPHN người ký; size 255
#   - DU_PHONG    : bổ sung – lưu chữ ký số cơ sở KBCB
#   - Ghi chú spec: Bảng 13 CHỈ gửi khi MA_LOAI_RV ∈ {2, 5}
#   - Implement validate() đầy đủ
# ===========================================================================

@dataclass
class Bang13_GiayChuyenTuyen(BHYTBase):
    """Bảng 13. Chỉ tiêu dữ liệu giấy chuyển tuyến/chuyển cơ sở KBCB BHYT."""

    MA_LK: Optional[str] = None
    SO_HOSO: Optional[str] = None
    SO_CHUYENTUYEN: Optional[str] = None
    GIAY_CHUYEN_TUYEN: Optional[str] = None
    MA_CSKCB: Optional[str] = None          # [size=5; mã CS cấp giấy chuyển]
    MA_CSKCB_DI: Optional[str] = None       # [QĐ 4750: đổi từ MA_NOI_DI; size=100; multi ";"]
    MA_CSKCB_DEN: Optional[str] = None      # [QĐ 4750: đổi từ MA_NOI_DEN; size=5]
    HO_TEN: Optional[str] = None
    NGAY_SINH: Optional[str] = None
    GIOI_TINH: Optional[str] = None
    MA_QUOCTICH: Optional[str] = None
    MA_DANTOC: Optional[str] = None
    MA_NGHE_NGHIEP: Optional[str] = None
    DIA_CHI: Optional[str] = None
    MA_THE_BHYT: Optional[str] = None       # [size=n; multi-value ";"]
    GT_THE_DEN: Optional[str] = None        # [size=n]
    NGAY_VAO: Optional[str] = None          # [size=100; tham chiếu Bảng 1]
    NGAY_VAO_NOI_TRU: Optional[str] = None
    NGAY_RA: Optional[str] = None           # [size=100; tham chiếu Bảng 1]
    DAU_HIEU_LS: Optional[str] = None       # [size=n]
    CHAN_DOAN_RV: Optional[str] = None      # [size=n]
    QT_BENHLY: Optional[str] = None         # [size=n]
    TOMTAT_KQ: Optional[str] = None         # [size=n]
    PP_DIEUTRI: Optional[str] = None        # [size=n; QĐ 4750: pp/thủ thuật/kỹ thuật/thuốc đã dùng]
    MA_BENH_CHINH: Optional[str] = None
    MA_BENH_KT: Optional[str] = None
    MA_BENH_YHCT: Optional[str] = None
    # TEN_DICH_VU: BỎ theo QĐ 4750 (STT 28)
    # TEN_THUOC  : BỎ theo QĐ 4750 (STT 29)
    TINH_TRANG_CT: Optional[str] = None     # [QĐ 4750: đổi từ PP_DIEU_TRI; size=n; tình trạng BN khi chuyển]
    MA_LOAI_RV: Optional[str] = None        # [Số; Bảng 13 CHỈ gửi khi = 2 hoặc 5]
    MA_LYDO_CT: Optional[str] = None        # [Số; 1=đủ điều kiện / 2=không đáp ứng / 3=theo yêu cầu BN]
    HUONG_DIEU_TRI: Optional[str] = None    # [size=n]
    PHUONGTIEN_VC: Optional[str] = None
    HOTEN_NGUOI_HT: Optional[str] = None
    CHUCDANH_NGUOI_HT: Optional[str] = None
    MA_BAC_SI: Optional[str] = None         # [size=255; mã GPHN; huy động: GPHN.HD.XXXXX]
    MA_TTDV: Optional[str] = None           # [đổi -> Chuỗi, size=255; mã GPHN người ký]
    DU_PHONG: Optional[str] = None          # [size=n; QĐ 4750: lưu chữ ký số KBCB]

    _MAX_LEN: ClassVar[Dict[str, Optional[int]]] = {
        "MA_LK": 100, "SO_HOSO": 50, "SO_CHUYENTUYEN": 50,
        "GIAY_CHUYEN_TUYEN": 50, "MA_CSKCB": 5,
        "MA_CSKCB_DI": 100, "MA_CSKCB_DEN": 5,
        "HO_TEN": 255, "NGAY_SINH": 12, "GIOI_TINH": 1,
        "MA_QUOCTICH": 3, "MA_DANTOC": 2, "MA_NGHE_NGHIEP": 5,
        "DIA_CHI": 1024, "NGAY_VAO": 100, "NGAY_VAO_NOI_TRU": 12,
        "NGAY_RA": 100, "MA_BENH_CHINH": 7, "MA_BENH_KT": 100,
        "MA_BENH_YHCT": 255,
        # TEN_DICH_VU, TEN_THUOC: đã bỏ
        # TINH_TRANG_CT, DAU_HIEU_LS, CHAN_DOAN_RV, QT_BENHLY,
        # TOMTAT_KQ, PP_DIEUTRI, HUONG_DIEU_TRI, DU_PHONG: size=n
        "MA_LOAI_RV": 1, "MA_LYDO_CT": 1,
        "PHUONGTIEN_VC": 255, "HOTEN_NGUOI_HT": 255,
        "CHUCDANH_NGUOI_HT": 255, "MA_BAC_SI": 255, "MA_TTDV": 255,
    }
    _NUMERIC: ClassVar[set] = {"GIOI_TINH", "MA_LOAI_RV", "MA_LYDO_CT"}
    _DATE12: ClassVar[set] = {"NGAY_SINH", "NGAY_VAO_NOI_TRU"}

    # -----------------------------------------------------------------------
    # validate() – Logic nghiệp vụ Bảng 13
    # Base class tự xử lý _MAX_LEN, _NUMERIC, _DATE12.
    # Override: bắt buộc, enum, MA_LOAI_RV chỉ {2,5}, MA_BAC_SI format.
    # -----------------------------------------------------------------------
    def validate(self) -> list[str]:
        errs: list[str] = super().validate()

        # ==================================================================
        # 1. MA_LK – bắt buộc
        # ==================================================================
        if not self.MA_LK:
            errs.append("MA_LK: bắt buộc, không được để trống")

        # ==================================================================
        # 10. GIOI_TINH – Số, 1 ký tự, enum {1=Nam / 2=Nữ / 3=Không XĐ}
        # ==================================================================
        gt = self._to_int(self.GIOI_TINH)
        if self.GIOI_TINH is not None and gt not in {1, 2, 3}:
            errs.append(
                f"GIOI_TINH: '{self.GIOI_TINH}' không hợp lệ "
                "(cần 1=Nam / 2=Nữ / 3=Chưa xác định)"
            )

        # ==================================================================
        # 6. MA_CSKCB_DI – Chuỗi, max 100
        #    QĐ 4750: nhiều cơ sở → phân cách ";", mỗi mã đúng 5 ký tự
        # ==================================================================
        if self.MA_CSKCB_DI:
            for idx, ma in enumerate(str(self.MA_CSKCB_DI).split(";")):
                ma = ma.strip()
                if not ma:
                    errs.append(
                        f"MA_CSKCB_DI: mục {idx + 1} rỗng "
                        "(kiểm tra dấu ';' thừa)"
                    )
                elif len(ma) != 5:
                    errs.append(
                        f"MA_CSKCB_DI: mã '{ma}' (mục {idx + 1}) "
                        f"phải đúng 5 ký tự, nhận {len(ma)} ký tự"
                    )

        # ==================================================================
        # 31. MA_LOAI_RV – Số, 1 ký tự, enum {1-5}
        #    Ghi chú spec: Bảng 13 CHỈ gửi khi MA_LOAI_RV ∈ {2, 5}
        #    2=Chuyển viện cùng tuyến / 5=Chuyển tuyến trên
        # ==================================================================
        _LOAI_RV_VALID = {1, 2, 3, 4, 5}
        _LOAI_RV_BANG13 = {2, 5}
        loai_rv = self._to_int(self.MA_LOAI_RV)
        if self.MA_LOAI_RV is not None:
            if loai_rv not in _LOAI_RV_VALID:
                errs.append(
                    f"MA_LOAI_RV: '{self.MA_LOAI_RV}' không hợp lệ "
                    f"(cần 1–5)"
                )
            elif loai_rv not in _LOAI_RV_BANG13:
                errs.append(
                    f"MA_LOAI_RV: '{self.MA_LOAI_RV}' – Bảng 13 chỉ trích chuyển "
                    "khi MA_LOAI_RV ∈ {2 (chuyển viện cùng tuyến), "
                    "5 (chuyển tuyến trên)}"
                )

        # ==================================================================
        # 32. MA_LYDO_CT – Số, 1 ký tự, enum {1, 2, 3}
        #    1=Đủ điều kiện chuyển / 2=Không đáp ứng khả năng / 3=Theo y/c BN
        # ==================================================================
        lydo = self._to_int(self.MA_LYDO_CT)
        if self.MA_LYDO_CT is not None and lydo not in {1, 2, 3}:
            errs.append(
                f"MA_LYDO_CT: '{self.MA_LYDO_CT}' không hợp lệ "
                "(cần 1=đủ điều kiện / 2=không đáp ứng khả năng / "
                "3=theo yêu cầu người bệnh)"
            )

        # ==================================================================
        # 37. MA_BAC_SI – Chuỗi, max 255
        #    QĐ 4750: mã GPHN người hành nghề chỉ định chuyển tuyến
        #    Trường hợp huy động/điều động: GPHN.HD.XXXXX
        #      XXXXX = mã 5 ký tự cơ sở KCB cử đi
        #           hoặc TT_XXX (2 ký tự mã tỉnh + XXX)
        #    Lưu ý: KHÔNG dùng TX/CG như Bảng 4; riêng Bảng 13 dùng HD
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
                            "Bảng 13 chỉ dùng HD (huy động/điều động)"
                        )
                    if not ma_cs.strip():
                        errs.append(
                            f"MA_BAC_SI: thiếu mã cơ sở KBCB trong '{val}'"
                        )

        return errs