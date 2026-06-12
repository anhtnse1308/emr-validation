"""
Rule I.2 (nhánh D004.1) – VTYT vượt mức chi quy định
Căn cứ: khoản 2 Điều 3 Thông tư 04/2017/TT-BYT ngày 14/4/2017

Áp dụng: tổng chi phí VTYT cho một lần Chụp, nong và đặt stent ĐMV
(bao gồm cả bộ dụng cụ lấy huyết khối) vượt mức quy định.

Mã từ chối: D004.1

Cấu trúc detect:
  - Tìm các MA_LK có dịch vụ Chụp/nong/đặt stent ĐMV trong XML3
  - Tổng hợp THANH_TIEN_BH của tất cả VTYT (MA_NHOM = 4 hoặc 5) trong cùng MA_LK
  - So sánh với ngưỡng quy định
"""

from giamdinh.GiamDinhBase import GiamDinhBase, GiamDinhError

# ---------------------------------------------------------------------------
# Mã DVKT Chụp/nong/đặt stent ĐMV
# ---------------------------------------------------------------------------
MA_NONG_STENT = {
    "17.106", "17.107", "17.108",
    "17.10600", "17.10601", "17.10602",
}

# ---------------------------------------------------------------------------
# Ngưỡng mức thanh toán VTYT theo TT 04/2017/TT-BYT
# Đơn vị: VNĐ. Cần rà soát lại theo phụ lục hiện hành của BYT.
# ---------------------------------------------------------------------------
MUCCHI_VTYT_NONG_STENT = 40_000_000   # 40 triệu VNĐ / lần

# Nhóm VTYT (MA_NHOM trong XML3): 4=Vật tư thay thế, 5=Vật tư tiêu hao đặc biệt
MA_NHOM_VTYT = {4, 5}

CAN_CU = "khoản 2 Điều 3 Thông tư 04/2017/TT-BYT ngày 14/4/2017"


class VTYTVuotMuc(GiamDinhBase):
    """
    Rule: Tổng VTYT trong lần Chụp/nong/đặt stent ĐMV vượt mức quy định.
    Mã từ chối: D004.1
    """

    def check(self, all_objects: dict) -> list[GiamDinhError]:
        errors: list[GiamDinhError] = []

        rows_xml3 = self._get_rows(all_objects, "XML3")
        groups = self._group_by_ma_lk(rows_xml3)

        for ma_lk, rows in groups.items():
            if not ma_lk:
                continue

            # Kiểm tra lần khám có dịch vụ Nong+stent không
            has_nong_stent = any(
                (getattr(r, "MA_DICH_VU", "") or "").strip() in MA_NONG_STENT
                for _, r in rows
            )
            if not has_nong_stent:
                continue

            # Tổng VTYT (MA_NHOM thuộc nhóm VTYT)
            tong_vtyt = 0.0
            vtyt_rows = []
            for row_excel, rec in rows:
                ma_nhom_raw = getattr(rec, "MA_NHOM", None)
                try:
                    ma_nhom = int(float(str(ma_nhom_raw))) if ma_nhom_raw else None
                except (ValueError, TypeError):
                    ma_nhom = None

                if ma_nhom in MA_NHOM_VTYT:
                    tt_raw = getattr(rec, "THANH_TIEN_BH", None)
                    try:
                        tt = float(str(tt_raw).replace(",", "")) if tt_raw else 0.0
                    except (ValueError, TypeError):
                        tt = 0.0
                    tong_vtyt += tt
                    vtyt_rows.append((row_excel, rec, tt))

            if tong_vtyt > MUCCHI_VTYT_NONG_STENT:
                # Báo lỗi trên dòng cuối cùng của nhóm VTYT (dòng tổng)
                last_row = vtyt_rows[-1][0] if vtyt_rows else rows[-1][0]
                errors.append(GiamDinhError(
                    sheet="XML3",
                    ma_lk=ma_lk,
                    row_excel=last_row,
                    ma_ly_do="D004.1",
                    mo_ta=(
                        f"Tổng VTYT cho kỹ thuật Chụp/nong/đặt stent ĐMV: "
                        f"{tong_vtyt:,.0f} đ – vượt mức quy định "
                        f"{MUCCHI_VTYT_NONG_STENT:,.0f} đ. "
                        f"Phần vượt: {tong_vtyt - MUCCHI_VTYT_NONG_STENT:,.0f} đ."
                    ),
                    can_cu=CAN_CU,
                    ma_dich_vu="NHOM_VTYT_4_5",
                ))

        return errors