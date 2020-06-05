import re
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
from comments.forms import CommentForm
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


def post_detail(request, slug=None):
    instance = get_object_or_404(Post, slug=slug)
    if instance.draft == True or instance.publish > timezone.now().date():
        if not request.user.is_staff or not request.user.is_superuser:
            raise Http404
    share_str = quote_plus(instance.context)

    initial_data = {
        "content_type": instance.get_content_type,
        "object_id": instance.id,
    }

    form = CommentForm(request.POST or None, initial=initial_data)
    if form.is_valid():
        c_type = form.cleaned_data.get("content_type")
        # print(c_type)
        new_type = c_type.split("|")
        # print(new_type[0].strip())
        content_type = ContentType.objects.get(
            app_label=new_type[0].strip(), model=new_type[1].strip()
        )
        obj_id = form.cleaned_data.get("object_id")
        content_data = form.cleaned_data.get("content")
        parent_obj = None
        try:
            parent_id = int(request.POST.get("parent_id"))
        except:
            parent_id = None
        if parent_id:
            parent_qs = Comment.objects.filter(id=parent_id)
            if parent_qs.exists() and parent_qs.count() == 1:
                parent_obj = parent_qs.first()

        new_comment, created = Comment.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=obj_id,
            content=content_data,
            parent=parent_obj,
        )
        return HttpResponseRedirect(new_comment.content_object.get_absolute_url())

    comments = instance.comments  # Comment.objects.filter_by_instance(instance)
    context = {
        "title": instance.title,
        "instance": instance,
        "share_string": share_str,
        "comments": comments,
        "comment_form": form,
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
