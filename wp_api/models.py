from django.db import models
from main.models import (
    BaseModel,
    Course,
)
from wp_api.wcapi import (WcApi, settings)
from tools.model_extra import HTMLField
from django.core.exceptions import ObjectDoesNotExist

# Create your models here.
ORDER_STATUSES = (
    ('pending', 'Pending'),
    ('processing', 'Processing'),
    ('on-hold', 'On-Hold'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
    ('refunded', 'Refunded'),
    ('failed', 'Failed'),
    ('trash', 'Trash')
)

wcapi = WcApi()
default_image = getattr(settings, 'BASE_URL', 'https://api-staging.deviare.co.za/static/images/default.png')


class WpAPIModel(models.Model):
    # objects = WpAPIManager()

    class Meta:
        abstract = True

    def _get_object(self, model, obj_id):
        try:
            return model.objects.get(pk=obj_id)
        except model.DoesNotExist:
            pass

    def save(self, override=False, **kwargs):
        super(WpAPIModel, self).save(**kwargs)

    def delete(self, override=False):
        super(WpAPIModel, self).delete()


class Category(models.Model):
    name = models.CharField(max_length=255, default='', blank=True)
    image = models.TextField(default=default_image)
    cat_id = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"Category:{self.name}"

    @classmethod
    def get_create(cls, name):
        qs = cls.objects.filter(name=name)
        if not qs.exists():
            c = cls(name=name)
            r = wcapi.categories.create({'name': name, 'image': {'src': default_image}})
            c.cat_id = int(r.get('id'))
            c.save()
            return c
        return qs.first()


class CourseProduct(WpAPIModel):
    name = models.CharField(max_length=255, default='', blank=True)
    product_id = models.IntegerField(default=0)
    category = models.ForeignKey(Category, related_name='courses', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='wc_product', on_delete=models.CASCADE)
    description = HTMLField(default='', null=True, blank=True)
    image = models.CharField(max_length=255,null=True,  default=default_image)
    regular_price = models.FloatField(null=True, default=0.0)

    class Meta:
        verbose_name = "Course Product"
        verbose_name_plural = "Course Products"

    def __str__(self):
        return f"Course:{self.course.name}"


class Order(BaseModel):
    raw_data = models.TextField()
    status = models.CharField(choices=ORDER_STATUSES, default='pending',max_length=150)
    order_id = models.CharField(max_length=255, default='', blank=True)

    number = models.CharField(max_length=255, default='', blank=True)
    order_key = models.CharField(max_length=255, default='', blank=True)
    customer_id = models.CharField(max_length=255, default='', blank=True)
    customer_ip_address = models.CharField(max_length=255, default='', blank=True)
    customer_user_agent = models.CharField(max_length=255, default='', blank=True)
    customer_note = models.TextField(default='')
   
    date_paid_gmt = models.DateTimeField(null=True)
    date_completed_gmt = models.DateTimeField(null=True)
    
    billing = models.TextField(default='{}')
    line_items = models.TextField(default='[]')

    sent_mail = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return f"Order {self.status} - ({self.order_id})"