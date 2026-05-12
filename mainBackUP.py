from model.XML1 import Bang1_TongHop
from model.XML10 import Bang10_GiayNghiDuongThai
from model.XML11 import Bang11_GiayNghiHuongBHXH
from model.XML13 import Bang13_GiayChuyenTuyen
from model.XML14 import Bang14_GiayHenKhamLai
from model.XML2 import Bang2_Thuoc
from model.XML3 import Bang3_DVKT_VTYT
from model.XML4 import Bang4_DichVuCLS
from model.XML5 import Bang5_DienBienLamSang
from model.XML7 import Bang7_GiayRaVien
from model.XML8 import Bang8_TomTatHSBA
from model.XML9 import Bang9_GiayChungSinh
from services.excel_service import ExcelService
from services.helper import FileHelper
import os

# File excel đầu vào
#excel_file = r"D:\BAOCAO_HIS\Daily-XML130\KB-9-5-26.xlsx";


excel_file = input("File Excel: ").strip().strip('"')

if not os.path.exists(excel_file):
    print("File không tồn tại!")
    exit()
all_objects, all_errors = ExcelService.read_excel(excel_file)
print(all_errors)
#for sheet_name, objects in all_objects.items():
#
#    print(f"\n===== {sheet_name} =====")
#
#    for i, obj in enumerate(objects, start=1):
#
#        print(f"\nRow {i}")
#
#        for k, v in obj.__dict__.items():
#
#            print(f"{k}: {v}")
#
#for i, obj in enumerate(all_objects["XML1"], start=1):
#    print(f"Row {i} {obj}")

for sheet_name, objects in all_objects.items():

    print(f"\n===== SHEET: {sheet_name} =====")

    for i, record in enumerate(objects, start=2):

        errors = record.validate()

        if errors:

            print(f"\n❌ Row Excel {i} - LỖI:")

            for e in errors:

                print(" -", e)

        else:

            print(f"Row Excel {i}: ✅ OK")

#Gom log
logs = []

for sheet_name, objects in all_objects.items():

    logs.append(f"\n===== SHEET: {sheet_name} =====")

    for i, record in enumerate(objects, start=2):

        errors = record.validate()

        if errors:

            logs.append(f"\n❌ Row Excel {i} - LỖI:")

            for e in errors:
                logs.append(" - " + e + "\n")

        else:

            logs.append(f"Row Excel {i}: ✅ OK")
#Ghi log
log_file = FileHelper.write_log(excel_file, logs)

print("Đã ghi log:", log_file)