import django_filters
from users.models import Payment
from materials.models import Course, Lesson


class PaymentFilter(django_filters.FilterSet):
    course = django_filters.ModelChoiceFilter(
        field_name='paid_course',
        queryset=Course.objects.all(),
        label='Фильтр по курсу'
    )
    lesson = django_filters.ModelChoiceFilter(
        field_name='paid_lesson',
        queryset=Lesson.objects.all(),
        label='Фильтр по уроку'
    )
    payment_method = django_filters.ChoiceFilter(
        choices=Payment.PAYMENT_METHOD_CHOICES,
        label='Способ оплаты'
    )
    ordering = django_filters.OrderingFilter(
        fields=(
            ('payment_date', 'date_asc'),
            ('-payment_date', 'date_desc'),
        ),
        field_labels={
            'payment_date': 'По дате (возрастание)',
            '-payment_date': 'По дате (убывание)',
        }
    )

    class Meta:
        model = Payment
        fields = ['course', 'lesson', 'payment_method']