# vendor,description,mpn,list_price,naspo_price,source_file,dupicate_vendor_mpn
# Invictus Apps DBAPrepared 911,SE-Assist-Implementation,SE-Assist-Hardware,3000.0,2940.0,NASPO_Price_Catalog_A-E_10.15.2025.xlsx,False
# Invictus Apps DBAPrepared 911,SE-Assist-Implementation,SE-Assist-Implementation,15000.0,14700.0,NASPO_Price_Catalog_A-E_10.15.2025.xlsx,False
# Invictus Apps DBAPrepared 911,SE-Assist-Implementation,SE-Assist-Training-OnSite,15000.0,14700.0,NASPO_Price_Catalog_A-E_10.15.2025.xlsx,False
# Invictus Apps DBAPrepared 911,SE-Assist-Implementation,SE-Assist-Training-Virtual,15000.0,14700.0,NASPO_Price_Catalog_A-E_10.15.2025.xlsx,False

from django.db import models
import uuid


class Vendor(models.Model):
    name = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.name


class CatalogItem(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT,
                               related_name="items")
    mpn = models.CharField(max_length=255, blank=True)
    mpn_normalized = models.CharField(max_length=255, blank=True,
                                      db_index=True)
    description = models.TextField(blank=True)
    list_price = models.DecimalField(max_digits=14, decimal_places=2,
                                     null=True, blank=True)
    naspo_price = models.DecimalField(max_digits=14, decimal_places=2,
                                      null=True, blank=True)
    source_file = models.CharField(max_length=80)
    duplicate_vendor_mpn = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.vendor.name} - {self.mpn}"
