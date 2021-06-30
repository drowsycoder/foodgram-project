from decimal import Decimal

from django.db import IntegrityError, transaction
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404

from recipes.models import Ingredient, Recipe, RecipeIngredient


def get_recipes_by_tags(tags):
    return Recipe.objects.filter(tags__name__in=tags)


def get_ingredients(request):
    result = {}
    for key, value in request.POST.items():
        if key.startswith('nameIngredient'):
            num = key.split('_')[1]
            result[value] = request.POST[f'valueIngredient_{num}']
    return result


def save_recipe(request, form, author=None):
    try:
        recipe = form.save(commit=False)
        recipe.author = author or request.user

        with transaction.atomic():
            recipe.save()
            RecipeIngredient.objects.filter(
                recipe=recipe
            ).delete()

            ingredients = get_ingredients(request)
            recipe_ingredients = []
            for name, quantity in ingredients.items():
                ingredient = get_object_or_404(Ingredient, name=name)
                obj = RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient,
                    quantity=abs(Decimal(quantity.replace(',', '.')))
                )
                recipe_ingredients.append(obj)
            RecipeIngredient.objects.bulk_create(recipe_ingredients)
            form.save_m2m()
            return recipe

    except IntegrityError:
        return HttpResponseBadRequest
