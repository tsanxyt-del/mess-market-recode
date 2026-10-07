"""Bill manager page (admin): recent uploads + standalone upload."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import BillUploadForm
from .services import list_bill_records
from .storage import save_bill_file
from .validators import UploadValidationError


@login_required
def bill_manager(request):
    from config.mongo import DB_DOWN_MESSAGE
    form = BillUploadForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        try:
            path = save_bill_file(form.cleaned_data["bill"], form.cleaned_data.get("purchase_date"))
            messages.success(request, f"Bill uploaded: {path}")
            return redirect("bill-manager")
        except UploadValidationError as exc:
            messages.error(request, str(exc))
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning("Bill upload failed: %r", exc)
            messages.error(request, DB_DOWN_MESSAGE)
    try:
        bills = list_bill_records()
        db_down = False
    except Exception:
        bills = []
        db_down = True
    return render(request, "admin/uploads/bill_manager.html",
                  {"form": form, "bills": bills, "db_down": db_down})
