from django.contrib import admin
from .models import Account, Message, Response


class MessageAdmin(admin.ModelAdmin):
    list_display = (
        'to_phone_number',
        'from_phone_number',
        'status',
        'direction',
        'date_sent'
    )
    list_display_links = list_display
    list_filter = ('status', 'direction', 'date_sent')
    date_hierarchy = 'date_sent'
    ordering = ('-date_sent', )


class ResponseAdmin(admin.ModelAdmin):
    list_display = ('action', 'active', 'body', 'date_updated')
    list_display_links = list_display
    list_filter = ('action', 'active')


class AccountAdmin(admin.ModelAdmin):
    list_display = (
        'friendly_name',
        'owner_account_sid',
        'account_type',
        'status',
        'date_updated'
    )
    list_display_links = list_display


admin.site.register(Message, MessageAdmin)
admin.site.register(Response, ResponseAdmin)
admin.site.register(Account, AccountAdmin)
