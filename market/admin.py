from django.contrib import admin
from .models import Category, Product, UserProfile


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'unit', 'stock_quantity', 'is_available', 'is_active', 'updated_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'category__name')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('price', 'stock_quantity', 'is_active')
    ordering = ('-created_at',)
    
    @admin.display(boolean=True, description='In Stock')
    def is_available(self, obj):
        return obj.is_available


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'city', 'postal_code')
    search_fields = ('user__username', 'user__email', 'phone_number', 'city')
