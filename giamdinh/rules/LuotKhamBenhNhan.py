"""
Rule III – Tách lượt KCB + KCB sau ngày chết
Căn cứ: QĐ 4210/QĐ-BYT ngày 20/09/2017 + CV 3370/BHXH-GĐĐT ngày 26/10/2020

III.1 – Thận nhân tạo ngoại trú: tối đa 12 lượt / 1 BN / 1 năm
  Detect: group XML1 theo MA_BN + NAM_QT
  ICD thận nhân tạo: N18.5, N18.6 (Suy thận mạn giai đoạn 5/cuối)
  Mã DVKT thận nhân tạo: prefix "13."

III.2 – KCB sau ngày chết: NGAY_VAO > ngày tử vong của BN
  Detect: không thể tự động hoàn toàn (cần dữ liệu ngày chết từ BHXH)
  Implement: kiểm tra KET_QUA_DTRI = 5 (tử vong tại KBCB)
             → các MA_LK khác cùng MA_BN có NGAY_VAO sau NGAY_RA của lượt tử vong
"""

from collections import defaultdict
from giamdinh.GiamDinhBase import GiamDinhBase, GiamDinhError

# ---------------------------------------------------------------------------
# Mã DVKT thận nhân tạo (prefix)
# ---------------------------------------------------------------------------
MA_THAN_NHAN_TAO_PREFIXES = (
    "13.",   # Nhóm lọc máu / thận nhân tạo
)

# ICD-10 thận nhân tạo chu kỳ
ICD_THAN_NHAN_TAO = {
    "N18.5",  # Suy thận mạn giai đoạn 5
    "N18.6",  # Suy thận giai đoạn cuối
    "N18.9",  # Suy thận mạn không xác định
    "Z49",    # Chăm sóc lọc thận
    "Z49.0", "Z49.1", "Z49.2",
}

MAX_LUOT_THAN_NAM = 12

CAN_CU_TACH_LUOT = "Chỉ tiêu số 35 Bảng 1, QĐ 4210/QĐ-BYT ngày 20/09/2017"
CAN_CU_CHET = "CV 3370/BHXH-GĐĐT ngày 26/10/2020 + NĐ 117/2020/NĐ-CP ngày 28/09/2020"


def _is_than_nhan_tao(ma_benh: str, xml3_dv_set: set) -> bool:
    """Kiểm tra lần khám có phải thận nhân tạo không."""
    if ma_benh:
        for icd in ICD_THAN_NHAN_TAO:
            if ma_benh.startswith(icd) or icd.startswith(ma_benh):
                return True
    for dv in xml3_dv_set:
        if any(dv.startswith(p) for p in MA_THAN_NHAN_TAO_PREFIXES):
            return True
    return False


class LuotKhamBenhNhan(GiamDinhBase):
    """
    Rule III.1: Thận nhân tạo ngoại trú > 12 lượt/năm/BN
    Rule III.2: KCB sau ngày tử vong
    """

    def check(self, all_objects: dict) -> list[GiamDinhError]:
        errors: list[GiamDinhError] = []

        xml1_rows = self._get_rows(all_objects, "XML1")

        # Lấy danh sách DVKT của mỗi MA_LK từ XML3
        lk_to_dvkt: dict[str, set] = defaultdict(set)
        for _, rec in self._get_rows(all_objects, "XML3"):
            ma_lk = getattr(rec, "MA_LK", None) or ""
            ma_dv = getattr(rec, "MA_DICH_VU", None) or ""
            if ma_lk and ma_dv:
                lk_to_dvkt[ma_lk].add(ma_dv.strip())

        # ===================================================================
        # III.1 – Thận nhân tạo ngoại trú > 12 lượt/BN/năm
        # Group: (MA_BN, NAM_QT) → list lượt thận nhân tạo
        # ===================================================================
        # key = (ma_bn, nam_qt) → list[(row_excel, rec)]
        than_groups: dict[tuple, list] = defaultdict(list)

        for row_excel, rec in xml1_rows:
            ma_bn = getattr(rec, "MA_BN", None) or ""
            nam_qt = getattr(rec, "NAM_QT", None) or ""
            ma_loai_kcb = getattr(rec, "MA_LOAI_KCB", None) or ""
            ma_benh = getattr(rec, "MA_BENH_CHINH", None) or ""
            ma_lk = getattr(rec, "MA_LK", None) or ""

            # Chỉ xét ngoại trú (MA_LOAI_KCB ∈ {02, 05, 08})
            if ma_loai_kcb not in {"02", "05", "08"}:
                continue

            if not ma_bn or not nam_qt:
                continue

            dvkt_set = lk_to_dvkt.get(ma_lk, set())

            if _is_than_nhan_tao(ma_benh, dvkt_set):
                than_groups[(ma_bn, nam_qt)].append((row_excel, rec))

        for (ma_bn, nam_qt), rows in than_groups.items():
            if len(rows) > MAX_LUOT_THAN_NAM:
                # Báo lỗi trên toàn bộ lượt thừa (từ lượt thứ 13 trở đi)
                vuot_rows = rows[MAX_LUOT_THAN_NAM:]
                for row_excel, rec in vuot_rows:
                    ma_lk = getattr(rec, "MA_LK", None) or ""
                    errors.append(GiamDinhError(
                        sheet="XML1",
                        ma_lk=ma_lk,
                        row_excel=row_excel,
                        ma_ly_do="",  # Không có mã lý do cụ thể trong văn bản
                        mo_ta=(
                            f"BN '{ma_bn}' năm {nam_qt}: "
                            f"có {len(rows)} lượt thận nhân tạo ngoại trú, "
                            f"vượt mức tối đa {MAX_LUOT_THAN_NAM} lượt/năm. "
                            "Các lượt từ thứ 13 trở đi cần điều chỉnh lại theo quy định "
                            "(mỗi tháng chỉ gửi 1 lượt từ ngày 01 đến ngày cuối tháng)."
                        ),
                        can_cu=CAN_CU_TACH_LUOT,
                    ))

        # ===================================================================
        # III.2 – KCB sau ngày tử vong
        # Detect: BN có lần khám KET_QUA_DTRI = 5 (tử vong tại KBCB)
        #         → tìm các lần khám khác cùng MA_BN có NGAY_VAO > NGAY_RA của lần tử vong
        # ===================================================================
        # map MA_BN → list lần tử vong (ngay_ra dạng string yyyymmddHHMM)
        tu_vong_map: dict[str, list[str]] = defaultdict(list)

        for _, rec in xml1_rows:
            ma_bn = getattr(rec, "MA_BN", None) or ""
            ket_qua = str(getattr(rec, "KET_QUA_DTRI", None) or "").strip()
            ngay_ra = str(getattr(rec, "NGAY_RA", None) or "").strip()

            # KET_QUA_DTRI = 5: tử vong tại cơ sở KBCB
            if ket_qua == "5" and ma_bn and ngay_ra and len(ngay_ra) >= 8:
                tu_vong_map[ma_bn].append(ngay_ra)

        for row_excel, rec in xml1_rows:
            ma_bn = getattr(rec, "MA_BN", None) or ""
            ma_lk = getattr(rec, "MA_LK", None) or ""
            ngay_vao = str(getattr(rec, "NGAY_VAO", None) or "").strip()
            ket_qua = str(getattr(rec, "KET_QUA_DTRI", None) or "").strip()

            if not ma_bn or ma_bn not in tu_vong_map:
                continue
            if not ngay_vao or len(ngay_vao) < 8:
                continue

            for ngay_chet in tu_vong_map[ma_bn]:
                # So sánh chuỗi yyyymmdd... (lexicographic = chronological)
                ngay_vao_d = ngay_vao[:8]
                ngay_chet_d = ngay_chet[:8]

                if ngay_vao_d > ngay_chet_d and ket_qua != "5":
                    errors.append(GiamDinhError(
                        sheet="XML1",
                        ma_lk=ma_lk,
                        row_excel=row_excel,
                        ma_ly_do="",
                        mo_ta=(
                            f"BN '{ma_bn}': lần khám NGAY_VAO={ngay_vao} "
                            f"xảy ra SAU ngày tử vong đã ghi nhận ({ngay_chet}). "
                            "Đây là trường hợp KCB sau ngày chết. "
                            "Đề nghị kiểm tra và thu hồi chi phí, "
                            "xử phạt hành chính theo NĐ 117/2020/NĐ-CP."
                        ),
                        can_cu=CAN_CU_CHET,
                    ))
                    break  # chỉ báo 1 lần cho mỗi dòng

        return errors