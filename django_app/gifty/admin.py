from django.contrib import admin
from django.contrib.admin import sites

from .models import (
    AppManager,
    GenderCategory,
    PriceCategory,
    Product,
    AgeCategory
)


class CategoryInline(admin.TabularInline):
    model = None
    fields = ('is_active', )
    extra = 0

    def has_delete_permission(self, request, obj=None):
        return False


class AgeCategoryInline(CategoryInline):
    model = AgeCategory
    verbose_name = "나이대"
    verbose_name_plural = "나이대"


class PriceCategoryInline(CategoryInline):
    model = PriceCategory
    verbose_name = "가격대"
    verbose_name_plural = "가격대"


class GenderCategoryInline(CategoryInline):
    model = GenderCategory
    verbose_name = "성별"
    verbose_name_plural = "성별"


class AppManagerAdmin(admin.ModelAdmin):
    model = AppManager
    inlines = (AgeCategoryInline, PriceCategoryInline, GenderCategoryInline)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


class GiftyAdminSite(admin.AdminSite):
    app_orders = [
        {
            'name': 'gifty',
            'model_orders': ['앱관리', '상품관리']
        },
        {
            'name': 'user',
            'model_orders': ['사용자(들)']
        }
    ]

    def get_app_list(self, request):
        app_dict = self._build_app_dict(request)
        app_list = []

        for app in self.app_orders:
            app_list.append(app_dict[app['name']])
            models = app_list[-1]['models']
            ordered_models = []

            for model_name in app['model_orders']:
                ordered_models.append(
                    self.find_model(models, model_name)
                )
            app_list[-1]['models'] = ordered_models

        return app_list

    def find_model(self, models, name):
        for model in models:
            if model['name'] == name:
                return model


gifty_admin_site = GiftyAdminSite()
admin.site = gifty_admin_site
sites.site = gifty_admin_site


admin.site.register(AppManager, AppManagerAdmin)
admin.site.register(Product)
