from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.http import JsonResponse

import json
from .models import Item, Review

from marshmallow import Schema, fields, validates, ValidationError
from marshmallow.validate import Length


class ItemSchema(Schema):
    title = fields.Str(validate=Length(1, 64), required=True)
    description = fields.Str(validate=Length(1, 1024), required=True)
    price = fields.Field(required=True)

    @validates('price')
    def is_price_suitable(self, price):
        try:
            price = int(price)
            if not (1 <= price <= 1000000):
                raise ValueError
        except ValueError:
            raise ValidationError('Is not suitable')


@method_decorator(csrf_exempt, name='dispatch')
class AddItemView(View):
    def post(self, request):
        try:
            document = json.loads(request.body)
            schema = ItemSchema(strict=True)
            schema.load(document)
            item = Item(title=document['title'],
                        description=document['description'],
                        price=document['price'])
            item.save()
            data = {
                'id': item.pk
            }
            return JsonResponse(data, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'errors': 'Invalid JSON'}, status=400)
        except ValidationError:
            return JsonResponse({'errors': 'Validation failed'}, status=400)


class ReviewSchema(Schema):
    text = fields.Str(validate=Length(1, 1024), required=True)
    grade = fields.Field(required=True)

    @validates('grade')
    def is_grade_suitable(self, grade):
        try:
            grade = int(grade)
            if not (1 <= grade <= 10):
                raise ValueError
        except ValueError:
            raise ValidationError('Is not suitable')


@method_decorator(csrf_exempt, name='dispatch')
class PostReviewView(View):
    def post(self, request, item_id):
        try:
            document = json.loads(request.body)
            schema = ReviewSchema(strict=True)
            schema.load(document)
            review = Review(grade=document['grade'],
                            text=document['text'],
                            item=Item.objects.get(pk=item_id))
            review.save()
            data = {
                'id': review.pk
            }
            return JsonResponse(data, status=201)
        except Item.DoesNotExist:
            return JsonResponse({'errors': 'Does not exist'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'errors': 'Invalid JSON'}, status=400)
        except ValidationError:
            return JsonResponse({'errors': 'Validation failed'}, status=400)


class GetItemView(View):
    def get(self, request, item_id):
        try:
            item = Item.objects.get(pk=item_id)
            reviews = Review.objects.filter(item=item).order_by('-pk')[:5]
            data = {
                'id': item_id,
                'title': item.title,
                'description': item.description,
                'price': item.price,
                'reviews': [{
                    'id': review.pk,
                    'text': review.text,
                    'grade': review.grade
                } for review in reviews]
            }
            return JsonResponse(data, status=200)
        except Item.DoesNotExist:
            return JsonResponse({'errors': 'Does not exist'}, status=404)
