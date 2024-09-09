from django.contrib import admin
from ..models.order_models import Order, OrderItem, OrderAddress


class OrderItemInline(admin.StackedInline):
    model = OrderItem
    
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    #list_display = ("__str__", "refund_request")
    list_display = ("get_user_name", "get_order_code", "get_created_date", "get_registered_order_id","get_order_status", "refund_request")
    list_filter = ("order_status","code")
    readonly_fields = [
        "compelted_at",
    ]
    inlines = [OrderItemInline]

    def get_user_name(self, obj):
        return obj.user.name
    get_user_name.short_description = "User"

    def get_order_code(self, obj):
        return obj.code
    get_order_code.short_description = "Order Code"

    def get_created_date(self, obj):
        return obj.created_at.date()
    get_created_date.short_description = "Date"

    def get_registered_order_id(self, obj):
        return obj.registered_order_id
    get_registered_order_id.short_description = "Register ID"

    def refund_request(self, obj):
        return True if obj.refund_order else False
    refund_request.boolean = True
    refund_request.short_description = "Refund Requested"

    def get_order_status(self, obj):
            return obj.order_status
    get_order_status.short_description = "Order Status"



    ##colored status
    class Media:
        css = {
            'all': ('admin/css/custom_admin_order.css',)
        }
        js = ('admin/js/custom_admin_order.js',)

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(OrderAddress)
