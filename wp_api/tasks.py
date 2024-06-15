import json
from celery import shared_task
from celery.utils.log import get_task_logger
from wp_api.wcapi import WcApi
from wp_api.models import (Course, CourseProduct, Category, default_image)
from main.serializers import CourseSerializer, serializers

logger = get_task_logger(__name__)

wcapi = WcApi()


class CourseProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseProduct
        fields = "__all__"


@shared_task(name="create_course_product", bind=True)
def create_course_product(self, pk=None, course_in=None):
    try:
        # course = course_in or CourseProduct.objects.get(pk=pk)
        

        # content = serializer.data
        # Field values required to create a course on talentLMS
        course_creation_keys = {
            "name"
            "description",
            "regular_price",
            # "category",
            "image"
        }
        for course in CourseProduct.objects.all():
            serializer = CourseProductSerializer(course)
            content = serializer.data
            tmp = {c: content[c] for c in content.keys() & course_creation_keys}
            # cat = Category.get_create(tmp.get('category'))
            payload = {
                "name": tmp.get('name'),
                "type": "custom",
                "regular_price": tmp.get('regular_price'),
                "description": tmp.get('description'),
                # "categories": [
                #     {
                #         "id": cat.cat_id
                #     }
                # ],
                "images": [
                    {"src": tmp.get('image') or default_image}
                ]
            }
            ret = wcapi.courses.create(payload)
            course.product_id = ret.get('id')
            course.save()
        # course_product, created = CourseProduct.objects.update_or_create(course_id={
        #     'product_id': ret.get('id'),
        #     # 'category': cat,
        #     # 'course': course
        # })

    except Exception as exc:
        logger.exception(exc)

def load_category(name):
    wcapi.categories.read(params={'per_page': 100})

def load_all_categories():
    cats = Course.objects.values_list('category', flat=True).distinct()
    for cat in cats:
        c = Category.get_create(cat)


def load_all_courses():
    course_ids = Course.objects.values_list('id', flat=True)
    for pk in course_ids:
        create_course_product(pk=pk)
