"""
Rule – Kiểm tra chất lượng dữ liệu (CV 199/GĐĐT-PTDB ngày 13/05/2022)
Nguồn: Trung tâm Giám định BHYT và Thanh toán đa tuyến

5 nhóm cảnh báo, toàn bộ detect từ XML1 (+ cross XML2/XML3 cho Rule 1):

  R1 – Ngoại trú chỉ phát sinh tiền khám, không có DVKT/thuốc  → WARN.DL01
  R2 – Ngoại trú SO_NGAY_DTRI = 0                              → WARN.DL02
  R3 – Nội trú MA_LOAI_KCB=3 nhưng thời gian nằm < 4 giờ      → WARN.DL03
  R4 – Nội trú > 4 giờ nhưng SO_NGAY_DTRI = 0                 → WARN.DL04
  R5 – COVID-19 (U07.1) không có bệnh kèm hợp lệ              → WARN.DL05
       (Rule 5 bị BHXH giảm trừ thẳng, không cần giải trình)

Ghi chú:
  - Mã lý do WARN.DLxx là mã nội bộ, không phải mã từ chối BHXH chính thức.
  - Rule 3: nội trú < 4 giờ có thể hợp lệ nếu dùng MA_LOAI_KCB=09
            (nội trú dưới 4 giờ theo QĐ 4750) → cảnh báo để kiểm tra, không từ chối cứng.
  - Rule 5: CV 3100/BYT-BH ngày 20/4/2021 bắt buộc có bệnh kèm ≠ U07.1/U07.2.
"""

from datetime import datetime
from giamdinh.GiamDinhBase import GiamDinhBase, GiamDinhError

# ---------------------------------------------------------------------------
# Hằng số
# ---------------------------------------------------------------------------
# MA_LOAI_KCB
LOAI_NGOAI_TRU = {"02", "05", "08"}
LOAI_NOI_TRU   = {"03", "04", "06"}

# Ngưỡng thời gian nằm viện nội trú (phút)
NOI_TRU_MIN_PHUT = 240   # 4 giờ

# ICD COVID-19
ICD_COVID = {"U07.1", "U07.2"}

# Mã DVKT khám bệnh (chỉ tính phí khám, không phải DVKT thực sự)
# Thực tế cần map đầy đủ từ danh mục; đây là prefix/set phổ biến
MA_KHAM_BENH_PREFIXES = ("00.",)   # nhóm khám bệnh
MA_KHAM_BENH = {
    "00.001", "00.00100",   # Khám bệnh thông thường
    "00.002", "00.00200",   # Khám bệnh theo yêu cầu
    "00.003", "00.00300",   # Khám chuyên khoa
}

CAN_CU = "CV 199/GĐĐT-PTDB ngày 13/05/2022 + CV 3100/BYT-BH ngày 20/4/2021"


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def _parse_date12(val: str) -> datetime | None:
    """Parse chuỗi DATE12 (yyyymmddHHMM) → datetime, None nếu lỗi."""
    try:
        s = str(val or "").strip()
        if len(s) == 12 and s.isdigit():
            return datetime.strptime(s, "%Y%m%d%H%M")
    except ValueError:
        pass
    return None


def _so_ngay(val) -> int | None:
    """Parse SO_NGAY_DTRI → int, None nếu không parse được."""
    try:
        return int(float(str(val).strip()))
    except (ValueError, TypeError, AttributeError):
        return None


def _is_kham_benh_only(ma_dv: str) -> bool:
    """True nếu mã DVKT chỉ là mã khám bệnh (không phải DVKT thực sự)."""
    ma_dv = ma_dv.strip()
    return (ma_dv in MA_KHAM_BENH or
            any(ma_dv.startswith(p) for p in MA_KHAM_BENH_PREFIXES))


def _thoi_gian_nam_phut(ngay_vao: str, ngay_ra: str) -> float | None:
    """Tính số phút nằm viện. None nếu không parse được."""
    dt_vao = _parse_date12(ngay_vao)
    dt_ra  = _parse_date12(ngay_ra)
    if dt_vao and dt_ra and dt_ra >= dt_vao:
        return (dt_ra - dt_vao).total_seconds() / 60
    return None


# ---------------------------------------------------------------------------
# Rule class
# ---------------------------------------------------------------------------
class KiemTraDuLieu(GiamDinhBase):
    """
    5 rule cảnh báo chất lượng dữ liệu XML BHYT.
    Mỗi rule là 1 method riêng để dễ bật/tắt.
    """

    def check(self, all_objects: dict) -> list[GiamDinhError]:
        errors: list[GiamDinhError] = []
        errors.extend(self._r1_ngoaitru_chi_kham(all_objects))
        errors.extend(self._r2_ngoaitru_0_ngay(all_objects))
        errors.extend(self._r3_noitru_duoi_4_gio(all_objects))
        errors.extend(self._r4_noitru_0_ngay(all_objects))
        errors.extend(self._r5_covid_khong_benh_kem(all_objects))
        return errors

    # ------------------------------------------------------------------
    # R1 – Ngoại trú chỉ phát sinh tiền khám, không có DVKT/thuốc
    # ------------------------------------------------------------------
    def _r1_ngoaitru_chi_kham(self, all_objects: dict) -> list[GiamDinhError]:
        errors = []

        # MA_LK có thuốc (XML2)
        lk_co_thuoc: set[str] = {
            (getattr(r, "MA_LK", "") or "").strip()
            for _, r in self._get_rows(all_objects, "XML2")
            if (getattr(r, "MA_LK", "") or "").strip()
        }

        # MA_LK có DVKT thực sự (XML3, loại trừ mã khám bệnh)
        lk_co_dvkt: set[str] = set()
        for _, r in self._get_rows(all_objects, "XML3"):
            ma_lk = (getattr(r, "MA_LK",      "") or "").strip()
            ma_dv  = (getattr(r, "MA_DICH_VU", "") or "").strip()
            if ma_lk and ma_dv and not _is_kham_benh_only(ma_dv):
                lk_co_dvkt.add(ma_lk)

        # Kiểm tra XML1
        for row_excel, rec in self._get_rows(all_objects, "XML1"):
            ma_lk   = (getattr(rec, "MA_LK",       "") or "").strip()
            loai    = (getattr(rec, "MA_LOAI_KCB",  "") or "").strip()
            if not ma_lk or loai not in LOAI_NGOAI_TRU:
                continue
            if ma_lk not in lk_co_thuoc and ma_lk not in lk_co_dvkt:
                errors.append(GiamDinhError(
                    sheet="XML1", ma_lk=ma_lk, row_excel=row_excel,
                    ma_ly_do="WARN.DL01",
                    mo_ta=(
                        f"Ngoại trú (MA_LOAI_KCB={loai}) chỉ phát sinh tiền khám bệnh, "
                        "không có DVKT hoặc thuốc nào trong XML2/XML3. "
                        "Kiểm tra dữ liệu có gửi đủ sheet không."
                    ),
                    can_cu=CAN_CU,
                ))
        return errors

    # ------------------------------------------------------------------
    # R2 – Ngoại trú SO_NGAY_DTRI = 0
    # ------------------------------------------------------------------
    def _r2_ngoaitru_0_ngay(self, all_objects: dict) -> list[GiamDinhError]:
        errors = []
        for row_excel, rec in self._get_rows(all_objects, "XML1"):
            ma_lk   = (getattr(rec, "MA_LK",       "") or "").strip()
            loai    = (getattr(rec, "MA_LOAI_KCB",  "") or "").strip()
            so_ngay = _so_ngay(getattr(rec, "SO_NGAY_DTRI", None))
            if not ma_lk or loai not in LOAI_NGOAI_TRU:
                continue
            if so_ngay is not None and so_ngay == 0:
                errors.append(GiamDinhError(
                    sheet="XML1", ma_lk=ma_lk, row_excel=row_excel,
                    ma_ly_do="WARN.DL02",
                    mo_ta=(
                        f"Ngoại trú (MA_LOAI_KCB={loai}) có SO_NGAY_DTRI=0. "
                        "Ngoại trú tối thiểu phải = 1 ngày. "
                        "Kiểm tra lại dữ liệu thống kê."
                    ),
                    can_cu=CAN_CU,
                ))
        return errors

    # ------------------------------------------------------------------
    # R3 – Nội trú MA_LOAI_KCB=3 nhưng thời gian nằm < 4 giờ
    # ------------------------------------------------------------------
    def _r3_noitru_duoi_4_gio(self, all_objects: dict) -> list[GiamDinhError]:
        errors = []
        for row_excel, rec in self._get_rows(all_objects, "XML1"):
            ma_lk = (getattr(rec, "MA_LK",      "") or "").strip()
            loai  = (getattr(rec, "MA_LOAI_KCB", "") or "").strip()
            if not ma_lk or loai != "03":
                continue
            ngay_vao = getattr(rec, "NGAY_VAO", "") or ""
            ngay_ra  = getattr(rec, "NGAY_RA",  "") or ""
            phut = _thoi_gian_nam_phut(ngay_vao, ngay_ra)
            if phut is not None and phut < NOI_TRU_MIN_PHUT:
                gio  = int(phut // 60)
                phut_le = int(phut % 60)
                errors.append(GiamDinhError(
                    sheet="XML1", ma_lk=ma_lk, row_excel=row_excel,
                    ma_ly_do="WARN.DL03",
                    mo_ta=(
                        f"Nội trú (MA_LOAI_KCB=03) thời gian nằm viện "
                        f"{gio} giờ {phut_le} phút (< 4 giờ). "
                        f"NGAY_VAO={ngay_vao} → NGAY_RA={ngay_ra}. "
                        "Nếu đúng < 4 giờ nên dùng MA_LOAI_KCB=09 "
                        "(nội trú dưới 4 giờ theo QĐ 4750)."
                    ),
                    can_cu=CAN_CU,
                ))
        return errors

    # ------------------------------------------------------------------
    # R4 – Nội trú > 4 giờ nhưng SO_NGAY_DTRI = 0
    # ------------------------------------------------------------------
    def _r4_noitru_0_ngay(self, all_objects: dict) -> list[GiamDinhError]:
        errors = []
        for row_excel, rec in self._get_rows(all_objects, "XML1"):
            ma_lk   = (getattr(rec, "MA_LK",       "") or "").strip()
            loai    = (getattr(rec, "MA_LOAI_KCB",  "") or "").strip()
            so_ngay = _so_ngay(getattr(rec, "SO_NGAY_DTRI", None))
            if not ma_lk or loai not in LOAI_NOI_TRU:
                continue
            if so_ngay is None or so_ngay != 0:
                continue
            # Chỉ cảnh báo nếu thực sự nằm > 4 giờ
            ngay_vao = getattr(rec, "NGAY_VAO", "") or ""
            ngay_ra  = getattr(rec, "NGAY_RA",  "") or ""
            phut = _thoi_gian_nam_phut(ngay_vao, ngay_ra)
            if phut is None or phut > NOI_TRU_MIN_PHUT:
                phut_str = f"{phut:.0f} phút" if phut else "không xác định"
                errors.append(GiamDinhError(
                    sheet="XML1", ma_lk=ma_lk, row_excel=row_excel,
                    ma_ly_do="WARN.DL04",
                    mo_ta=(
                        f"Nội trú (MA_LOAI_KCB={loai}) thời gian nằm {phut_str} "
                        f"nhưng SO_NGAY_DTRI=0. "
                        f"NGAY_VAO={ngay_vao} → NGAY_RA={ngay_ra}. "
                        "Mâu thuẫn dữ liệu, cần điều chỉnh SO_NGAY_DTRI."
                    ),
                    can_cu=CAN_CU,
                ))
        return errors

    # ------------------------------------------------------------------
    # R5 – COVID-19 không có bệnh kèm hợp lệ
    # ------------------------------------------------------------------
    def _r5_covid_khong_benh_kem(self, all_objects: dict) -> list[GiamDinhError]:
        errors = []
        for row_excel, rec in self._get_rows(all_objects, "XML1"):
            ma_lk   = (getattr(rec, "MA_LK",         "") or "").strip()
            ma_chinh = (getattr(rec, "MA_BENH_CHINH", "") or "").strip().upper()
            ma_kt    = (getattr(rec, "MA_BENH_KT",    "") or "").strip()
            if not ma_lk or ma_chinh != "U07.1":
                continue

            # Parse MA_BENH_KT → tập mã kèm theo
            benh_kem: set[str] = {
                c.strip().upper()
                for c in ma_kt.split(";")
                if c.strip()
            }

            # Hợp lệ: có ít nhất 1 mã kèm theo KHÁC U07.1 và U07.2
            benh_kem_hop_le = benh_kem - ICD_COVID
            if not benh_kem_hop_le:
                if not benh_kem:
                    mo_ta_kem = "không có mã bệnh kèm theo"
                else:
                    mo_ta_kem = (
                        f"mã bệnh kèm theo chỉ có: "
                        f"{'; '.join(sorted(benh_kem))} (đều là COVID)"
                    )
                errors.append(GiamDinhError(
                    sheet="XML1", ma_lk=ma_lk, row_excel=row_excel,
                    ma_ly_do="WARN.DL05",
                    mo_ta=(
                        f"Chẩn đoán chính COVID-19 (U07.1), {mo_ta_kem}. "
                        "Theo CV 3100/BYT-BH ngày 20/4/2021: BN COVID-19 phải có "
                        "ít nhất 1 bệnh kèm theo khác U07.1/U07.2. "
                        "BHXH sẽ thực hiện giảm trừ trực tiếp trên hệ thống."
                    ),
                    can_cu="CV 3100/BYT-BH ngày 20/4/2021 + CV 199/GĐĐT-PTDB ngày 13/05/2022",
                ))
        return errors   