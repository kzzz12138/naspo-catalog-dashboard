from gettext import Catalog

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from naspo.management.commands.load_catalog import normalize_mpn
from naspo.models import CatalogItem, Vendor
from django.db.models import Q
from django.core.paginator import Paginator


def search(request):
    q = request.GET.get("q", "").strip()
    vendor_name = request.GET.get("vendor", "").strip()

    items = CatalogItem.objects.select_related("vendor").order_by("id")
    searched = False

    if vendor_name != "":
        items = items.filter(vendor__name__icontains=vendor_name)
        searched = True

    if q != "":
        normalized = q.upper()
        items = items.filter(Q(mpn_normalized__icontains=normalized)
                             | Q(description__icontains=q))
        searched = True

    if not searched:
        items = CatalogItem.objects.none()

    paginator = Paginator(items, 50)
    page = paginator.get_page(request.GET.get("page"))

    total_items = 0
    if not searched:
        total_items = CatalogItem.objects.count()

    vendor_names = Vendor.objects.values_list('name', flat=True)

    context = {
        "q": q,
        "vendor": vendor_name,
        "searched": searched,
        "page": page,
        "vendor_names": vendor_names,
        "total_items": total_items
    }

    return render(request, 'index.html', context)
