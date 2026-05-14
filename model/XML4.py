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
    # -----------------------------------------------------------------------
    # Helpers nội bộ (giống XML3, không phụ thuộc BHYTBase)
    # -----------------------------------------------------------------------
    @staticmethod
    def _to_int(value) -> int | None:
        if value is None or str(value).strip() == "":
            return None
        try:
            return int(float(str(value).strip()))
        except (ValueError, TypeError):
            return None

    # -----------------------------------------------------------------------
    # validate() – Logic nghiệp vụ Bảng 4
    # Base class tự xử lý _MAX_LEN, _NUMERIC, _DATE12.
    # Override bổ sung: bắt buộc, format đặc biệt, cross-field.
    # -----------------------------------------------------------------------
    def validate(self) -> list[str]:
        errs: list[str] = []

        # ==================================================================
        # 1. MA_LK – bắt buộc, Chuỗi, max 100
        # ==================================================================
        if not self.MA_LK:
            errs.append("MA_LK: bắt buộc, không được để trống")

        # ==================================================================
        # 2. STT – số nguyên dương, tăng từ 1
        # ==================================================================
        stt = self._to_int(self.STT)
        if self.STT is not None and stt is not None and stt < 1:
            errs.append(f"STT: '{self.STT}' phải là số nguyên dương >= 1")

        # ==================================================================
        # 3. MA_DICH_VU – bắt buộc, Chuỗi, max 50
        #    Mã DVKT CLS theo QĐ 7603/QĐ-BYT
        # ==================================================================
        if not self.MA_DICH_VU:
            errs.append("MA_DICH_VU: bắt buộc, không được để trống")

        # ==================================================================
        # 4. MA_CHI_SO – Chuỗi, max 255
        #    QĐ mới: nếu chưa có mã → tạm thời mã hóa bằng tên chỉ số
        #    (viết liền, không dấu, không khoảng trắng, không ký tự đặc biệt)
        #    Chỉ ghi các chỉ số có đơn vị đo lường
        # ==================================================================
        if self.MA_CHI_SO:
            # Phát hiện chuỗi "tạm thời" (không có mã chuẩn): không chứa '.' và toàn chữ/số
            # → kiểm tra không có dấu tiếng Việt và không có khoảng trắng
            if " " in self.MA_CHI_SO:
                errs.append(
                    f"MA_CHI_SO: '{self.MA_CHI_SO}' chứa khoảng trắng. "
                    "Trường hợp chưa có mã chuẩn, mã hoá bằng tên viết liền không dấu "
                    "(VD: 'glucosetoan' thay vì 'glucose toàn phần')"
                )

        # ==================================================================
        # 5. TEN_CHI_SO – Chuỗi, max 255
        #    QĐ mới: chỉ ghi các chỉ số có đơn vị đo lường
        # ==================================================================
        # (Không có validate bổ sung ngoài _MAX_LEN của base class)

        # ==================================================================
        # 6. GIA_TRI – Chuỗi, max 255
        #    QĐ mới: chỉ ghi chỉ số có đơn vị đo lường
        #    Có thể để trống khi chưa có kết quả (gửi thay thế sau)
        # ==================================================================
        # (Không validate bắt buộc – để trống hợp lệ)

        # ==================================================================
        # 7. DON_VI_DO – Chuỗi, max 50
        #    QĐ mới: để trống nếu chỉ số không có đơn vị đo
        # ==================================================================
        # (Không validate bắt buộc)

        # ==================================================================
        # Cross-field: DON_VI_DO có giá trị
        #   → MA_CHI_SO và TEN_CHI_SO phải có giá trị (tính nhất quán)
        # ==================================================================
        if self.DON_VI_DO:
            if not self.MA_CHI_SO:
                errs.append(
                    "MA_CHI_SO: bắt buộc khi DON_VI_DO có giá trị "
                    f"(DON_VI_DO='{self.DON_VI_DO}')"
                )
            if not self.TEN_CHI_SO:
                errs.append(
                    "TEN_CHI_SO: bắt buộc khi DON_VI_DO có giá trị "
                    f"(DON_VI_DO='{self.DON_VI_DO}')"
                )

        # ==================================================================
        # Cross-field: GIA_TRI có giá trị → KET_LUAN phải để trống
        #    QĐ mới: "Trường hợp xét nghiệm có kết quả xác định ở GIA_TRI
        #             thì để trống trường KET_LUAN"
        #    Lý do: tránh trùng lặp thông tin số + diễn giải văn bản
        # ==================================================================
        if self.GIA_TRI and self.KET_LUAN:
            errs.append(
                f"KET_LUAN: phải để trống khi GIA_TRI đã có giá trị ('{self.GIA_TRI}'). "
                "Theo QĐ mới: GIA_TRI dùng cho kết quả số, KET_LUAN dùng cho kết luận văn bản"
            )

        # ==================================================================
        # Cross-field: MO_TA / KET_LUAN – dùng cho CĐHA, TDCN, GPB
        #    Khi không có GIA_TRI → nên có MO_TA hoặc KET_LUAN
        # ==================================================================
        if not self.GIA_TRI and not self.MO_TA and not self.KET_LUAN:
            # Chỉ cảnh báo nếu có MA_CHI_SO (tức là dịch vụ có kết quả)
            if self.MA_CHI_SO:
                errs.append(
                    "GIA_TRI, MO_TA, KET_LUAN: ít nhất 1 trường phải có giá trị "
                    "khi MA_CHI_SO đã được khai báo"
                )

        # ==================================================================
        # 11. MA_BS_DOC_KQ – Chuỗi, max 255
        #    Định dạng QĐ mới (3 trường hợp):
        #    a) Thông thường   : <GPHN>           (chuỗi mã bác sĩ)
        #    b) Khám từ xa     : <GPHN>.TX.<XXXXX> (TX + mã cơ sở hỗ trợ)
        #    c) Chuyển giao KT : <GPHN>.CG.<XXXXX> (CG + mã cơ sở chuyển giao)
        #    Không bắt buộc khi chuyển gửi XN (MA_CHI_SO rỗng)
        # ==================================================================
        if self.MA_BS_DOC_KQ:
            val = str(self.MA_BS_DOC_KQ).strip()
            # Có chứa dấu "." → phải đúng format <GPHN>.<TX|CG>.<XXXXX>
            if "." in val:
                parts = val.split(".")
                if len(parts) != 3:
                    errs.append(
                        f"MA_BS_DOC_KQ: '{val}' sai định dạng. "
                        "Phải là <GPHN>.TX.<MaCsKbcb> hoặc <GPHN>.CG.<MaCsKbcb>"
                    )
                else:
                    gphn, loai, ma_cs = parts
                    if not gphn.strip():
                        errs.append(
                            f"MA_BS_DOC_KQ: thiếu mã GPHN bác sĩ trong '{val}'"
                        )
                    if loai.upper() not in {"TX", "CG"}:
                        errs.append(
                            f"MA_BS_DOC_KQ: loại '{loai}' không hợp lệ trong '{val}', "
                            "chỉ chấp nhận TX (từ xa) hoặc CG (chuyển giao kỹ thuật)"
                        )
                    if not ma_cs.strip():
                        errs.append(
                            f"MA_BS_DOC_KQ: thiếu mã cơ sở KBCB trong '{val}'"
                        )

        return errs