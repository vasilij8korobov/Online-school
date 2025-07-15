from django.contrib import admin
from .models import Course, Lesson, Subscription
from django.utils import timezone
from .tasks import send_update_notification




@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'last_updated', 'preview_display')
    list_filter = ('owner', 'last_updated')
    search_fields = ('name', 'description')
    readonly_fields = ('preview_display',)

    def preview_display(self, obj):
        if obj.preview:
            return f'<img src="{obj.preview.url}" width="100" height="100" />'
        return "Нет изображения"

    preview_display.allow_tags = True
    preview_display.short_description = 'Превью'

    def save_model(self, request, obj, form, change):
        if change:
            # Проверяем, если курс обновляется, отправляем уведомление
            if obj.last_updated and (timezone.now() - obj.last_updated).total_seconds() > 14400:
                send_update_notification.delay(obj.id)
        obj.last_updated = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'owner', 'preview_display')
    list_filter = ('course', 'owner')
    search_fields = ('name', 'description')
    readonly_fields = ('preview_display',)

    def preview_display(self, obj):
        if obj.preview:
            return f'<img src="{obj.preview.url}" width="100" height="100" />'
        return "Нет изображения"

    preview_display.allow_tags = True
    preview_display.short_description = 'Превью'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'subscribed_at')
    list_filter = ('user', 'course')
    search_fields = ('user__email', 'course__name')
    readonly_fields = ('subscribed_at',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # При создании подписки отправляем уведомление
        if not change:
            send_update_notification.delay(obj.course.id)
