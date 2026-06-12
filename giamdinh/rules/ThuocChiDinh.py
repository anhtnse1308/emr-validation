"""
Rule II – Chỉ định thuốc không đúng quy định (mã từ chối S059.2, S079.1)
Căn cứ:
  - TT 05/2015/TT-BYT ngày 17/3/2015 (Danh mục thuốc YHCT – S059.2)
  - TT 30/2018/TT-BYT + TT 01/2020/TT-BYT (Kháng sinh đặc biệt – S079.1)

Nhóm S059.2 – Thuốc YHCT dùng ngoài giới hạn chỉ định:
  Phát hiện qua: MA_THUOC (XML2) + MA_BENH_CHINH/MA_BENH_KT (XML1) cùng MA_LK

Nhóm S079.1 – Kháng sinh đặc biệt sử dụng không đúng hạng bệnh viện:
  Phát hiện qua: MA_THUOC (XML2) + MA_CSKCB (XML1)
  Hạng BV được mã hóa qua MA_CSKCB → cần map bên ngoài hoặc dùng danh sách whitelist
"""

from giamdinh.GiamDinhBase import GiamDinhBase, GiamDinhError

# ---------------------------------------------------------------------------
# S059.2 – Thuốc YHCT giới hạn chỉ định
# Cấu trúc: mã_chi_phi → (set ICD-10 hợp lệ, tên thuốc, mô tả giới hạn)
# ---------------------------------------------------------------------------
THUOC_YHCT_GIOI_HAN: dict[str, tuple[set, str, str]] = {
    "05c.53": (
        {"M16", "M17"},  # Thoái hóa khớp hông (M16), khớp gối (M17)
        "Cao avocado/soya không xà phòng hóa (05c.53)",
        "Chỉ thanh toán điều trị thoái hóa khớp hông và khớp gối (M16, M17)",
    ),
    "05c.103": (
        {"K52"},  # Viêm đại tràng mạn tính không xác định nhiễm khuẩn
        "Ngưu nhĩ phong, La liễu (05c.103)",
        "Chỉ thanh toán điều trị viêm đại tràng mạn tính (K52)",
    ),
}

# ---------------------------------------------------------------------------
# S079.1 – Kháng sinh đặc biệt theo hạng bệnh viện
# Chỉ được dùng tại BV hạng đặc biệt, hạng I, hạng II, BV lao-phổi
# ---------------------------------------------------------------------------
KHANG_SINH_DAC_BIET: dict[str, str] = {
    "40.168": "Cefepim",
    "40.176": "Cefpirom",
    "40.183": "Ceftriaxon",
    "40.188": "Imipenem + cilastatin",
    "40.189": "Meropenem",
    "40.192": "Piperacillin + tazobactam",
    "40.196": "Ticarcillin + acid clavulanic",
    "40.258": "Vancomycin",
}

# Prefix MA_CSKCB cho BV hạng đặc biệt / I / II / BV Lao-Phổi
# Thực tế cần map đầy đủ từ danh mục BHYT; đây là placeholder
# Cấu trúc: set mã CSKCB được phép dùng kháng sinh đặc biệt
# Bệnh viện hạng đặc biệt: BV Bạch Mai (01000), Chợ Rẫy (75404), ...
CSKCB_HANG_DUOC_PHEP: set[str] = {
    "01000",  # BV Bạch Mai
    "75404",  # BV Chợ Rẫy
    "01001",  # BV Việt Đức
    "01002",  # BV K
    "01003",  # BV Nhi TW
    "75405",  # BV Từ Dũ
    # ... Thêm đầy đủ theo danh mục BYT
    # Lưu ý: danh sách này cần được duy trì theo QĐ phân hạng BV hiện hành
}

# Nếu không có danh sách whitelist đầy đủ, chuyển sang chế độ WARN thay vì ERROR
# Đặt = True để chỉ cảnh báo, không từ chối cứng
KHANG_SINH_WARN_ONLY = True

CAN_CU_YHCT = "TT 05/2015/TT-BYT ngày 17/3/2015 (Danh mục thuốc đông y/YHCT BHYT)"
CAN_CU_KHANG_SINH = "TT 30/2018/TT-BYT + TT 01/2020/TT-BYT (khoản 3 Điều 4 + khoản 1 Điều 1)"


def _icd_in_group(icd_val: str, allowed_icd: set) -> bool:
    """Kiểm tra ICD có nằm trong nhóm được phép không (prefix match)."""
    if not icd_val:
        return False
    codes = [c.strip() for c in str(icd_val).split(";") if c.strip()]
    for code in codes:
        for ref in allowed_icd:
            if code == ref or code.startswith(ref):
                return True
    return False


class ThuocChiDinh(GiamDinhBase):
    """
    Rule II: Thuốc YHCT ngoài giới hạn chỉ định (S059.2)
             + Kháng sinh đặc biệt sai hạng BV (S079.1)
    """

    def check(self, all_objects: dict) -> list[GiamDinhError]:
        errors: list[GiamDinhError] = []

        # Lấy chẩn đoán và mã CSKCB từ XML1
        xml1_map: dict[str, dict] = {}
        for _, rec in self._get_rows(all_objects, "XML1"):
            ma_lk = getattr(rec, "MA_LK", None) or ""
            if ma_lk:
                xml1_map[ma_lk] = {
                    "MA_BENH_CHINH": getattr(rec, "MA_BENH_CHINH", "") or "",
                    "MA_BENH_KT": getattr(rec, "MA_BENH_KT", "") or "",
                    "MA_CSKCB": getattr(rec, "MA_CSKCB", "") or "",
                }

        # Kiểm tra từng dòng thuốc trong XML2
        for row_excel, rec in self._get_rows(all_objects, "XML2"):
            ma_lk = getattr(rec, "MA_LK", None) or ""
            ma_thuoc = (getattr(rec, "MA_THUOC", None) or "").strip()
            if not ma_lk or not ma_thuoc:
                continue

            info = xml1_map.get(ma_lk, {})
            icd_chinh = info.get("MA_BENH_CHINH", "")
            icd_kt = info.get("MA_BENH_KT", "")
            ma_cskcb = info.get("MA_CSKCB", "")

            # ==============================================================
            # S059.2 – Thuốc YHCT ngoài giới hạn chỉ định
            # ==============================================================
            if ma_thuoc in THUOC_YHCT_GIOI_HAN:
                allowed_icd, ten_thuoc, gioi_han = THUOC_YHCT_GIOI_HAN[ma_thuoc]
                if not (_icd_in_group(icd_chinh, allowed_icd) or
                        _icd_in_group(icd_kt, allowed_icd)):
                    errors.append(GiamDinhError(
                        sheet="XML2",
                        ma_lk=ma_lk,
                        row_excel=row_excel,
                        ma_ly_do="S059.2",
                        mo_ta=(
                            f"Thuốc '{ten_thuoc}' chỉ định không đúng giới hạn. "
                            f"{gioi_han}. "
                            f"Chẩn đoán hiện tại: ICD chính={icd_chinh or '(trống)'}, "
                            f"ICD kèm={icd_kt or '(trống)'}. "
                            "Từ chối thanh toán."
                        ),
                        can_cu=CAN_CU_YHCT,
                        ma_dich_vu=ma_thuoc,
                    ))

            # ==============================================================
            # S079.1 – Kháng sinh đặc biệt sai hạng BV
            # ==============================================================
            if ma_thuoc in KHANG_SINH_DAC_BIET:
                ten_ks = KHANG_SINH_DAC_BIET[ma_thuoc]
                is_allowed_bv = (
                    ma_cskcb in CSKCB_HANG_DUOC_PHEP
                    if CSKCB_HANG_DUOC_PHEP
                    else True  # nếu whitelist rỗng thì không check
                )

                if not is_allowed_bv:
                    ma_ly_do = "S079.1"
                    errors.append(GiamDinhError(
                        sheet="XML2",
                        ma_lk=ma_lk,
                        row_excel=row_excel,
                        ma_ly_do=ma_ly_do,
                        mo_ta=(
                            f"Kháng sinh đặc biệt '{ten_ks}' (mã {ma_thuoc}) "
                            f"sử dụng tại CSKCB '{ma_cskcb}' không đúng hạng bệnh viện quy định "
                            "(chỉ được dùng tại BV hạng đặc biệt, I, II hoặc BV Lao-Phổi). "
                            "Kiểm tra có dùng kèm DVKT được phê duyệt không trước khi từ chối."
                        ),
                        can_cu=CAN_CU_KHANG_SINH,
                        ma_dich_vu=ma_thuoc,
                    ))
                elif KHANG_SINH_WARN_ONLY and not CSKCB_HANG_DUOC_PHEP:
                    # Whitelist chưa đầy đủ → cảnh báo để kiểm tra thủ công
                    errors.append(GiamDinhError(
                        sheet="XML2",
                        ma_lk=ma_lk,
                        row_excel=row_excel,
                        ma_ly_do="S079.1-WARN",
                        mo_ta=(
                            f"[CẦN KIỂM TRA] Kháng sinh đặc biệt '{ten_ks}' (mã {ma_thuoc}) "
                            f"tại CSKCB '{ma_cskcb}'. "
                            "Cần xác minh hạng BV và điều kiện sử dụng theo TT 30/2018."
                        ),
                        can_cu=CAN_CU_KHANG_SINH,
                        ma_dich_vu=ma_thuoc,
                    ))

        return errors