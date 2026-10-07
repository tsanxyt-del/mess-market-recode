"""CSV + Excel (.xlsx) export (openpyxl optional)."""
import csv
from django.http import HttpResponse

try:
    from openpyxl import Workbook
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False


def csv_response(filename, headers, rows):
    resp = HttpResponse(content_type="text/csv")
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    w = csv.writer(resp)
    w.writerow(headers)
    w.writerows(rows)
    return resp


def monthly_csv(report):
    rows = [[d["date"], d["display"], d["items"], d["amount"]] for d in report["days"]]
    return csv_response(f"monthly-{report['year']}-{report['month']:02d}.csv",
                        ["Date", "Display", "Items", "Amount"], rows)


def daily_csv(report):
    rows = [[i.get("item_name"), i.get("quantity"), i.get("unit"),
             i.get("rate"), i.get("total"), i.get("remark", "")]
            for i in report["items"]]
    return csv_response(f"daily-{report['date']}.csv",
                        ["Item", "Quantity", "Unit", "Rate", "Total", "Remark"], rows)


def itemwise_csv(report):
    rows = [[r["date"], r["quantity"], r["unit"], r["rate"], r["total"]] for r in report["rows"]]
    return csv_response(f"item-{report['item']}.csv",
                        ["Date", "Quantity", "Unit", "Rate", "Total"], rows)


def _xlsx_response(filename, headers, rows):
    if not HAS_OPENPYXL:
        return HttpResponse("Excel export needs `pip install openpyxl`.",
                            status=501, content_type="text/plain")
    wb = Workbook()
    ws = wb.active
    ws.append(headers)
    for r in rows:
        ws.append(r)
    for col in ws.columns:
        ws.column_dimensions[col[0].column_letter].width = 18
    resp = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    wb.save(resp)
    return resp


def monthly_xlsx(report):
    rows = [[d["date"], d["display"], d["items"], d["amount"]] for d in report["days"]]
    return _xlsx_response(f"monthly-{report['year']}-{report['month']:02d}.xlsx",
                          ["Date", "Display", "Items", "Amount"], rows)


def daily_xlsx(report):
    rows = [[i.get("item_name"), i.get("quantity"), i.get("unit"),
             i.get("rate"), i.get("total")] for i in report["items"]]
    return _xlsx_response(f"daily-{report['date']}.xlsx",
                          ["Item", "Quantity", "Unit", "Rate", "Total"], rows)


def itemwise_xlsx(report):
    rows = [[r["date"], r["quantity"], r["unit"], r["rate"], r["total"]] for r in report["rows"]]
    return _xlsx_response(f"item-{report['item']}.xlsx",
                          ["Date", "Quantity", "Unit", "Rate", "Total"], rows)
