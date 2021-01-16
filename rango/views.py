from django.shortcuts import render
from rango.models import Category
from rango.models import Page
from django.http import HttpResponse


def index(request):
    # Query the database for Lsit of all categories
    # order list by number of likes
    # retrieve only the top 5
    # place list in context_dict, to be passed to template
    # - infront of likes to sort in descending order
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    # Construct a dictionary to pass to the template engine as its context.
    # Note the key boldmessage matches to {{boldmessage} in the template
    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list

    # Return the rendered response to send to the client.
    # We make use of the shortcut function to make our lives easier.
    # Note that the first parameter is the template we wish to use.
    return render(request, 'rango/index.html', context=context_dict)


def show_category(request, category_name_slug):
    # create context dict to pass to template rendering engine
    context_dict = {}

    try:
        # try to find a category with the given name
        # if no .get() raise DoesNotExist exception
        # get() method returns model instance or raises exception
        category = Category.objects.get(slug=category_name_slug)

        # Retrieve associated pages
        # filter( returns list of page objects or empty list
        pages = Page.objects.filter(category=category)

        # Add results list to template context under name pages
        context_dict['pages'] = pages

        # Also add category object from database to context dict
        # to verify existance in template
        context_dict['category'] = category
    except:
        # if there is no such category
        context_dict['category'] = None
        context_dict['pages'] = None

    # render the response and return to client
    return render(request, 'rango/category.html', context=context_dict )


def about(request):
    return render(request, 'rango/about.html')


