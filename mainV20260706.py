from services.excel_service import ExcelService
from services.helper import FileHelper
from giamdinh.GiamDinhServices import GiamDinhService
import os

while True:
    try:
        excel_file = input("Nhập file Excel: ").strip().strip('"')
        if os.path.exists(excel_file):
            break
    except KeyboardInterrupt:
        print("\nĐã hủy chương trình.")
        exit()

    choice = input("❌ File không tồn tại! Nhập lại? (Y/N): ").strip().lower()
    if choice != "y":
        print("Đã hủy chương trình.")
        exit()

# -----------------------------------------------------------------------
# 1. Đọc + validate dữ liệu (layer hiện có)
# -----------------------------------------------------------------------
all_objects, _ = ExcelService.read_excel(excel_file)

# --- In ra console ---
FileHelper.print_errors_console(all_objects)

# --- Log text tổng hợp ---
summary_log = FileHelper.write_log_summary(excel_file, all_objects)
print(f"\n✅ Đã ghi log tổng hợp    : {summary_log}")

# --- Log JSON chi tiết ---
json_log = FileHelper.write_log_json(excel_file, all_objects, suffix="errors")
print(f"✅ Đã ghi log JSON        : {json_log}")

# --- Log txt chỉ dòng lỗi ---
errors_only_log = FileHelper.write_log_errors_only(excel_file, all_objects)
print(f"✅ Đã ghi log lỗi        : {errors_only_log}")

# --- Excel tất cả dòng + STATUS + ERRORS ---
excel_summary = FileHelper.write_excel_summary(excel_file, all_objects)
print(f"✅ Đã xuất Excel tổng hợp : {excel_summary}")

# --- Excel chỉ dòng lỗi + ROW_EXCEL ---
excel_errors = FileHelper.write_excel_errors_only(excel_file, all_objects)
print(f"✅ Đã xuất Excel lỗi      : {excel_errors}")

# -----------------------------------------------------------------------
# 2. Giám định thanh toán (layer mới)
# -----------------------------------------------------------------------
print("\n" + "=" * 60)
print("  GIÁM ĐỊNH THANH TOÁN BHYT")
print("=" * 60)

giamdinh_errors = GiamDinhService.run(all_objects)

if giamdinh_errors:
    print(f"\n⚠️  Phát hiện {len(giamdinh_errors)} trường hợp cần xem xét từ chối thanh toán:")
    # In tóm tắt theo mã lý do
    from collections import Counter
    cnt = Counter(e.ma_ly_do for e in giamdinh_errors)
    for ma_ly_do, so_luong in sorted(cnt.items()):
        label = ma_ly_do if ma_ly_do else "(không có mã)"
        print(f"   {label:20s}: {so_luong} trường hợp")
else:
    print("\n✓ Không phát hiện trường hợp vi phạm quy định thanh toán.")

giamdinh_excel = GiamDinhService.write_excel_giamdinh(excel_file, giamdinh_errors)
print(f"\n✅ Đã xuất Excel giám định: {giamdinh_excel}")