from dataclasses import dataclass, field, fields
from typing import Optional, ClassVar, Dict, Any
import re
from datetime import datetime
from model.BHYTBase import BHYTBase

# ===========================================================================
# BẢNG 3 – DVKT & VTYT
# ===========================================================================
 
@dataclass
class Bang3_DVKT_VTYT(BHYTBase):
    """Bảng 3. Chỉ tiêu chi tiết dịch vụ kỹ thuật và vật tư y tế."""
 
    MA_LK: Optional[str] = None
    STT: Optional[str] = None
    MA_DICH_VU: Optional[str] = None
    MA_PTTT_QT: Optional[str] = None
    MA_VAT_TU: Optional[str] = None
    MA_NHOM: Optional[str] = None
    GOI_VTYT: Optional[str] = None
    TEN_VAT_TU: Optional[str] = None
    TEN_DICH_VU: Optional[str] = None
    MA_XANG_DAU: Optional[str] = None
    DON_VI_TINH: Optional[str] = None
    PHAM_VI: Optional[str] = None
    SO_LUONG: Optional[str] = None
    DON_GIA_BV: Optional[str] = None
    DON_GIA_BH: Optional[str] = None
    TT_THAU: Optional[str] = None           # [size -> 50]
    TYLE_TT_DV: Optional[str] = None
    TYLE_TT_BH: Optional[str] = None
    THANH_TIEN_BV: Optional[str] = None
    THANH_TIEN_BH: Optional[str] = None
    T_TRANTT: Optional[str] = None
    MUC_HUONG: Optional[str] = None
    T_NGUONKHAC_NSNN: Optional[str] = None
    T_NGUONKHAC_VTNN: Optional[str] = None
    T_NGUONKHAC_VTTN: Optional[str] = None
    T_NGUONKHAC_CL: Optional[str] = None
    T_NGUONKHAC: Optional[str] = None
    T_BNTT: Optional[str] = None
    T_BNCCT: Optional[str] = None
    T_BHTT: Optional[str] = None
    MA_KHOA: Optional[str] = None           # [size -> 50]
    MA_GIUONG: Optional[str] = None
    MA_BAC_SI: Optional[str] = None
    NGUOI_THUC_HIEN: Optional[str] = None
    MA_BENH: Optional[str] = None
    MA_BENH_YHCT: Optional[str] = None      # [size -> 150]
    NGAY_YL: Optional[str] = None
    NGAY_TH_YL: Optional[str] = None
    NGAY_KQ: Optional[str] = None
    MA_PTTT: Optional[str] = None
    VET_THUONG_TP: Optional[str] = None
    PP_VO_CAM: Optional[str] = None
    VI_TRI_TH_DVKT: Optional[str] = None
    MA_MAY: Optional[str] = None
    MA_HIEU_SP: Optional[str] = None
    TAI_SU_DUNG: Optional[str] = None
    DU_PHONG: Optional[str] = None
 
    _MAX_LEN: ClassVar[Dict[str, Optional[int]]] = {
        "MA_LK": 100, "STT": 10, "MA_DICH_VU": 50, "MA_PTTT_QT": 255,
        "MA_VAT_TU": 255, "MA_NHOM": 2, "GOI_VTYT": 3,
        "TEN_VAT_TU": 1024, "TEN_DICH_VU": 1024, "MA_XANG_DAU": 20,
        "DON_VI_TINH": 50, "PHAM_VI": 1, "SO_LUONG": 10,
        "DON_GIA_BV": 15, "DON_GIA_BH": 15, "TT_THAU": 50,
        "TYLE_TT_DV": 3, "TYLE_TT_BH": 3,
        "THANH_TIEN_BV": 15, "THANH_TIEN_BH": 15, "T_TRANTT": 15,
        "MUC_HUONG": 3,
        "T_NGUONKHAC_NSNN": 15, "T_NGUONKHAC_VTNN": 15,
        "T_NGUONKHAC_VTTN": 15, "T_NGUONKHAC_CL": 15, "T_NGUONKHAC": 15,
        "T_BNTT": 15, "T_BNCCT": 15, "T_BHTT": 15,
        "MA_KHOA": 50, "MA_GIUONG": 50, "MA_BAC_SI": 255,
        "NGUOI_THUC_HIEN": 255, "MA_BENH": 100, "MA_BENH_YHCT": 150,
        "NGAY_YL": 12, "NGAY_TH_YL": 12, "NGAY_KQ": 12,
        "MA_PTTT": 1, "VET_THUONG_TP": 1, "PP_VO_CAM": 1,
        "VI_TRI_TH_DVKT": 3, "MA_MAY": 1024, "MA_HIEU_SP": 255,
        "TAI_SU_DUNG": 1,
    }
    _NUMERIC: ClassVar[set] = {
        "STT", "MA_NHOM", "PHAM_VI", "SO_LUONG", "DON_GIA_BV", "DON_GIA_BH",
        "TYLE_TT_DV", "TYLE_TT_BH", "THANH_TIEN_BV", "THANH_TIEN_BH", "T_TRANTT",
        "MUC_HUONG", "T_NGUONKHAC_NSNN", "T_NGUONKHAC_VTNN", "T_NGUONKHAC_VTTN",
        "T_NGUONKHAC_CL", "T_NGUONKHAC", "T_BNTT", "T_BNCCT", "T_BHTT",
        "MA_PTTT", "VET_THUONG_TP", "PP_VO_CAM", "VI_TRI_TH_DVKT", "TAI_SU_DUNG",
    }
    _DATE12: ClassVar[set] = {"NGAY_YL", "NGAY_TH_YL", "NGAY_KQ"}
    # -----------------------------------------------------------------------
    # validate() – Toàn bộ logic nghiệp vụ Bảng 3
    # Base class tự xử lý _MAX_LEN, _NUMERIC, _DATE12.
    # Override này bổ sung: bắt buộc, enum, range, format, công thức, cross-field.
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
        # 3. MA_DICH_VU – Chuỗi, max 50
        #    Spec QĐ mới: suffix hợp lệ: _GT (gây tê), _TB (dừng kỹ thuật), _TT (gây tê chưa có giá)
        #    Vận chuyển: VC.XXXXX; CLS chuyển gửi: XX.YYYY.ZZZZ.K.WWWWW; chưa có giá: XX.YYYY.0000
        # ==================================================================
        if self.MA_DICH_VU:
            ma_dv_clean = re.sub(r"_(GT|TB|TT)$", "", self.MA_DICH_VU.strip())
            # Không validate sâu format mã do Bộ Y tế quản lý,
            # chỉ kiểm suffix hợp lệ
            if re.search(r"_[A-Z]{2}$", self.MA_DICH_VU):
                suffix = self.MA_DICH_VU.split("_")[-1]
                if suffix not in {"GT", "TB", "TT"}:
                    errs.append(
                        f"MA_DICH_VU: suffix '_{suffix}' không hợp lệ, "
                        "chỉ chấp nhận _GT (gây tê), _TB (dừng kỹ thuật), _TT (gây tê chưa có giá)"
                    )

        # ==================================================================
        # 6. MA_NHOM – Số, 2 ký tự, enum 1-19
        #    QĐ 4750 bổ sung mã 19: dịch vụ khác (tiền ăn, đi lại, lưu trú)
        # ==================================================================
        ma_nhom = self._to_int(self.MA_NHOM)
        if self.MA_NHOM is not None and ma_nhom is not None:
            if not (1 <= ma_nhom <= 19):
                errs.append(
                    f"MA_NHOM: '{self.MA_NHOM}' không hợp lệ, phải trong 1–19"
                )

        # ==================================================================
        # 7. GOI_VTYT – Chuỗi, max 3, format G<số> (G1, G2, ..., G99)
        # ==================================================================
        if self.GOI_VTYT:
            if not re.fullmatch(r"G[1-9]\d?", self.GOI_VTYT.strip()):
                errs.append(
                    f"GOI_VTYT: '{self.GOI_VTYT}' sai định dạng, "
                    "phải là G1, G2, … G99 (tối đa 3 ký tự)"
                )

        # ==================================================================
        # 12. PHAM_VI – Số, 1 ký tự, enum {1, 2, 3}
        #    1: BHYT thanh toán | 2: người bệnh tự trả | 3: quân đội/công an/cơ yếu
        # ==================================================================
        pham_vi = self._to_int(self.PHAM_VI)
        if self.PHAM_VI is not None and pham_vi is not None:
            if pham_vi not in {1, 2, 3}:
                errs.append(
                    f"PHAM_VI: '{self.PHAM_VI}' không hợp lệ, "
                    "chỉ chấp nhận 1 (BHYT) / 2 (tự trả) / 3 (quân đội/công an/cơ yếu)"
                )

        # ==================================================================
        # 13. SO_LUONG – Số, max 10, tối đa 3 chữ số thập phân, dùng dấu "."
        # ==================================================================
        sl = self._to_float(self.SO_LUONG)
        if self.SO_LUONG is not None and sl is not None:
            if "," in str(self.SO_LUONG):
                errs.append("SO_LUONG: dùng dấu chấm '.' thay vì dấu phẩy ',' cho số thập phân")
            elif self._decimal_places(self.SO_LUONG) > 3:
                errs.append(
                    f"SO_LUONG: '{self.SO_LUONG}' vượt quá 3 chữ số thập phân"
                )

        # ==================================================================
        # 14. DON_GIA_BV – Số, max 15, tối đa 3 chữ số thập phân, dùng dấu ".", >= 0
        # ==================================================================
        dgbv = self._to_float(self.DON_GIA_BV)
        if self.DON_GIA_BV is not None and dgbv is not None:
            if "," in str(self.DON_GIA_BV):
                errs.append("DON_GIA_BV: dùng dấu chấm '.' thay vì dấu phẩy ','")
            elif self._decimal_places(self.DON_GIA_BV) > 3:
                errs.append("DON_GIA_BV: vượt quá 3 chữ số thập phân")
            if dgbv < 0:
                errs.append("DON_GIA_BV: không được âm")

        # ==================================================================
        # 15. DON_GIA_BH – Số, max 15, tối đa 3 chữ số thập phân, dùng dấu ".", >= 0
        #    Lưu ý QĐ mới: khi VTYT có mức TT và DON_GIA_BV > mức TT → DON_GIA_BH = T_TRANTT
        # ==================================================================
        dgbh = self._to_float(self.DON_GIA_BH)
        if self.DON_GIA_BH is not None and dgbh is not None:
            if "," in str(self.DON_GIA_BH):
                errs.append("DON_GIA_BH: dùng dấu chấm '.' thay vì dấu phẩy ','")
            elif self._decimal_places(self.DON_GIA_BH) > 3:
                errs.append("DON_GIA_BH: vượt quá 3 chữ số thập phân")
            if dgbh < 0:
                errs.append("DON_GIA_BH: không được âm")

        # Kiểm tra: khi T_TRANTT có giá trị, DON_GIA_BV > T_TRANTT → DON_GIA_BH phải = T_TRANTT
        t_tran = self._to_float(self.T_TRANTT)
        if (dgbv is not None and dgbh is not None and t_tran is not None and t_tran > 0):
            if dgbv > t_tran and abs(dgbh - t_tran) > 0.001:
                errs.append(
                    f"DON_GIA_BH: khi DON_GIA_BV ({dgbv}) > T_TRANTT ({t_tran}), "
                    f"DON_GIA_BH phải = T_TRANTT ({t_tran}), thực tế {dgbh}"
                )

        # ==================================================================
        # 17. TYLE_TT_DV – Số, max 3, số nguyên, enum cố định {0,10,30,33,50,80,100}
        #    Hoặc bất kỳ giá trị nào trong 0-100 (trường hợp giảm giá BV)
        #    Các trường hợp còn lại TYLE_TT_DV ghi 100
        # ==================================================================
        _TYLE_DV_COMMON = {0, 10, 30, 33, 50, 80, 100}
        tyle_dv = self._to_int(self.TYLE_TT_DV)
        if self.TYLE_TT_DV is not None and tyle_dv is not None:
            if not (0 <= tyle_dv <= 100):
                errs.append(
                    f"TYLE_TT_DV: '{self.TYLE_TT_DV}' phải trong 0-100"
                )
            elif tyle_dv not in _TYLE_DV_COMMON:
                # Cảnh báo (warning) thay vì lỗi – có thể là trường hợp giảm giá BV
                errs.append(
                    f"TYLE_TT_DV: '{self.TYLE_TT_DV}' không thuộc tập thông thường "
                    f"{sorted(_TYLE_DV_COMMON)}. Kiểm tra lại nếu không phải trường hợp giảm đơn giá BV"
                )

        # ==================================================================
        # 18. TYLE_TT_BH – Số, max 3, số nguyên, 0-100
        #    0: ngoài phạm vi BHYT | 100: không quy định tỷ lệ | 50/75/...: theo quy định
        # ==================================================================
        tyle_bh = self._to_int(self.TYLE_TT_BH)
        if self.TYLE_TT_BH is not None and tyle_bh is not None:
            if not (0 <= tyle_bh <= 100):
                errs.append(
                    f"TYLE_TT_BH: '{self.TYLE_TT_BH}' không hợp lệ, phải trong 0–100"
                )

        # ==================================================================
        # 19. THANH_TIEN_BV – Số, max 15, tối đa 2 chữ số thập phân
        #    Công thức chính (QĐ mới): THANH_TIEN_BV = SO_LUONG * DON_GIA_BV * TYLE_TT_DV/100
        #    Trường hợp đặc biệt (BV không thu thêm chênh lệch BH):
        #      THANH_TIEN_BV = SO_LUONG*DON_GIA_BV - SO_LUONG*DON_GIA_BH*(100-TYLE_TT_DV)/100
        #    BUG cũ (QĐ 130): = SO_LUONG * DON_GIA_BV (thiếu TYLE_TT_DV)
        # ==================================================================
        ttbv = self._to_float(self.THANH_TIEN_BV)
        if self.THANH_TIEN_BV is not None and ttbv is not None:
            if "," in str(self.THANH_TIEN_BV):
                errs.append("THANH_TIEN_BV: dùng dấu chấm '.' thay vì dấu phẩy ','")
            elif self._decimal_places(self.THANH_TIEN_BV) > 2:
                errs.append("THANH_TIEN_BV: vượt quá 2 chữ số thập phân")
            if ttbv < 0:
                errs.append("THANH_TIEN_BV: không được âm")

        if sl is not None and dgbv is not None and tyle_dv is not None and ttbv is not None:
            # Công thức chuẩn
            expected_std = round(sl * dgbv * tyle_dv / 100, 2)
            # Công thức đặc biệt (BV không thu thêm)
            expected_special = None
            if dgbh is not None:
                expected_special = round(sl * dgbv - sl * dgbh * (100 - tyle_dv) / 100, 2)

            ok_std     = abs(ttbv - expected_std) <= 0.02
            ok_special = (expected_special is not None and abs(ttbv - expected_special) <= 0.02)

            if not ok_std and not ok_special:
                errs.append(
                    f"THANH_TIEN_BV: thực tế {ttbv}, "
                    f"kỳ vọng {expected_std} (SO_LUONG×DON_GIA_BV×TYLE_TT_DV/100) "
                    f"hoặc {expected_special} (trường hợp BV không thu thêm). "
                    "Công thức đã sửa đổi theo QĐ mới (không còn = SO_LUONG×DON_GIA_BV)"
                )

        # ==================================================================
        # 20. THANH_TIEN_BH – Số, max 15, tối đa 2 chữ số thập phân
        #    Công thức (QĐ mới – áp dụng thống nhất mọi trường hợp):
        #      THANH_TIEN_BH = SO_LUONG * DON_GIA_BH * TYLE_TT_DV/100 * TYLE_TT_BH/100
        #    BUG cũ (QĐ 130): = SO_LUONG * DON_GIA_BH * TYLE_TT_BH/100 (thiếu TYLE_TT_DV)
        # ==================================================================
        ttbh = self._to_float(self.THANH_TIEN_BH)
        if self.THANH_TIEN_BH is not None and ttbh is not None:
            if "," in str(self.THANH_TIEN_BH):
                errs.append("THANH_TIEN_BH: dùng dấu chấm '.' thay vì dấu phẩy ','")
            elif self._decimal_places(self.THANH_TIEN_BH) > 2:
                errs.append("THANH_TIEN_BH: vượt quá 2 chữ số thập phân")
            if ttbh < 0:
                errs.append("THANH_TIEN_BH: không được âm")

        if (sl is not None and dgbh is not None
                and tyle_dv is not None and tyle_bh is not None and ttbh is not None):
            expected_ttbh = round(sl * dgbh * tyle_dv / 100 * tyle_bh / 100, 2)
            if abs(ttbh - expected_ttbh) > 0.02:
                errs.append(
                    f"THANH_TIEN_BH: kỳ vọng {expected_ttbh} "
                    f"(SO_LUONG×DON_GIA_BH×TYLE_TT_DV/100×TYLE_TT_BH/100), "
                    f"thực tế {ttbh}"
                )

        # ==================================================================
        # 22. MUC_HUONG – Số, max 3, số nguyên, 0-100
        #    Đúng tuyến: 80/95/100; trái tuyến: nhân tỷ lệ (32=80%×40%, v.v.)
        # ==================================================================
        muc_huong = self._to_int(self.MUC_HUONG)
        if self.MUC_HUONG is not None and muc_huong is not None:
            if not (0 <= muc_huong <= 100):
                errs.append(
                    f"MUC_HUONG: '{self.MUC_HUONG}' không hợp lệ, phải trong 0–100"
                )

        # ==================================================================
        # 23-26. T_NGUONKHAC_* – Số, max 15, >= 0, tối đa 2 chữ số thập phân
        # ==================================================================
        nguon_nsnn = self._to_float(self.T_NGUONKHAC_NSNN) or 0.0
        nguon_vtnn = self._to_float(self.T_NGUONKHAC_VTNN) or 0.0
        nguon_vttn = self._to_float(self.T_NGUONKHAC_VTTN) or 0.0
        nguon_cl   = self._to_float(self.T_NGUONKHAC_CL)   or 0.0

        for fname, fval in [
            ("T_NGUONKHAC_NSNN", nguon_nsnn),
            ("T_NGUONKHAC_VTNN", nguon_vtnn),
            ("T_NGUONKHAC_VTTN", nguon_vttn),
            ("T_NGUONKHAC_CL",   nguon_cl),
        ]:
            raw = getattr(self, fname)
            if raw is not None:
                if fval < 0:
                    errs.append(f"{fname}: không được âm")
                if self._decimal_places(raw) > 2:
                    errs.append(f"{fname}: vượt quá 2 chữ số thập phân")

        # ==================================================================
        # 27. T_NGUONKHAC = tổng 4 nguồn
        #    QĐ mới: khi T_NGUONKHAC > 0 → giảm trừ lần lượt T_BNTT → T_BNCCT → T_BHTT
        # ==================================================================
        t_nguon = self._to_float(self.T_NGUONKHAC)
        if self.T_NGUONKHAC is not None and t_nguon is not None:
            if t_nguon < 0:
                errs.append("T_NGUONKHAC: không được âm")
            expected_nguon = round(nguon_nsnn + nguon_vtnn + nguon_vttn + nguon_cl, 2)
            if abs(t_nguon - expected_nguon) > 0.02:
                errs.append(
                    f"T_NGUONKHAC: kỳ vọng {expected_nguon} "
                    f"(T_NGUONKHAC_NSNN + VTNN + VTTN + CL), thực tế {t_nguon}"
                )
            # Ràng buộc: 0 < T_NGUONKHAC < THANH_TIEN_BV
            if ttbv is not None and t_nguon >= ttbv:
                errs.append(
                    f"T_NGUONKHAC ({t_nguon}) phải < THANH_TIEN_BV ({ttbv})"
                )

        # ==================================================================
        # Tính các giá trị tạm thời để kiểm tra T_BNTT, T_BNCCT, T_BHTT
        # Công thức tạm tính (QĐ mới):
        #   T_BHTT_TT  = THANH_TIEN_BH * MUC_HUONG / 100
        #   T_BNCCT_TT = THANH_TIEN_BH - T_BHTT_TT
        #   T_BNTT_TT  = THANH_TIEN_BV - THANH_TIEN_BH
        # Sau đó điều chỉnh nếu T_NGUONKHAC > 0 (giảm trừ theo thứ tự T_BNTT → T_BNCCT → T_BHTT)
        # ==================================================================
        t_bhtt_tt  = None
        t_bncct_tt = None
        t_bntt_tt  = None
        if ttbh is not None and muc_huong is not None:
            t_bhtt_tt  = round(ttbh * muc_huong / 100, 2)
            t_bncct_tt = round(ttbh - t_bhtt_tt, 2)
        if ttbv is not None and ttbh is not None:
            t_bntt_tt = round(ttbv - ttbh, 2)

        # Tính giá trị kỳ vọng sau khi điều chỉnh T_NGUONKHAC
        exp_bntt = exp_bncct = exp_bhtt = None
        if t_bntt_tt is not None and t_bncct_tt is not None and t_bhtt_tt is not None:
            nguon = t_nguon or 0.0
            # Giảm T_BNTT trước
            if nguon <= t_bntt_tt:
                exp_bntt  = round(t_bntt_tt - nguon, 2)
                exp_bncct = t_bncct_tt
                exp_bhtt  = t_bhtt_tt
            else:
                exp_bntt = 0.0
                du = nguon - t_bntt_tt
                if du <= t_bncct_tt:
                    exp_bncct = round(t_bncct_tt - du, 2)
                    exp_bhtt  = t_bhtt_tt
                else:
                    exp_bncct = 0.0
                    du2 = du - t_bncct_tt
                    exp_bhtt = round(max(t_bhtt_tt - du2, 0), 2)

        # ==================================================================
        # 30. T_BHTT – Số, max 15, >= 0, tối đa 2 chữ số thập phân
        #    Công thức QĐ mới: T_BHTT = THANH_TIEN_BH * MUC_HUONG/100
        #    Khi có T_NGUONKHAC: giảm trừ theo thứ tự ưu tiên
        # ==================================================================
        t_bhtt = self._to_float(self.T_BHTT)
        if self.T_BHTT is not None and t_bhtt is not None:
            if t_bhtt < 0:
                errs.append("T_BHTT: không được âm")
            if self._decimal_places(self.T_BHTT) > 2:
                errs.append("T_BHTT: vượt quá 2 chữ số thập phân")
            if exp_bhtt is not None and abs(t_bhtt - exp_bhtt) > 0.02:
                errs.append(
                    f"T_BHTT: kỳ vọng {exp_bhtt} "
                    f"(THANH_TIEN_BH×MUC_HUONG/100"
                    + (", đã điều chỉnh T_NGUONKHAC)" if t_nguon else ")") +
                    f", thực tế {t_bhtt}"
                )

        # ==================================================================
        # 29. T_BNCCT – Số, max 15, >= 0, tối đa 2 chữ số thập phân
        #    Công thức QĐ mới: T_BNCCT = THANH_TIEN_BH - T_BHTT
        # ==================================================================
        t_bncct = self._to_float(self.T_BNCCT)
        if self.T_BNCCT is not None and t_bncct is not None:
            if t_bncct < 0:
                errs.append("T_BNCCT: không được âm")
            if self._decimal_places(self.T_BNCCT) > 2:
                errs.append("T_BNCCT: vượt quá 2 chữ số thập phân")
            if exp_bncct is not None and abs(t_bncct - exp_bncct) > 0.02:
                errs.append(
                    f"T_BNCCT: kỳ vọng {exp_bncct} "
                    f"(THANH_TIEN_BH - T_BHTT"
                    + (", đã điều chỉnh T_NGUONKHAC)" if t_nguon else ")") +
                    f", thực tế {t_bncct}"
                )

        # ==================================================================
        # 28. T_BNTT – Số, max 15, >= 0, tối đa 2 chữ số thập phân
        #    Công thức QĐ mới: T_BNTT = THANH_TIEN_BV - THANH_TIEN_BH
        # ==================================================================
        t_bntt = self._to_float(self.T_BNTT)
        if self.T_BNTT is not None and t_bntt is not None:
            if t_bntt < 0:
                errs.append("T_BNTT: không được âm")
            if self._decimal_places(self.T_BNTT) > 2:
                errs.append("T_BNTT: vượt quá 2 chữ số thập phân")
            if exp_bntt is not None and abs(t_bntt - exp_bntt) > 0.02:
                errs.append(
                    f"T_BNTT: kỳ vọng {exp_bntt} "
                    f"(THANH_TIEN_BV - THANH_TIEN_BH"
                    + (", đã điều chỉnh T_NGUONKHAC)" if t_nguon else ")") +
                    f", thực tế {t_bntt}"
                )

        # ==================================================================
        # Cân đối tổng: THANH_TIEN_BV = T_BNTT + T_BNCCT + T_BHTT + T_NGUONKHAC
        # ==================================================================
        if (ttbv is not None and t_bntt is not None
                and t_bncct is not None and t_bhtt is not None):
            total = round(t_bntt + t_bncct + t_bhtt + (t_nguon or 0.0), 2)
            if abs(total - ttbv) > 0.05:
                errs.append(
                    f"Cân đối chi phí: THANH_TIEN_BV ({ttbv}) ≠ "
                    f"T_BNTT+T_BNCCT+T_BHTT+T_NGUONKHAC ({total})"
                )

        # ==================================================================
        # 32. MA_GIUONG – Chuỗi, max 50
        #    Format mỗi giường: [H|T|C|K]NNN (4 ký tự)
        #    Nhiều giường cách nhau ";", QĐ mới bãi bỏ ghi chú lưu ý cũ
        # ==================================================================
        if self.MA_GIUONG:
            for mg in str(self.MA_GIUONG).split(";"):
                mg = mg.strip()
                if mg and not re.fullmatch(r"[HTCK]\d{3}", mg):
                    errs.append(
                        f"MA_GIUONG: '{mg}' sai định dạng, "
                        "phải là [H|T|C|K] + 3 chữ số (H001/T002/C001/K001)"
                    )

        # ==================================================================
        # 37-39. Trật tự thời gian: NGAY_YL ≤ NGAY_TH_YL ≤ NGAY_KQ
        #        So sánh chuỗi hợp lệ vì format yyyymmddHHMM (lexicographic = chronological)
        # ==================================================================
        yl = str(self.NGAY_YL or "").strip()
        th = str(self.NGAY_TH_YL or "").strip()
        kq = str(self.NGAY_KQ or "").strip()

        if yl and th and len(yl) == 12 and len(th) == 12:
            if th < yl:
                errs.append(
                    f"NGAY_TH_YL ({th}) không được trước NGAY_YL ({yl})"
                )
        if th and kq and len(th) == 12 and len(kq) == 12:
            if kq < th:
                errs.append(
                    f"NGAY_KQ ({kq}) không được trước NGAY_TH_YL ({th})"
                )

        # ==================================================================
        # 40. MA_PTTT – Số, 1 ký tự, enum {1, 2, 3}
        #    1: phí dịch vụ | 2: định suất | 3: DRG
        # ==================================================================
        ma_pttt = self._to_int(self.MA_PTTT)
        if self.MA_PTTT is not None and ma_pttt is not None:
            if ma_pttt not in {1, 2, 3}:
                errs.append(
                    f"MA_PTTT: '{self.MA_PTTT}' không hợp lệ, "
                    "chỉ chấp nhận 1 (phí dịch vụ) / 2 (định suất) / 3 (DRG)"
                )

        # ==================================================================
        # 41. VET_THUONG_TP – Số, 1 ký tự, chỉ ghi "1" hoặc để trống
        # ==================================================================
        if self.VET_THUONG_TP is not None:
            if self._to_int(self.VET_THUONG_TP) != 1:
                errs.append(
                    f"VET_THUONG_TP: '{self.VET_THUONG_TP}' không hợp lệ, "
                    "chỉ chấp nhận '1' (vết thương tái phát) hoặc để trống"
                )

        # ==================================================================
        # 42. PP_VO_CAM – Số, 1 ký tự, enum {1, 2, 3, 4}
        #    1: Gây mê | 2: Gây tê | 3: Châm tê | 4: Phương pháp khác
        #    Chỉ bắt buộc khi có phẫu thuật/thủ thuật dùng vô cảm
        # ==================================================================
        pp_vc = self._to_int(self.PP_VO_CAM)
        if self.PP_VO_CAM is not None and pp_vc is not None:
            if pp_vc not in {1, 2, 3, 4}:
                errs.append(
                    f"PP_VO_CAM: '{self.PP_VO_CAM}' không hợp lệ, "
                    "chỉ chấp nhận 1 (gây mê) / 2 (gây tê) / 3 (châm tê) / 4 (khác)"
                )

        # ==================================================================
        # 44. MA_MAY – Chuỗi, max 1024
        #    Định dạng QĐ mới: XX.n.Z1;Z2;Z3
        #      - XX/XXX : mã nhóm máy (2-3 ký tự chữ cái)
        #      - n      : nguồn kinh phí (1/2/3, nếu =3 ghi kèm [nguồn cụ thể])
        #      - Z1;Z2;Z3: serial các máy trong hệ thống, cách nhau ";",
        #                  có thể chứa ký tự đặc biệt
        #    Ví dụ: MD.1.0175420;0228420;0091720
        #      → mã nhóm MD, nguồn NSNN, 3 serial: 0175420 / 0228420 / 0091720
        #    Cấu trúc parse: split ".": 3 phần, maxsplit=2
        #      parts[0] = XX, parts[1] = n, parts[2] = toàn bộ chuỗi serial
        #    BUG cũ: split ";" trước rồi parse từng mảnh → sai, vì ";"
        #            phân cách serial bên trong trường, không phân cách nhiều máy
        # ==================================================================
        if self.MA_MAY:
            raw_may = str(self.MA_MAY).strip()
            # Split tối đa 2 lần theo "." → [XX, n, "serial1;serial2;..."]
            parts = raw_may.split(".", 2)

            if len(parts) < 3:
                errs.append(
                    f"MA_MAY: '{raw_may}' sai định dạng, "
                    "phải là XX.n.Z (VD: MD.1.0175420;0228420;0091720)"
                )
            else:
                xx_raw, n_raw, serials_raw = parts[0], parts[1], parts[2]

                # --- Kiểm tra mã nhóm máy: 2-3 ký tự chữ cái (tiếng Việt hoặc Latin) ---
                if not re.fullmatch(r"[A-ZĐÁẮẶÂẤẬĂÊẾỆÔỐỘƠỚỢƯỨỰa-zđ]{2,3}", xx_raw, re.IGNORECASE):
                    errs.append(
                        f"MA_MAY: mã nhóm máy '{xx_raw}' phải là 2-3 ký tự chữ cái "
                        "(VD: HH, VS, MD, MRI, PET, DSA, ĐT…)"
                    )

                # --- Kiểm tra nguồn kinh phí: 1 / 2 / 3[...] ---
                if not re.fullmatch(r"[123](\[.+?])?", n_raw):
                    errs.append(
                        f"MA_MAY: nguồn kinh phí '{n_raw}' không hợp lệ. "
                        "Phải là: 1 (NSNN), 2 (tài trợ/viện trợ/hỗ trợ), "
                        "3[tên nguồn] (nguồn khác – VD: 3[vaynganhang])"
                    )

                # --- Kiểm tra phần serial: không được rỗng ---
                if not serials_raw.strip():
                    errs.append(
                        f"MA_MAY: thiếu số serial sau '{xx_raw}.{n_raw}.'"
                    )
                else:
                    # Serial có thể chứa bất kỳ ký tự nào kể cả đặc biệt,
                    # chỉ kiểm tra không có mảnh nào rỗng giữa hai dấu ";"
                    serials = serials_raw.split(";")
                    empty_idx = [i + 1 for i, s in enumerate(serials) if not s.strip()]
                    if empty_idx:
                        errs.append(
                            f"MA_MAY: serial rỗng tại vị trí {empty_idx} "
                            f"(kiểm tra dấu ';' thừa trong '{serials_raw}')"
                        )

        # ==================================================================
        # 46. TAI_SU_DUNG – Số, 1 ký tự, chỉ ghi "1" hoặc để trống
        # ==================================================================
        if self.TAI_SU_DUNG is not None:
            if self._to_int(self.TAI_SU_DUNG) != 1:
                errs.append(
                    f"TAI_SU_DUNG: '{self.TAI_SU_DUNG}' không hợp lệ, "
                    "chỉ chấp nhận '1' (VTYT tái sử dụng) hoặc để trống"
                )

        # ==================================================================
        # Cross-field: MA_DICH_VU / MA_VAT_TU – ít nhất 1 phải có giá trị
        # ==================================================================
        if not self.MA_DICH_VU and not self.MA_VAT_TU:
            errs.append(
                "MA_DICH_VU và MA_VAT_TU: ít nhất 1 trường phải có giá trị"
            )

        # ==================================================================
        # Cross-field: PHAM_VI = 1 → DON_GIA_BH > 0
        # ==================================================================
        if pham_vi == 1 and dgbh is not None and dgbh == 0:
            # Trường hợp ngoại lệ: DVKT chưa có mức giá (mã kết thúc .0000 hoặc _TB)
            ma_dv_str = str(self.MA_DICH_VU or "")
            if not (ma_dv_str.endswith(".0000") or ma_dv_str.endswith("_TB") or ma_dv_str.endswith("_TT")):
                errs.append(
                    "DON_GIA_BH = 0 khi PHAM_VI = 1: "
                    "chỉ hợp lệ khi DVKT chưa có mức giá (mã kết thúc .0000/_TB/_TT)"
                )

        # ==================================================================
        # Cross-field: TAI_SU_DUNG = 1 → DON_GIA_BV phải = DON_GIA_BH
        # ==================================================================
        if (self.TAI_SU_DUNG is not None and self._to_int(self.TAI_SU_DUNG) == 1
                and dgbv is not None and dgbh is not None):
            if abs(dgbv - dgbh) > 0.001:
                errs.append(
                    f"TAI_SU_DUNG=1: DON_GIA_BV ({dgbv}) phải = DON_GIA_BH ({dgbh}) "
                    "theo quy định VTYT tái sử dụng"
                )

        return errs