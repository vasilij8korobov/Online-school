from rest_framework.pagination import PageNumberPagination


class LessonPagination(PageNumberPagination):
    page_size = 10  # Количество уроков на странице по умолчанию
    page_size_query_param = 'page_size'  # Параметр для изменения количества элементов на странице
    max_page_size = 50  # Максимальное количество элементов на странице


class CoursePagination(PageNumberPagination):
    page_size = 5  # Меньше курсов на странице, так как они более "тяжелые"
    page_size_query_param = 'page_size'
    max_page_size = 20
