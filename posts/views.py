from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils import timezone
from django.db.models import Q

# from django.utils import timezone
from urllib.parse import quote_plus

# Create your views here.
# import Forms
from .forms import PostForm

# import Models
from .models import Post
from comments.models import Comment

# the logic handle the request the browser/client make
def post_create(request):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    # form = PostForm()
    form = PostForm(request.POST or None, request.FILES or None)
    context = {"form": form}
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        # message success
        messages.success(
            request, "<a href='#'>Successfully</a> Created", extra_tags="html_safe"
        )
        return HttpResponseRedirect(instance.get_absolute_url())
    return render(request, "post_form.html", context)


def post_detail(request, slug):
    # instance = Post.objects.get(id=3)
    instance = get_object_or_404(Post, slug=slug)
    if instance.draft == True or instance.publish > timezone.now().date():
        if not request.user.is_staff or not request.user.is_superuser:
            raise Http404
    share_str = quote_plus(instance.context)
    content_type = ContentType.objects.get_for_model(Post)
    obj_id = instance.id
    comments = Comment.objects.filter(content_type=content_type, object_id=obj_id)
    context = {
        "title": instance.title,
        "instance": instance,
        "share_string": share_str,
        "comments": comments,
    }
    return render(request, "post_detail.html", context)


def post_list(request):
    # queryset = Post.objects.filter(draft=False).filter(
    #     publish__lte=timezone.now()
    # )  # .all()  # .order_by("-timestamp")
    today = timezone.now().date()
    queryset = Post.objects.active()
    if request.user.is_staff or request.user.is_superuser:
        queryset = Post.objects.all()

    query = request.GET.get("q")
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query)
            | Q(context__icontains=query)
            | Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
        ).distinct()

    paginator = Paginator(queryset, 5)
    page_request_var = "page"
    page = request.GET.get(page_request_var)
    try:
        contact = paginator.page(page)
    except PageNotAnInteger:
        contact = paginator.page(1)
    except EmptyPage:
        contact = paginator.page(paginator.num_pages)

    context = {
        "object_list": contact,
        "title": "List",
        "page_request_var": page_request_var,
        "today": today,
    }
    # if request.user.is_authenticated:
    #     context = {"title": "My User List"}
    # else:
    #     context = {"title": "List"}
    # return HttpResponse("<h1>List</h1>")
    return render(request, "post_list.html", context)


def post_update(request, slug=None):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    instance = get_object_or_404(Post, slug=slug)
    form = PostForm(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        # message success
        messages.success(request, "Item Saved")
        return HttpResponseRedirect(instance.get_absolute_url())

    context = {"title": instance.title, "instance": instance, "form": form}
    return render(request, "post_form.html", context)


def post_delete(request, id=None):
    if not request.is_superuser:
        raise Http404
    instance = get_object_or_404(Post, id=id)
    instance.delete()
    return redirect("posts:list")
