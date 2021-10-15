from django.contrib import admin
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import JsonLexer

from blood_tests.models import (
    BloodTestRejected,
    BloodTestsPassed,
    BloodTestsPassedFeedback,
)


class FeedbackInline(admin.StackedInline):
    model = BloodTestsPassedFeedback
    extra = 0
    readonly_fields = (
        "feedback_id",
        "package_code",
        "result_code",
        "description",
        "blood_test_passed",
    )
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class BloodTestPassedAdmin(admin.ModelAdmin):
    inlines = [
        FeedbackInline,
    ]

    fields = (
        "response_http_code",
        "response_time",
        "request_sent_pretty",
    )
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def request_sent_pretty(self, instance):
        response = instance.request_sent

        # Truncate the data
        response = response[:10000]

        # Get the Pygments formatter
        formatter = HtmlFormatter(style="colorful")

        # Highlight the data
        response = highlight(response, JsonLexer(), formatter)

        # Get the stylesheet
        style = "<style>" + formatter.get_style_defs() + "</style><br>"

        # Safe the output
        return mark_safe(style + response)

    request_sent_pretty.short_description = "Wysłane żądanie"


class BloodTestRejectedAdmin(admin.ModelAdmin):
    readonly_fields = ("request_senst",)

    fields = (
        "request_sent",
        "response_time",
        "error_code",
        "response_data",
    )
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(BloodTestRejected, BloodTestRejectedAdmin)
admin.site.register(BloodTestsPassed, BloodTestPassedAdmin)
