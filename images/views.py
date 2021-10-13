from django.contrib.messages.api import success
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import JsonResponse
from .forms import ImageCreateForm,ImageEditForm
from .models import Image
from common.decorators import ajax_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator 
from actions.utils import create_action
import redis
from django.conf import settings

r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
     db=settings.REDIS_DB
)

@login_required
def image_create(request):
    if request.method == 'POST':
        form = ImageCreateForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            new_item = form.save(commit=False)
            new_item.user = request.user
            new_item.save()
            create_action(request.user, 'bookmarked image', new_item)
            messages.success(request,'Your image has been bookmarked successfully.')
            return redirect(new_item.get_absolute_url())
        else:
            messages.error(request,'There was an error in your field.')
        
    form = ImageCreateForm(request.GET)
    return render(request,'images/image/create.html',{'section': 'images', 'form':form})


def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id , slug=slug)
    total_views = r.incr(f'image:{image.id}:views')
    # zincrby is a set of images id with most image_ranking value.
    r.zincrby('image_ranking', 1, image.id)
    return render(
        request,'images/image/detail.html',{'section':'images',
         'image':image,'total_views':total_views
    })

@login_required
def image_ranking(request):
    image_ranking = r.zrange('image_ranking', 0, -1, desc=True)[:10]
    #[b'8', b'1', b'7', b'6', b'3', b'5', b'13']
    image_ranking_ids = [ int(id) for id in image_ranking ]
    #[8, 1, 7, 6, 3, 5, 13]
    # retrieve objects with ids in image_ranking_ids
    most_viewed = list(Image.objects.filter(id__in=image_ranking_ids))
    # sort images in irder if the list above, so it will be sorted from most view images to less.
    most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))
    return render(
        request, 'images/image/ranking.html',
    {'section':'image', 'most_viewed':most_viewed}
    )



@ajax_required
@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id') 
    image_action = request.POST.get('action') 
    if image_id and image_action:
        try:
            image = Image.objects.get(id=image_id)
            if image_action == 'like':
                image.likes.add(request.user)
                create_action(request.user, 'likes', image)
            else: 
                image.likes.remove(request.user)
            return JsonResponse({'status':'ok'})
        except:
            pass
    return JsonResponse({'status':'error'})



@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images,8)
    page = request.GET.get('page')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        images = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            return HttpResponse("")
        images = paginator.page(paginator.num_pages)
    if request.is_ajax():
        return render(request, 'images/image/list_ajax.html',{'section':'images', 'images':images})

    return render(request, 'images/image/list.html',{'section':'images', 'images':images})


@login_required
def delete_image(request, id):
    image = get_object_or_404(Image, id=id)
    if request.method =="POST" and request.user == image.user:
        image.delete()
        success('Your image has been successfully deleted.')
        return redirect('images/image/user_image.html')

    
    return render(request, 'images/image/delete.html',{'image':image})

@login_required
def edit_image(request, id):
    image = get_object_or_404(Image, id=id)
    if request.user != image.user:
        return redirect('images:list')
    form = ImageEditForm(instance=image)
    if request.method =="POST":
        if form.is_valid():
            form.save()
        success('Your image has been successfully updated.')
        return redirect('images/image/edit.html')

    
    return render(request, 'images/image/edit.html',{'image':image})


@login_required
def user_images(request):
    images = Image.objects.filter(user=request.user)
    return render(request, 'images/image/user_image.html',{'images':images})

