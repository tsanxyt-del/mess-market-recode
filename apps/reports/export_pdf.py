"""PDF exports — reportlab (optional dep). Excel lives in export_excel.py."""
from django.http import HttpResponse

# Backward-compat: old imports `from .export_pdf import monthly_xlsx` still work.
from .export_excel import monthly_xlsx, daily_xlsx, itemwise_xlsx  # noqa: F401

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


def simple_pdf_response(filename, title, lines):
    if not HAS_REPORTLAB:
        return HttpResponse("PDF export needs `pip install reportlab`.",
                            status=501, content_type="text/plain")
    resp = HttpResponse(content_type="application/pdf")
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    c = canvas.Canvas(resp, pagesize=A4)
    w, h = A4
    y = h - 50
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, title)
    y -= 25
    c.setFont("Helvetica", 10)
    for line in lines:
        if y < 50:
            c.showPage()
            y = h - 50
            c.setFont("Helvetica", 10)
        c.drawString(50, y, str(line)[:110])
        y -= 14
    c.save()
    return resp


def monthly_pdf(report):
    lines = [f"Monthly Report {report['month']:02d}/{report['year']}",
             f"Total: Rs.{report['total_amount']} | Items: {report['total_items']} | Days: {report['recorded_days']}", ""]
    lines += [f"{d['date']}  {d['items']} items  Rs.{d['amount']}" for d in report["days"]]
    return simple_pdf_response(f"monthly-{report['year']}-{report['month']:02d}.pdf",
                               "Monthly Report", lines)


def daily_pdf(report):
    lines = [f"Daily Report {report['date']}",
             f"Total: Rs.{report['total_amount']} | Items: {report['total_items']}", ""]
    lines += [f"{i.get('item_name')} {i.get('quantity')}{i.get('unit')} @ Rs.{i.get('rate')} = Rs.{i.get('total')}"
              for i in report["items"]]
    return simple_pdf_response(f"daily-{report['date']}.pdf", "Daily Report", lines)


def itemwise_pdf(report):
    lines = [f"Item Report: {report['item']}",
             f"Qty: {report['total_quantity']}{report['unit']} | Total: Rs.{report['total_amount']}", ""]
    lines += [f"{r['date']} {r['quantity']}{r['unit']} = Rs.{r['total']}" for r in report["rows"]]
    return simple_pdf_response(f"item-{report['item']}.pdf", "Item-wise Report", lines)
