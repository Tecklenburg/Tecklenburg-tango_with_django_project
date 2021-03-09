from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User

from rango.bing_search import run_query
from rango.models import Category, Page, UserProfile, Message, Chat
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm, ChatForm
# from django.contrib.auth import authenticate, login, logout
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

'''
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
        pages = Page.objects.filter(category=category).order_by('-views')

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
    return render(request, 'rango/category.html', context=context_dict)
'''

@login_required()
def add_category(request):
    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            # redirect user back to index view
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
                                        kwargs={'category_name_slug': category_name_slug}))
        else:
            print(form.errors)
    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)


'''
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
'''

'''
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
'''

'''
@login_required
def user_logout(request):
    # use django buil in logout function and redirect ot index
    logout(request)
    return redirect(reverse('rango:index'))
'''


def about(request):
    context_dict = {}
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

    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = last_visit_cookie

    request.session['visits'] = visits


'''
def goto_url(request):
    if request.method == 'GET':
        page_id = request.GET('page_id')
        try:
            selected_page = Page.objects.get(id=page_id)
        except:
            return redirect(reverse('rango:index'))
        selected_page.views = selected_page.views + 1
        selected_page.last_visit = timezone.now()
        selected_page.save()
        return (selected_page.url)
    return redirect(reverse('rango:index'))
'''


@login_required
def register_profile(request):
    form = UserProfileForm()

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)

        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()
            return redirect(reverse('rango:index'))
        else:
            print(form.errors)
    context_dict = {'form': form}
    return render(request, 'rango/profile_registration.html', context_dict)


class AboutView(View):
    def get(self, request):
        context_dict = {}

        visitor_cookie_handler(request)
        context_dict['visits'] = request.session['visits']

        return render(request, 'rango/about.html', context_dict)


class AddCategoryView(View):
    @method_decorator(login_required)
    def get(self, request):
        form = CategoryForm()
        return render(request, 'rango/add_category.html', {'form': form})

    @method_decorator(login_required)
    def post(self, request):
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return redirect(reverse('rango:index'))
        else:
            print(form.errors)

        return render(request, 'rango/add_category.html', {'form': form})


class ProfileView(View):
    def get_user_details(self, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None

        user_profile = UserProfile.objects.get_or_create(user=user)[0]
        form = UserProfileForm({'website': user_profile.website,
                                'picture': user_profile.picture})
        return (user, user_profile, form)

    @method_decorator(login_required)
    def get(self, request, username):
        try:
            (user, user_profile, form) = self.get_user_details(username)
        except TypeError:
            return redirect(reverse('rango:index'))

        context_dict = {'user_profile': user_profile,
                        'selected_user': user,
                        'form': form}
        return render(request, 'rango/profile.html', context_dict)

    @method_decorator(login_required)
    def post(self, request, username):
        try:
            (user, user_profile, form) = self.get_user_details(username)
        except TypeError:
            return redirect(reverse('rango:index'))

        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)

        if form.is_valid():
            form.save(commit=True)
            return redirect('rango:profile', user.username)
        else:
            print(form.errors)

        context_dict = {'user_profile': user_profile,
                        'selected_user': user,
                        'form': form}
        return render(request, 'rango/profile.html', context_dict)


class ListProfilesView(View):
    @method_decorator(login_required)
    def get(self, request):
        profiles = UserProfile.objects.all()
        return render(request, 'rango/list_profiles.html', {'user_profile_list': profiles})


class LikeCategoryView(View):
    @method_decorator(login_required)
    def get(self, request):
        category_id = request.GET['category_id']

        try:
            category = Category.objects.get(id=int(category_id))
        except Category.DoesNotExist:
            return HttpResponse(-1)
        except ValueError:
            return HttpResponse(-1)

        category.likes = category.likes + 1
        category.save()

        return HttpResponse(category.likes)


def get_category_list(max_results=0, starts_with=''):
    category_list = []

    if starts_with:
        category_list = Category.objects.filter(name__istartswith=starts_with)

    if max_results > 0:
        if len(category_list) > max_results:
            category_list = category_list[:max_results]

    return category_list


class CategorySuggestionView(View):
    def get(self, request):
        if 'suggestion' in request.GET:
            suggestion = request.GET['suggestion']
        else:
            suggestion = ''

        category_list = get_category_list(max_results=8, starts_with=suggestion)

        if len(category_list) == 0:
            category_list = Category.objects.order_by('-likes')

        return render(request, 'rango/categories.html', {'categories': category_list})


class GotoView(View):
    def get(self, request):
        page_id = request.GET.get('page_id')
        try:
            selected_page = Page.objects.get(id=page_id)
        except Page.DoesNotExist:
            return redirect(reverse('rango:index'))
        selected_page.views = selected_page.views + 1
        selected_page.last_visit = timezone.now()
        selected_page.save()
        return redirect(selected_page.url)

'''
def search(request):
    result_list = []
    query = ""
    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            result_list = run_query(query)

    return render(request, 'rango/search.html', {'result_list': result_list, 'search_term': query})
'''


class ShowCategory(View):
    def get(self, request, category_name_slug):
        # create context dict to pass to template rendering engine
        context_dict = {}
        try:
            # try to find a category with the given name
            # if no .get() raise DoesNotExist exception
            # get() method returns model instance or raises exception
            category = Category.objects.get(slug=category_name_slug)

            # Retrieve associated pages
            # filter( returns list of page objects or empty list
            pages = Page.objects.filter(category=category).order_by('-views')

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
        return render(request, 'rango/category.html', context=context_dict)

    def post(self, request, category_name_slug):
        # create context dict to pass to template rendering engine
        context_dict = {}
        try:
            # try to find a category with the given name
            # if no .get() raise DoesNotExist exception
            # get() method returns model instance or raises exception
            category = Category.objects.get(slug=category_name_slug)

            # Retrieve associated pages
            # filter( returns list of page objects or empty list
            pages = Page.objects.filter(category=category).order_by('-views')

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

        context_dict['result_list'] = []
        context_dict['query'] = ""
        if request.method == 'POST':
            context_dict['query'] = request.POST['query'].strip()
            if context_dict['query']:
                context_dict['result_list'] = run_query(context_dict['query'])

        return render(request, 'rango/category.html', context_dict)


class SearchAddPageView(View):
    @method_decorator(login_required)
    def get(self, request):
        category_id = request.GET['category_id']
        title = request.GET['title']
        url = request.GET['url']

        try:
            category = Category.objects.get(id=int(category_id))
        except Category.DoesNotExist:
            return HttpResponse('Error - category not found')
        except ValueError:
            return HttpResponse('Error - bad category ID.')

        p = Page.objects.get_or_create(category=category,
                                       title=title,
                                       url=url)
        pages = Page.objects.filter(category=category).order_by('-views')
        return render(request, 'rango/page_listing.html', {'pages': pages})


class AddPageView(View):
    def get_category_name(self, category_name_slug):
        """
        A helper method that was created to demonstrate the power of class-based views.
        You can reuse this method in the get() and post() methods!
        """
        try:
            category = Category.objects.get(slug=category_name_slug)
        except Category.DoesNotExist:
            category = None

        return category

    @method_decorator(login_required)
    def get(self, request, category_name_slug):
        form = PageForm()
        category = self.get_category_name(category_name_slug)

        if category is None:
            return redirect(reverse('rango:index'))

        context_dict = {'form': form, 'category': category}
        return render(request, 'rango/add_page.html', context_dict)

    @method_decorator(login_required)
    def post(self, request, category_name_slug):
        form = PageForm(request.POST)
        category = self.get_category_name(category_name_slug)

        if category is None:
            return redirect(reverse('rango:index'))

        if form.is_valid():
            page = form.save(commit=False)
            page.category = category
            page.views = 0
            page.save()

            return redirect(reverse('rango:show_category', kwargs={'category_name_slug': category_name_slug}))
        else:
            print(form.errors)

        context_dict = {'form': form, 'category': category}
        return render(request, 'rango/add_page.html', context=context_dict)


class ChatView(View):
    def get(self, request, chat_id, user_id):
        chat = Chat.objects.get(id=int(chat_id))
        context_dict = {}
        context_dict['chat_id'] = chat_id
        context_dict['user_id'] = int(user_id)
        context_dict['users'] = []
        for user in chat.users.all():
            context_dict['users'].append(user.user)
        context_dict['name'] = chat.name
        context_dict['messages'] = Message.objects.filter(chat=chat).order_by('date')
        return render(request, 'rango/chat.html', context=context_dict)


class ChatAddMessageView(View):
    @method_decorator(login_required)
    def get(self, request):
        user_id = request.GET['user_id']
        user = User.objects.get(id=user_id)
        message = request.GET['message']
        chat_id = request.GET['chat_id']
        chat = Chat.objects.get(id=chat_id)
        Message.objects.create(sender=user, content=message, date=timezone.now(), chat=chat)
        messages = Message.objects.order_by('date')
        return render(request, 'rango/chat_log.html', {'messages': messages})


# combine with ChatAddMessageView
class MessageCheckView(View):
    @method_decorator(login_required)
    def get(self, request):
        latest_client = int(request.GET['latest_message_id'])
        chat_id = int(request.GET['chat_id'])
        chat = Chat.objects.get(id=chat_id)
        latest_server = Message.objects.filter(chat=chat).order_by('-date')[0].id

        if latest_client == latest_server:
            out = False
        else:
            out = latest_server
        return HttpResponse(out)


class ChatUpdateView(View):
    @method_decorator(login_required)
    def get(self, request):
        chat_id = int(request.GET['chat_id'])
        chat = Chat.objects.get(id=chat_id)
        messages = Message.objects.filter(chat=chat).order_by('date')
        return render(request, 'rango/chat_log.html', {'messages': messages})


class NewChatView(View):
    @method_decorator(login_required)
    def get(self, request, user_id):
        context_dict ={}
        context_dict['form'] = ChatForm()
        context_dict['user_id'] = int(user_id)
        context_dict['user_profile_list'] = UserProfile.objects.all()
        return render(request, 'rango/new_chat.html', context_dict)

    @method_decorator(login_required)
    def post(self, request, user_id):
        user_ids = request.POST.get('users').split(',')
        user_ids.append(user_id)
        form = ChatForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            for u_id in user_ids:
                user = User.objects.get(id=int(u_id))
                print(user)
                user_profile = UserProfile.objects.get(user=user)
                form.instance.users.add(user_profile)
            return redirect(reverse('rango:index'))
        else:
            print(form.errors)
        return redirect(reverse('rango:new_chat',
                                kwargs={'user_id': user_id}))


class ChatsView(View):
    @method_decorator(login_required)
    def get(self, request, user_id):
        context_dict = {}
        user = User.objects.get(id=int(user_id))
        user_profile = UserProfile.objects.get(user=user)
        chats = user_profile.chat_set.all()

        chat_collection = []
        for chat in chats:
            dict = {}
            dict['chatid'] = chat.id
            dict['name'] = chat.name
            users = []
            for u in chat.users.all():
                if u.user.id != int(user_id):
                    users.append(u.user.username)
            dict['users'] = users
            chat_collection.append(dict)

        return render(request, 'rango/chats.html', {'chats': chat_collection, 'user_id': user_id})
