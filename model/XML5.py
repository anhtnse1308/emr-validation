from dataclasses import dataclass, field, fields
from typing import Optional, ClassVar, Dict, Any
import re
from model.BHYTBase import BHYTBase

# ===========================================================================
# BẢNG 5 – Diễn biến lâm sàng
# ===========================================================================
 
@dataclass
class Bang5_DienBienLamSang(BHYTBase):
    """Bảng 5. Chỉ tiêu chi tiết diễn biến lâm sàng."""
 
    MA_LK: Optional[str] = None
    STT: Optional[str] = None
    DIEN_BIEN_LS: Optional[str] = None
    GIAI_DOAN_BENH: Optional[str] = None
    HOI_CHAN: Optional[str] = None
    PHAU_THUAT: Optional[str] = None
    THOI_DIEM_DBLS: Optional[str] = None
    NGUOI_THUC_HIEN: Optional[str] = None
    DU_PHONG: Optional[str] = None
 
    _MAX_LEN: ClassVar[Dict[str, Optional[int]]] = {
        "MA_LK": 100, "STT": 10,
        "THOI_DIEM_DBLS": 12, "NGUOI_THUC_HIEN": 255,
    }
    _NUMERIC: ClassVar[set] = {"STT"}
    _DATE12: ClassVar[set] = {"THOI_DIEM_DBLS"}
    # -----------------------------------------------------------------------
    # Helpers nội bộ
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
    # validate() – Logic nghiệp vụ Bảng 5
    # Base class tự xử lý _MAX_LEN, _NUMERIC, _DATE12.
    # Override bổ sung: bắt buộc, format CSST, format NGUOI_THUC_HIEN,
    #                   cross-field, ràng buộc ghi chú bảng.
    # -----------------------------------------------------------------------
    def validate(self) -> list[str]:
        errs: list[str] = []

        # ==================================================================
        # 1. MA_LK – bắt buộc
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
        # 3. DIEN_BIEN_LS – Chuỗi, max n
        #    QĐ mới: khi ghi chỉ số sinh tồn → dùng format chuẩn:
        #      CSST<M{mạch}_T{nhiệt độ}_HA{huyết áp}_NT{nhịp thở}_...>
        #    Kiểm tra: nếu có chuỗi "CSST" nhưng không đúng format → cảnh báo
        # ==================================================================
        if self.DIEN_BIEN_LS:
            dbls = str(self.DIEN_BIEN_LS)
            # Phát hiện có ghi sinh tồn nhưng không dùng tag CSST<>
            _SINHTON_KEYWORDS = ["mạch", "nhiệt độ", "huyết áp", "nhịp thở", "spo2", "hộ lý"]
            has_sinhton_text = any(k in dbls.lower() for k in _SINHTON_KEYWORDS)
            has_csst_tag = "CSST<" in dbls and ">" in dbls

            if has_sinhton_text and not has_csst_tag:
                errs.append(
                    "DIEN_BIEN_LS: phát hiện chỉ số sinh tồn nhưng chưa dùng format chuẩn. "
                    "Theo QĐ mới: ghi theo cấu trúc CSST<M{m}_T{t}_HA{ha}_NT{nt}_SP{sp}_HL{hl}>. "
                    "VD: \"CSST<M75_T37_HA120/70_NT18_HL2>\""
                )

            # Nếu có tag CSST<> → validate cấu trúc bên trong
            if has_csst_tag:
                csst_match = re.search(r"CSST<([^>]*)>", dbls)
                if csst_match:
                    inner = csst_match.group(1)
                    # Mỗi phần tử phải có dạng XX... (chữ hoa + giá trị)
                    parts = inner.split("_")
                    for p in parts:
                        if p and not re.match(r"^[A-Z]{1,3}[\d/\.]+$", p):
                            errs.append(
                                f"DIEN_BIEN_LS: chỉ số sinh tồn '{p}' trong CSST<> "
                                "sai định dạng. Phải là ký hiệu viết hoa + giá trị số "
                                "(VD: M75, T37, HA120/70, NT18, SP98, HL2)"
                            )
                            break  # chỉ báo lỗi đầu tiên, tránh spam

        # ==================================================================
        # 7. THOI_DIEM_DBLS – DATE12, đã validate bởi base class
        #    Thêm: kiểm tra thời điểm hợp lý (không phải tương lai)
        # ==================================================================
        if self.THOI_DIEM_DBLS and len(str(self.THOI_DIEM_DBLS)) == 12:
            from datetime import datetime
            try:
                dt = datetime.strptime(str(self.THOI_DIEM_DBLS), "%Y%m%d%H%M")
                if dt > datetime.now():
                    errs.append(
                        f"THOI_DIEM_DBLS: '{self.THOI_DIEM_DBLS}' là thời điểm tương lai, "
                        "kiểm tra lại"
                    )
                if dt.year < 2000:
                    errs.append(
                        f"THOI_DIEM_DBLS: '{self.THOI_DIEM_DBLS}' năm {dt.year} không hợp lý"
                    )
            except ValueError:
                errs.append(
                    f"THOI_DIEM_DBLS: '{self.THOI_DIEM_DBLS}' không phải ngày giờ hợp lệ "
                    "(yyyymmddHHMM). Kiểm tra tháng/ngày/giờ/phút"
                )

        # ==================================================================
        # 8. NGUOI_THUC_HIEN – Chuỗi, max 255
        #    QĐ mới: mã hóa theo số GPHN (giấy phép hành nghề)
        #            hoặc CCCD/định danh cá nhân (9 hoặc 12 chữ số)
        #    Nhiều người cách nhau ";", người chính ghi đầu tiên
        # ==================================================================
        if self.NGUOI_THUC_HIEN:
            nguoi_list = str(self.NGUOI_THUC_HIEN).split(";")
            for idx, nguoi in enumerate(nguoi_list):
                nguoi = nguoi.strip()
                if not nguoi:
                    errs.append(
                        f"NGUOI_THUC_HIEN: mục {idx + 1} rỗng "
                        "(kiểm tra dấu ';' thừa)"
                    )
                    continue
                # GPHN: số, có thể có chữ cái ở đầu (ví dụ: HN001234)
                # CCCD: 9 hoặc 12 chữ số thuần
                # → chỉ cần kiểm tra không có ký tự đặc biệt ngoài chữ/số
                if not re.fullmatch(r"[A-Za-z0-9/\.\-]+", nguoi):
                    errs.append(
                        f"NGUOI_THUC_HIEN: '{nguoi}' chứa ký tự không hợp lệ. "
                        "Phải là mã GPHN hoặc số CCCD/định danh cá nhân"
                    )

        # ==================================================================
        # Cross-field: ít nhất 1 trong 4 field nội dung phải có giá trị
        #    DIEN_BIEN_LS | GIAI_DOAN_BENH | HOI_CHAN | PHAU_THUAT
        #    (Record rỗng hoàn toàn không có ý nghĩa)
        # ==================================================================
        if not any([
            self.DIEN_BIEN_LS,
            self.GIAI_DOAN_BENH,
            self.HOI_CHAN,
            self.PHAU_THUAT,
        ]):
            errs.append(
                "DIEN_BIEN_LS / GIAI_DOAN_BENH / HOI_CHAN / PHAU_THUAT: "
                "ít nhất 1 trường phải có giá trị trong một record Bảng 5"
            )

        return errs