from decimal import Decimal, ROUND_HALF_UP
from typing import Any

import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction

from naspo.models import Vendor, CatalogItem

CSV_PATH = "data/clean/catalog_clean.csv"
BATCH_SIZE = 1000
PROGRESS_EVERY = 100000


def to_money(value):
    if pd.isna(value):
        return None
    return Decimal(str(value)).quantize(Decimal("0.01"),
                                        rounding=ROUND_HALF_UP)


def to_text(value):
    if pd.isna(value):
        return ""
    return str(value)


def normalize_mpn(value):
    return to_text(value).strip().upper()


class Command(BaseCommand):
    help = "Wipe and reload the catalog from data/clean/catalog_clean.csv"

    def handle(self, *args: Any, **options: Any):
        df = pd.read_csv(CSV_PATH, dtype={"vendor": str, "mpn": str,
                                          "description": str})
        with transaction.atomic():
            items_deleted = CatalogItem.objects.all().delete()[0]
            vendors_deleted = Vendor.objects.all().delete()[0]

            vendor_names = sorted(df["vendor"].dropna().unique())
            vendors = []
            for name in vendor_names:
                vendor = Vendor(name=name)
                vendors.append(vendor)

            print(vendors)
            Vendor.objects.bulk_create(vendors, batch_size=BATCH_SIZE)

            vendor_ids = {}
            for vendor in Vendor.objects.all():
                vendor_ids[vendor.name] = vendor.id

            batch = []
            created = 0
            for row in df.itertuples(index=False):
                item = CatalogItem(
                    vendor_id=vendor_ids[row.vendor],
                    mpn=to_text(row.mpn),
                    mpn_normalized=normalize_mpn(row.mpn),
                    description=to_text(row.description),
                    list_price=to_money(row.list_price),
                    naspo_price=to_money(row.naspo_price),
                    source_file=row.source_file,
                    duplicate_vendor_mpn=bool(row.duplicate_vendor_mpn),
                )
                batch.append(item)
                if len(batch) >= BATCH_SIZE:
                    CatalogItem.objects.bulk_create(batch,
                                                    batch_size=BATCH_SIZE)
                    created += len(batch)
                    batch = []
                    if created % PROGRESS_EVERY == 0:
                        print(f"Created {created} catalog items...")

            if len(batch) > 0:
                CatalogItem.objects.bulk_create(batch, batch_size=BATCH_SIZE)
                created += len(batch)

        flagged = CatalogItem.objects.filter(duplicate_vendor_mpn=True).count()
        print(f"Catalog load complete. Created {created} items, "
              f"deleted {items_deleted} items, deleted {vendors_deleted} "
              f"vendors, and flagged {flagged} duplicate vendor MPNs.")
