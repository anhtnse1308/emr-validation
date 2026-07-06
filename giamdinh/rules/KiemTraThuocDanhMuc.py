"""
Rule – Kiểm tra thuốc XML2 theo danh mục trúng thầu
Luồng độc lập, không phụ thuộc vào các rule giám định khác.

Các loại kiểm tra:
  T1 – MA_THUOC không có trong danh mục                    → WARN.DM01
  T2 – SO_DANG_KY không khớp với MA_THUOC trong danh mục   → WARN.DM02
  T3 – DON_GIA vượt DON_GIA_BH trong danh mục              → WARN.DM03
  T4 – DUONG_DUNG không khớp với danh mục                  → WARN.DM04
  T5 – HAM_LUONG không khớp với danh mục                   → WARN.DM05
  T6 – Thuốc hết hiệu lực tại thời điểm y lệnh             → WARN.DM06

Dùng:
    from giamdinh.KiemTraThuocDanhMuc import KiemTraThuocDanhMuc
    from giamdinh.DanhMucThuocLoader import DanhMucThuocLoader

    loader = DanhMucThuocLoader("path/to/FileDanhMucThuoc.xlsx")
    rule   = KiemTraThuocDanhMuc(loader)
    errors = rule.check(all_objects)
"""

from __future__ import annotations
from giamdinh.GiamDinhBase import GiamDinhBase, GiamDinhError
from giamdinh.DanhMucThuocLoader import DanhMucThuocLoader, DrugEntry

CAN_CU = "Danh mục thuốc trúng thầu của cơ sở KCB"

# Tolerance khi so sánh đơn giá (%)
DON_GIA_TOLERANCE_PCT = 0.01   # 1% cho sai số làm tròn


def _norm(s: str) -> str:
    """Chuẩn hóa chuỗi để so sánh: lower, strip, bỏ khoảng trắng thừa."""
    return " ".join(str(s).lower().split())


def _to_float(v) -> float | None:
    try:
        return float(str(v).replace(",", "").strip())
    except (ValueError, TypeError):
        return None


class KiemTraThuocDanhMuc(GiamDinhBase):
    """
    Kiểm tra từng dòng thuốc trong XML2 đối chiếu với danh mục trúng thầu.
    Khởi tạo một lần với DanhMucThuocLoader, check() nhiều lần trên all_objects khác nhau.
    """

    def __init__(self, loader: DanhMucThuocLoader):
        self.loader = loader

    def check(self, all_objects: dict) -> list[GiamDinhError]:
        errors: list[GiamDinhError] = []

        for row_excel, rec in self._get_rows(all_objects, "XML2"):
            ma_lk      = (getattr(rec, "MA_LK",      None) or "").strip()
            ma_thuoc   = (getattr(rec, "MA_THUOC",    None) or "").strip()
            so_dang_ky = (getattr(rec, "SO_DANG_KY",  None) or "").strip()
            don_gia    = _to_float(getattr(rec, "DON_GIA",    None))
            duong_dung = _norm(getattr(rec, "DUONG_DUNG",  None) or "")
            ham_luong  = _norm(getattr(rec, "HAM_LUONG",   None) or "")
            ngay_yl    = (getattr(rec, "NGAY_YL",     None) or "").strip()

            if not ma_lk or not ma_thuoc:
                continue

            # ==============================================================
            # T1 – MA_THUOC không có trong danh mục
            # ==============================================================
            if not self.loader.in_catalog(ma_thuoc=ma_thuoc):
                errors.append(GiamDinhError(
                    sheet="XML2", ma_lk=ma_lk, row_excel=row_excel,
                    ma_ly_do="WARN.DM01",
                    mo_ta=(
                        f"MA_THUOC '{ma_thuoc}' không có trong danh mục thuốc trúng thầu. "
                        "Kiểm tra lại mã thuốc hoặc bổ sung vào danh mục."
                    ),
                    can_cu=CAN_CU,
                    ma_dich_vu=ma_thuoc,
                ))
                continue   # không check tiếp nếu mã không tồn tại

            # Lấy các entry khớp MA_THUOC (có lọc hiệu lực nếu có ngày)
            entries_by_ma = self.loader.lookup(
                ma_thuoc=ma_thuoc,
                ngay_yl=ngay_yl or None,
            )

            # ==============================================================
            # T6 – Thuốc hết hiệu lực tại thời điểm y lệnh
            #       Trigger khi:
            #         - Có MA_THUOC trong danh mục (đã qua T1)
            #         - Kết hợp (MA_THUOC, SO_DANG_KY) cụ thể KHÔNG CÒN
            #           entry nào hiệu lực tại ngày y lệnh
            #         - Nhưng có entry với cặp đó khi không lọc ngày
            #           (tức là trước đây có, nay hết hạn)
            # ==============================================================
            if ngay_yl and so_dang_ky:
                entries_sdk_ngay = self.loader.lookup(
                    ma_thuoc=ma_thuoc,
                    so_dang_ky=so_dang_ky,
                    ngay_yl=ngay_yl,
                )
                entries_sdk_all = self.loader.lookup(
                    ma_thuoc=ma_thuoc,
                    so_dang_ky=so_dang_ky,
                )
                if not entries_sdk_ngay and entries_sdk_all:
                    # Cặp (MA_THUOC, SDK) từng tồn tại nhưng hết hiệu lực
                    den_list = sorted(
                        {e.den_ngay for e in entries_sdk_all if e.den_ngay},
                        reverse=True,
                    )
                    het_han = den_list[0] if den_list else "?"
                    errors.append(GiamDinhError(
                        sheet="XML2", ma_lk=ma_lk, row_excel=row_excel,
                        ma_ly_do="WARN.DM06",
                        mo_ta=(
                            f"Thuốc '{ma_thuoc}' / SDK '{so_dang_ky}' "
                            f"hết hiệu lực tại ngày y lệnh {ngay_yl}. "
                            f"Hiệu lực kết thúc: {het_han}. "
                            "Kiểm tra lại hợp đồng/quyết định thầu."
                        ),
                        can_cu=CAN_CU,
                        ma_dich_vu=ma_thuoc,
                    ))

            # ==============================================================
            # T2 – SO_DANG_KY không khớp với MA_THUOC trong danh mục
            # ==============================================================
            if so_dang_ky:
                entries_exact = self.loader.lookup(
                    ma_thuoc=ma_thuoc,
                    so_dang_ky=so_dang_ky,
                    ngay_yl=ngay_yl or None,
                )
                if not entries_exact:
                    # SO_DANG_KY không khớp với MA_THUOC → lỗi
                    sdky_in_cat = sorted({e.so_dang_ky for e in entries_by_ma})
                    errors.append(GiamDinhError(
                        sheet="XML2", ma_lk=ma_lk, row_excel=row_excel,
                        ma_ly_do="WARN.DM02",
                        mo_ta=(
                            f"SO_DANG_KY '{so_dang_ky}' không khớp với MA_THUOC '{ma_thuoc}' "
                            f"trong danh mục. "
                            f"Số đăng ký trong danh mục: {', '.join(sdky_in_cat[:5])}."
                        ),
                        can_cu=CAN_CU,
                        ma_dich_vu=ma_thuoc,
                    ))
                    # Vẫn dùng entries_by_ma để check tiếp các trường khác
                    working_entries = entries_by_ma
                else:
                    working_entries = entries_exact
            else:
                working_entries = entries_by_ma

            if not working_entries:
                continue

            # ==============================================================
            # T3 – DON_GIA vượt DON_GIA_BH trong danh mục
            # ==============================================================
            if don_gia is not None:
                max_gia_bh = max(
                    (e.don_gia_bh for e in working_entries if e.don_gia_bh is not None),
                    default=None,
                )
                if max_gia_bh is not None:
                    tolerance = max_gia_bh * DON_GIA_TOLERANCE_PCT
                    if don_gia > max_gia_bh + tolerance:
                        errors.append(GiamDinhError(
                            sheet="XML2", ma_lk=ma_lk, row_excel=row_excel,
                            ma_ly_do="WARN.DM03",
                            mo_ta=(
                                f"DON_GIA {don_gia:,.0f} đ vượt DON_GIA_BH tối đa "
                                f"{max_gia_bh:,.0f} đ trong danh mục "
                                f"(chênh {don_gia - max_gia_bh:,.0f} đ). "
                                f"MA_THUOC='{ma_thuoc}', SO_DANG_KY='{so_dang_ky}'."
                            ),
                            can_cu=CAN_CU,
                            ma_dich_vu=ma_thuoc,
                        ))

            # ==============================================================
            # T4 – DUONG_DUNG không khớp với danh mục
            # ==============================================================
            if duong_dung:
                dm_duong_dung = {_norm(e.duong_dung) for e in working_entries if e.duong_dung}
                if dm_duong_dung and duong_dung not in dm_duong_dung:
                    errors.append(GiamDinhError(
                        sheet="XML2", ma_lk=ma_lk, row_excel=row_excel,
                        ma_ly_do="WARN.DM04",
                        mo_ta=(
                            f"DUONG_DUNG '{duong_dung}' không khớp với danh mục. "
                            f"Danh mục: {', '.join(sorted(dm_duong_dung)[:3])}."
                        ),
                        can_cu=CAN_CU,
                        ma_dich_vu=ma_thuoc,
                    ))

            # ==============================================================
            # T5 – HAM_LUONG không khớp với danh mục
            # ==============================================================
            if ham_luong:
                dm_ham_luong = {_norm(e.ham_luong) for e in working_entries if e.ham_luong}
                if dm_ham_luong and ham_luong not in dm_ham_luong:
                    errors.append(GiamDinhError(
                        sheet="XML2", ma_lk=ma_lk, row_excel=row_excel,
                        ma_ly_do="WARN.DM05",
                        mo_ta=(
                            f"HAM_LUONG '{ham_luong}' không khớp với danh mục. "
                            f"Danh mục: {', '.join(sorted(dm_ham_luong)[:3])}."
                        ),
                        can_cu=CAN_CU,
                        ma_dich_vu=ma_thuoc,
                    ))

        return errors