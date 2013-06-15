from django.contrib import admin
from apps.pricelist.models import *


class OrientationAdmin(admin.ModelAdmin):
    pass

class SizeAdmin(admin.ModelAdmin):
    pass

class WeightAdmin(admin.ModelAdmin):
    pass

class CoatingAdmin(admin.ModelAdmin):
    pass

class FoldAdmin(admin.ModelAdmin):
    pass

class SidesAdmin(admin.ModelAdmin):
    pass

class MediaAdmin(admin.ModelAdmin):
    pass

class PrintingAdmin(admin.ModelAdmin):
    pass

class CornersAdmin(admin.ModelAdmin):
    pass

class PriceAdmin(admin.ModelAdmin):
    pass


admin.site.register(Orientation, OrientationAdmin)
admin.site.register(Size, SizeAdmin)
admin.site.register(Weight, WeightAdmin)
admin.site.register(Coating, CoatingAdmin)
admin.site.register(Fold, FoldAdmin)
admin.site.register(Sides, SidesAdmin)
admin.site.register(Media, MediaAdmin)
admin.site.register(Printing, PrintingAdmin)
admin.site.register(Corners, CornersAdmin)
admin.site.register(Price, PriceAdmin)
