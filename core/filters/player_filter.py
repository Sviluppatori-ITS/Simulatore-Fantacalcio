import django_filters
from django.db.models import Q
from core.models import Player


class PlayerFilter(django_filters.FilterSet):
    overall_min = django_filters.NumberFilter(field_name='overall', lookup_expr='gte')
    overall_max = django_filters.NumberFilter(field_name='overall', lookup_expr='lte')
    overall = django_filters.NumberFilter(field_name='overall', lookup_expr='exact')

    main_role = django_filters.CharFilter(field_name='main_role', lookup_expr='icontains')
    role = django_filters.CharFilter(field_name='main_role', lookup_expr='icontains')

    value_min = django_filters.NumberFilter(field_name='value', lookup_expr='gte')
    value_max = django_filters.NumberFilter(field_name='value', lookup_expr='lte')
    value = django_filters.NumberFilter(field_name='value', lookup_expr='exact')

    fanta_value_min = django_filters.NumberFilter(field_name='fanta_value', lookup_expr='gte')
    fanta_value_max = django_filters.NumberFilter(field_name='fanta_value', lookup_expr='lte')
    fanta_value = django_filters.NumberFilter(field_name='fanta_value', lookup_expr='exact')

    name = django_filters.CharFilter(field_name='person__name', lookup_expr='icontains')
    surname = django_filters.CharFilter(field_name='person__surname', lookup_expr='icontains')

    nationality = django_filters.CharFilter(method='filter_nationality')
    continent = django_filters.CharFilter(method='filter_continent')

    class Meta:
        model = Player
        fields = [
            'main_role', 'role', 'overall_min', 'overall_max',
            'value_min', 'value_max', 'value',
            'fanta_value_min', 'fanta_value_max', 'fanta_value',
            'name', 'surname',
            'nationality', 'continent'
        ]
        # ordering = [
        #     'name', 'surname', 'overall', 'value', 'fanta_value',
        #     'main_role',
        # ]

    def filter_nationality(self, queryset, name, value):
        return queryset.filter(
            Q(person__main_nationality__name__icontains=value) |
            Q(person__main_nationality__code__icontains=value) |
            Q(person__other_nationalities__name__icontains=value) |
            Q(person__other_nationalities__code__icontains=value)
        ).distinct()

    def filter_continent(self, queryset, name, value):
        return queryset.filter(
            Q(person__main_nationality__continent__name__icontains=value) |
            Q(person__other_nationalities__continent__name__icontains=value) |
            Q(person__main_nationality__continent__code__icontains=value) |
            Q(person__other_nationalities__continent__code__icontains=value)
        ).distinct()
