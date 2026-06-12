"""
Rule II – Chỉ định thuốc không đúng quy định (S059.2, S079.1, S011.02)
Căn cứ:
  - TT 05/2015/TT-BYT  (Danh mục thuốc YHCT)
  - TT 30/2018/TT-BYT + TT 01/2020/TT-BYT (Kháng sinh đặc biệt, thuốc giới hạn chỉ định)

Cấu trúc mở rộng:
  THUOC_CCI_RULES  – thuốc có chống chỉ định theo ICD (S011.02)
  THUOC_GIOI_HAN   – thuốc chỉ thanh toán khi có ICD cụ thể (S059.2 / S006.119 / ...)
  KHANG_SINH_DAC_BIET – kháng sinh chỉ dùng tại BV hạng cao (S079.1)
"""

from giamdinh.GiamDinhBase import GiamDinhBase, GiamDinhError
from giamdinh.ICDHelper import ICDHelper

# ===========================================================================
# S011.02 – Thuốc chống chỉ định theo ICD
# Cấu trúc: ma_thuoc → (set ICD bị CCI, tên thuốc, mô tả, căn cứ)
# ===========================================================================
THUOC_CCI_RULES: dict[str, tuple] = {

    # Procoralan 5mg / 7.5mg – CCI: Sốc tim, NMCT cấp, Đau thắt ngực không ổn định
    "VN-15960-12": ({"R57.0", "I21", "I20.0"}, "Procoralan 5mg",
                    "CCI: sốc tim (R57.0), NMCT cấp (I21), đau thắt ngực không ổn định (I20.0)",
                    "TT 30/2018/TT-BYT khoản 2 Điều 3"),
    "VN-21893-19": ({"R57.0", "I21", "I20.0"}, "Procoralan 5mg",
                    "CCI: sốc tim, NMCT cấp, đau thắt ngực không ổn định",
                    "TT 30/2018/TT-BYT khoản 2 Điều 3"),
    "VN-15961-12": ({"R57.0", "I21", "I20.0"}, "Procoralan 7.5mg",
                    "CCI: sốc tim, NMCT cấp, đau thắt ngực không ổn định",
                    "TT 30/2018/TT-BYT khoản 2 Điều 3"),
    "VN-21894-19": ({"R57.0", "I21", "I20.0"}, "Procoralan 7.5mg",
                    "CCI: sốc tim, NMCT cấp, đau thắt ngực không ổn định",
                    "TT 30/2018/TT-BYT khoản 2 Điều 3"),

    # Melanov-M – CCI: ĐTĐ phụ thuộc insulin, suy gan, suy thận, COPD, suy tim
    "VN-20575-17": ({"E10", "K72", "N18", "N19", "J44", "I50"}, "Melanov-M",
                    "CCI: ĐTĐ phụ thuộc insulin (E10), suy gan (K72), "
                    "suy thận (N18/N19), COPD (J44), suy tim (I50)",
                    "TT 30/2018/TT-BYT khoản 2 Điều 3"),

    # Coryol 12.5mg – CCI: Suy tim, suy gan, hen phế quản
    "VN-18273-14": ({"I50", "K72", "J45", "J46"}, "Coryol 12.5mg",
                    "CCI: suy tim (I50), suy gan (K72), hen phế quản (J45/J46)",
                    "TT 30/2018/TT-BYT khoản 2 Điều 3"),

    # Neutrivit – CCI: U ác tính
    "VD-20671-14": ({"C00", "C01", "C02", "C03", "C04", "C05", "C06", "C07",
                     "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15",
                     "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23",
                     "C24", "C25", "C26", "C30", "C31", "C32", "C33", "C34",
                     "C37", "C38", "C39", "C40", "C41", "C43", "C44", "C45",
                     "C46", "C47", "C48", "C49", "C50", "C51", "C52", "C53",
                     "C54", "C55", "C56", "C57", "C58", "C60", "C61", "C62",
                     "C63", "C64", "C65", "C66", "C67", "C68", "C69", "C70",
                     "C71", "C72", "C73", "C74", "C75", "C76", "C77", "C78",
                     "C79", "C80", "C81", "C82", "C83", "C84", "C85", "C88",
                     "C90", "C91", "C92", "C93", "C94", "C95", "C96", "C97"},
                    "Neutrivit (VD-20671-14)",
                    "CCI: u ác tính (nhóm C00-C97)",
                    "TT 30/2018/TT-BYT khoản 2 Điều 3"),

    # Savi 3B – CCI: U ác tính (dùng chung ICD ung thư)
    "VD-30494-18": ({"C00", "C16", "C18", "C34", "C50", "C53", "C61",
                     "C64", "C71", "C80", "C81", "C91", "C92"},
                    "Savi 3B (VD-30494-18)",
                    "CCI: u ác tính",
                    "TT 30/2018/TT-BYT khoản 2 Điều 3"),

    # Gelactive Fort – CCI: Trẻ < 6 tuổi, suy thận nặng (TNT), tiền sản giật,
    #                        loét ruột kết, viêm ruột thừa, tắc ruột, hẹp môn vị
    # Lưu ý: CCI trẻ < 6 tuổi cần kiểm tra tuổi BN (xử lý trong check())
    "VD-20376-13": ({"N18.5", "N18.6", "O14", "K51", "K37", "K56", "K31.1"},
                    "Gelactive Fort (VD-20376-13)",
                    "CCI: suy thận nặng/TNT (N18.5/N18.6), tiền sản giật (O14), "
                    "loét ruột kết (K51), viêm RT (K37), tắc ruột (K56), hẹp môn vị (K31.1). "
                    "Lưu ý: cần kiểm tra thêm tuổi BN < 6 tuổi.",
                    "TT 30/2018/TT-BYT khoản 2 Điều 3"),
    "VD-32408-19": ({"N18.5", "N18.6", "O14", "K51", "K37", "K56", "K31.1"},
                    "Gelactive Fort (VD-32408-19)",
                    "CCI: suy thận nặng/TNT, tiền sản giật, loét ruột kết, "
                    "viêm RT, tắc ruột, hẹp môn vị.",
                    "TT 30/2018/TT-BYT khoản 2 Điều 3"),

    # Phalintop – CCI: Đái tháo đường
    "VD-24094-16": ({"E10", "E11", "E12", "E13", "E14"}, "Phalintop (VD-24094-16)",
                    "CCI: đái tháo đường (E10-E14)",
                    "TT 30/2018/TT-BYT khoản 2 Điều 3"),
}

# ===========================================================================
# S059.2 / S006.119 – Thuốc chỉ thanh toán khi có ICD cụ thể
# Cấu trúc: ma_thuoc → (set ICD được phép, tên thuốc, mô tả giới hạn, mã lý do, căn cứ)
# ===========================================================================
THUOC_GIOI_HAN: dict[str, tuple] = {

    # Cao avocado/soya (05c.53) – chỉ thoái hóa khớp hông (M16) hoặc gối (M17)
    "05c.53": (
        {"M16", "M17"},
        "Cao avocado/soya không xà phòng hóa (05c.53)",
        "Chỉ thanh toán điều trị thoái hóa khớp hông (M16) và khớp gối (M17)",
        "S059.2",
        "TT 05/2015/TT-BYT ngày 17/3/2015",
    ),

    # Ngưu nhĩ phong, La liễu (05c.103) – chỉ viêm đại tràng mạn tính
    "05c.103": (
        {"K52"},
        "Ngưu nhĩ phong, La liễu (05c.103)",
        "Chỉ thanh toán điều trị viêm đại tràng mạn tính (K52)",
        "S059.2",
        "TT 05/2015/TT-BYT ngày 17/3/2015",
    ),

    # Lysin+Vitamin+Khoáng chất (40.1042) – chỉ trẻ < 6 tuổi suy dinh dưỡng
    # ICD suy dinh dưỡng: E40-E46
    # Lưu ý: cần kiểm tra thêm tuổi BN < 6 (xử lý riêng trong check())
    "40.1042": (
        {"E40", "E41", "E42", "E43", "E44", "E45", "E46"},
        "Lysin+Vitamin+Khoáng chất (40.1042)",
        "Chỉ thanh toán trẻ em dưới 6 tuổi suy dinh dưỡng (E40-E46). "
        "Cần kiểm tra thêm tuổi BN.",
        "S006.119",
        "TT 30/2018/TT-BYT cột 8 Phụ lục 01",
    ),
}

# ===========================================================================
# S079.1 – Kháng sinh đặc biệt (chỉ BV hạng đặc biệt / I / II / lao-phổi)
# ===========================================================================
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

# Whitelist mã CSKCB được phép dùng kháng sinh đặc biệt
# Cần bổ sung đầy đủ theo danh mục phân hạng BV của BYT
CSKCB_HANG_DUOC_PHEP: set[str] = {
    "01000", "75404", "01001", "01002", "01003", "75405",
}

# True = chỉ cảnh báo khi whitelist chưa đầy đủ
KHANG_SINH_WARN_ONLY = True

CAN_CU_KS = "TT 30/2018/TT-BYT + TT 01/2020/TT-BYT (khoản 3 Điều 4 + khoản 1 Điều 1)"


class ThuocChiDinh(GiamDinhBase):
    """
    Rule II: Thuốc CCI theo ICD (S011.02)
             + Thuốc ngoài giới hạn chỉ định (S059.2 / S006.119)
             + Kháng sinh đặc biệt sai hạng BV (S079.1)
    """

    def check(self, all_objects: dict) -> list[GiamDinhError]:
        errors: list[GiamDinhError] = []

        # MA_LK → {icd, ma_cskcb}
        xml1_map: dict[str, dict] = {}
        for _, rec in self._get_rows(all_objects, "XML1"):
            ma_lk = getattr(rec, "MA_LK", None) or ""
            if ma_lk:
                xml1_map[ma_lk] = {
                    "icd":      ICDHelper.from_record(rec),
                    "cskcb":    getattr(rec, "MA_CSKCB", "") or "",
                    "ngay_sinh": getattr(rec, "NGAY_SINH", "") or "",
                    "ngay_vao":  getattr(rec, "NGAY_VAO",  "") or "",
                }

        for row_excel, rec in self._get_rows(all_objects, "XML2"):
            ma_lk   = getattr(rec, "MA_LK",   None) or ""
            ma_thuoc = (getattr(rec, "MA_THUOC", None) or "").strip()
            so_dang_ky = (getattr(rec, "SO_DANG_KY", None) or "").strip()
            if not ma_lk or not ma_thuoc:
                continue

            info    = xml1_map.get(ma_lk, {})
            icd: ICDHelper = info.get("icd", ICDHelper("", ""))
            cskcb   = info.get("cskcb", "")

            # ==============================================================
            # S011.02 – Thuốc CCI theo mã đăng ký (SO_DANG_KY)
            # ==============================================================
            lookup_key = so_dang_ky if so_dang_ky in THUOC_CCI_RULES else ma_thuoc
            if lookup_key in THUOC_CCI_RULES:
                cci_icd, ten_thuoc, mo_ta_cci, can_cu_cci = THUOC_CCI_RULES[lookup_key]
                if icd.has_any(cci_icd):
                    errors.append(GiamDinhError(
                        sheet="XML2", ma_lk=ma_lk, row_excel=row_excel,
                        ma_ly_do="S011.02",
                        mo_ta=(
                            f"Thuốc '{ten_thuoc}' ({lookup_key}) có chống chỉ định. "
                            f"{mo_ta_cci}. {icd}"
                        ),
                        can_cu=can_cu_cci,
                        ma_dich_vu=ma_thuoc,
                    ))

            # ==============================================================
            # S059.2 / S006.119 – Thuốc ngoài giới hạn chỉ định
            # ==============================================================
            if ma_thuoc in THUOC_GIOI_HAN:
                allowed_icd, ten_thuoc, gioi_han, ma_ldo, can_cu_gh = THUOC_GIOI_HAN[ma_thuoc]
                if not icd.has_any(allowed_icd):
                    errors.append(GiamDinhError(
                        sheet="XML2", ma_lk=ma_lk, row_excel=row_excel,
                        ma_ly_do=ma_ldo,
                        mo_ta=(
                            f"Thuốc '{ten_thuoc}' chỉ định ngoài giới hạn. "
                            f"{gioi_han}. {icd}"
                        ),
                        can_cu=can_cu_gh,
                        ma_dich_vu=ma_thuoc,
                    ))

            # ==============================================================
            # S079.1 – Kháng sinh đặc biệt sai hạng BV
            # ==============================================================
            if ma_thuoc in KHANG_SINH_DAC_BIET:
                ten_ks = KHANG_SINH_DAC_BIET[ma_thuoc]
                is_allowed = (cskcb in CSKCB_HANG_DUOC_PHEP
                              if CSKCB_HANG_DUOC_PHEP else True)

                if not is_allowed:
                    errors.append(GiamDinhError(
                        sheet="XML2", ma_lk=ma_lk, row_excel=row_excel,
                        ma_ly_do="S079.1",
                        mo_ta=(
                            f"Kháng sinh đặc biệt '{ten_ks}' (mã {ma_thuoc}) "
                            f"tại CSKCB '{cskcb}' không đúng hạng BV quy định. "
                            "Cần kiểm tra có dùng kèm DVKT được phê duyệt không."
                        ),
                        can_cu=CAN_CU_KS,
                        ma_dich_vu=ma_thuoc,
                    ))
                elif KHANG_SINH_WARN_ONLY and not CSKCB_HANG_DUOC_PHEP:
                    errors.append(GiamDinhError(
                        sheet="XML2", ma_lk=ma_lk, row_excel=row_excel,
                        ma_ly_do="S079.1-WARN",
                        mo_ta=(
                            f"[CẦN KIỂM TRA] Kháng sinh đặc biệt '{ten_ks}' "
                            f"(mã {ma_thuoc}) tại CSKCB '{cskcb}'. "
                            "Xác minh hạng BV và điều kiện sử dụng."
                        ),
                        can_cu=CAN_CU_KS,
                        ma_dich_vu=ma_thuoc,
                    ))

        return errors