from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate,login
from django.contrib.auth.models import User
from .forms import LoginForm,UserRegistrationForm,UserEditForm,ProfileEditForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages
from .models import Contact, Profile
from actions.models import Action
from actions.utils import create_action 
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
# Create your views here.

def user_login(request):

    if request.method=='POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,username=cd['username'],password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request,user)
                    return HttpResponse('Authenticated successfully')
                
                return HttpResponse('Disabled account')

            return HttpResponse('invalid login')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form':form})

@login_required
def dashboard(request):
    actions = Action.objects.exclude(user=request.user)
    following_ids = request.user.following.values_list('id',flat=True)

    if following_ids:
        actions = actions.filter(user__id__in =  following_ids)
    # joining table's objects that relate to each other.
    actions = actions.select_related('user','user__profile').prefetch_related('target')[:10]
    # pagination
    paginator = Paginator(actions, 6)
    page = request.GET.get('page')
    try:
        actions = paginator.page(page)
    # if page wasn't integer
    except PageNotAnInteger:
        actions = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            return HttpResponse('')
        actions = paginator.page(paginator.num_pages)
    if request.is_ajax():
        return render(request, 'account/dashboard_ajax.html', {'section':'dashboard','actions':actions})
    return render(request, 'account/dashboard.html', {'section':'dashboard','actions':actions})


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(
                form.cleaned_data['password']
            )
            user.save()
            create_action(user, 'has created an account')
            return render(request,'account/register_done.html',{'user':user})
        else:
            form = UserRegistrationForm()
    form = UserRegistrationForm()
    return render(request,'account/register.html',{'form':form})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        u_form = UserEditForm(instance=request.user,data=request.POST)
        p_form = ProfileEditForm(request.POST,instance=request.user.profile,files=request.FILES)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request,'Your account has been updated successfuly')
            return redirect('account:edit')
        else:
            u_form = UserEditForm(instance=request.user)
            p_form = ProfileEditForm(instance=request.user.profile)
            messages.error(request,'There was an error in Your field data!!')
            return redirect('account:edit')
    u_form = UserEditForm(instance=request.user)
    p_form = ProfileEditForm(instance=request.user.profile)
    return render(request,'account/edit.html',{'u_form':u_form, 'p_form':p_form})

@login_required
def user_list(request):
    # users = User.objects.filter(is_active= True)
    profiles = Profile.objects.all()
    return render(request,'account/user/list.html',{'section': 'people','profiles':profiles})

@login_required
def user_detail(request,username):
    user = get_object_or_404(User,username=username, is_active=True)
    return render(request,'account/user/detail.html',{'section': 'people','user':user})


@login_required
@require_POST
def user_follow(request):
    user_id = request.POST.get('id')
    action  = request.POST.get('action')
    if user_id and action:
        try:
            user = User.objects.get(id=user_id) 
            if action == 'follow':
                # create relation from intermediary table
                Contact.objects.get_or_create(user_from = request.user , user_to=user)
                create_action(request.user, 'is following', user)
            else:
                Contact.objects.filter(user_from = request.user,
                user_to = user).delete()
            return JsonResponse({'status':'ok'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error'})
    return JsonResponse({'status':'error'})