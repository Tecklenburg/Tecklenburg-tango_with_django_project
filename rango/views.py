from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime


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

    # call the helper function for the cookies handler to increase counter
    visitor_cookie_handler(request)

    # Return the rendered response to send to the client.
    # We make use of the shortcut function to make our lives easier.
    # Note that the first parameter is the template we wish to use.
    response = render(request, 'rango/index.html', context=context_dict)
    return response


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

@login_required()
def add_category(request):
    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            #redirect user back to index view
            return redirect('/rango/')
        else:
            print(form.errors)
    return render(request, 'rango/add_category.html', {'form': form})

@login_required()
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    # cannot add a page that does not exist
    if category is None:
        return redirect('/rango/')

    form = PageForm()

    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()

                return redirect(reverse('rango:show_category',
                                        kwargs={'category_name_slug':category_name_slug}))
        else:
            print(form.errors)
    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)

def register(request):
    # variable to state success status  of registration
    registered = False

    # if HTTP POST, then interested in data
    if request.method == 'POST':
        # grab information from UserForm and UserProfileForm
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            # save data from the form
            user = user_form.save()

            # hash password with the set_password method
            user.set_password(user.password)
            user.save()

            # sort out user profile instance do not commit to make changes
            profile = profile_form.save(commit=False)
            profile.user = user

            # check for profile picture
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # save UserProfile
            profile.save()

            # if reached successful
            registered = True
        else:
            # Invalid form
            print(user_form.errors, profile_form.errors)
    else:
        # not a Post, so render the form
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render the template
    return render(request, 'rango/register.html', context={'user_form': user_form,
                                                             'profile_form': profile_form,
                                                             'registered': registered})

def user_login(request):
    # if request is Post, try tu pull the important info
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # use django to check if this is a valid user
        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                # inactive account
                return HttpResponse("Your Rango account is disabled.")
        else:
            # Bad login details
            print(f"Invalid login details: {username},{password}")
            return HttpResponse("Invalid login details supplied")

    # If scenario is a get request
    else:
        return render(request, 'rango/login.html')

@login_required
def user_logout(request):
    # use django buil in logout function and redirect ot index
    logout(request)
    return redirect(reverse('rango:index'))

def about(request):
    context_dict ={}
    # call the helper function for the cookies handler
    visitor_cookie_handler(request)
    context_dict['visits'] = int(request.session['visits'])
    return render(request, 'rango/about.html', context_dict)

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')

def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

def visitor_cookie_handler(request):
    # Get the number of visits to the site
    # if exists, values casted to int
    # else default to 1

    # cookie values always stored as Strings so they need to be casted into proper data type
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')

    if(datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = last_visit_cookie

    request.session['visits'] = visits
