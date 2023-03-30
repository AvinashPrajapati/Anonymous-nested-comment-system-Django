from django.shortcuts import render, reverse
from django.views.generic import ListView, DetailView
from .models import *
from django.shortcuts import render, get_object_or_404, redirect
from .forms import CommentForm
from django.http import HttpResponseRedirect

# Create your views here.


class PostIndexView(ListView):
    model = Blog
    template_name = "blog.html"
    queryset = Blog.objects.all()
    context_object_name = "posts"
    # def get_context_data(self, **kwargs):
    #     context = super(PostIndexView, self).get_context_data(**kwargs)
    #     context['genres'] = Genre.objects.all()

    # return context


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


# class PostDetailView(DetailView):
#     model = Blog
#     context_object_name = 'post'
#     template_name = 'blog-detail.html'

#     def get(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         context = self.get_context_data(object=self.object)

#         # adding like count
#         # like_status = False
#         # ip = get_client_ip(request)
#         # if self.object.likes.filter(id=IpModel.objects.get(ip=ip).id).exists():
#         #     like_status = True
#         # else:
#         #     like_status=False
#         # context['like_status'] = like_status
#         return self.render_to_response(context)

import datetime
from datetime import timezone


# likes ca be fetch here
def post_detail(request, pk):
    mails = MailBox.objects.all()
    for mail in mails:
        delta = datetime.datetime.now(timezone.utc) - mail.recieved
        if delta.seconds > 240:
            mail.delete()
    post = get_object_or_404(Blog, id=pk)
    # List of active comments for this post
    comments = post.comments.filter(active=True)
    # new_comment = None
    comment_form = CommentForm()
    if request.method == "POST":
        # A comment was posted
        token = request.POST.get("token")
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            mail_obj = None
            try:
                mail_obj = MailBox.objects.get(token=token)
            except Exception as e:
                pass
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            if mail_obj:
                new_comment.email = mail_obj.email
                new_comment.post = post
                mail_obj.delete()
                # delete all mail with time duration 1 h
                # Save the comment to the database
                # Save the comment to the database
                new_comment.save()
            else:
                return redirect(post.get_absolute_url() + "#" + str(new_comment.id))
            # redirect to same page and focus on that comment
            return redirect(post.get_absolute_url() + "#" + str(new_comment.id))
        else:
            comment_form = CommentForm()
    return render(
        request,
        "blog-detail.html",
        {"post": post, "comments": comments, "comment_form": comment_form},
    )


# handling reply, reply view
def reply_page(request):
    mails = MailBox.objects.all()
    for mail in mails:
        delta = datetime.datetime.now(timezone.utc) - mail.recieved
        if delta.seconds > 240:
            mail.delete()
    if request.method == "POST":
        token = request.POST.get("token")
        post_id = request.POST.get("post_id")  # from hidden input
        parent_id = request.POST.get("parent")  # from hidden input
        post_url = request.POST.get("post_url")  # from hidden input
        form = CommentForm(request.POST)

        if form.is_valid():
            mail_obj = None
            try:
                mail_obj = MailBox.objects.get(token=token)
            except Exception as e:
                pass
            reply = form.save(commit=False)
            if mail_obj:
                parent_level = Comment.objects.get(id=parent_id).level
                if parent_level < 3:
                    reply.level = parent_level + 1
                    reply.post = Blog(id=post_id)
                    reply.parent = Comment(id=parent_id)
                    reply.save()
                    mail_obj.delete()
                else:
                    return redirect(post_url + "#" + str(reply.id))
            return redirect(post_url + "#" + str(reply.id))
    return redirect("/")


from django.http import JsonResponse
from django.core.mail import send_mail
import string
import random
from django.conf import settings
import re


def mailSent(request):
    mails = MailBox.objects.all()
    for mail in mails:
        delta = datetime.datetime.now(timezone.utc) - mail.recieved
        if delta.seconds > 240:
            mail.delete()

    if request.method == "POST":
        sentMail = False
        regex_re = "[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+"
        email = request.POST.get("email")
        regex = re.compile(regex_re)
        e_lists = re.findall(regex_re, email)
        if len(e_lists) == 1:
            MailBox.objects.filter(email=email).delete()
            try:
                token = "".join(
                    random.choices(string.ascii_uppercase + string.digits, k=6)
                )
                subject = "welcome to Oneshothit world"
                message = f""
                message = f"Hi {email}, <br><p>your code:' <b>{token}</b> '<p>."
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [
                    email,
                ]
                send_mail(
                    subject, message, email_from, recipient_list, html_message=message
                )
                MailBox.objects.create(email=email, token=token)
                return JsonResponse({"message": "success"})
            except Exception as e:
                print(e)
                print("-------------")
                JsonResponse({"message": "failed"})
        else:
            JsonResponse({"message": "failed"})
    return JsonResponse({"message": "failed"})


def postLike(request, pk):
    post_id = request.POST.get("blog-id")
    post = Blog.objects.get(pk=post_id)
    ip = get_client_ip(request)
    if not IpModel.objects.filter(ip=ip).exists():
        IpModel.objects.create(ip=ip)
    if post.likes.filter(id=IpModel.objects.get(ip=ip).id).exists():
        post.likes.remove(IpModel.objects.get(ip=ip))
    else:
        post.likes.add(IpModel.objects.get(ip=ip))
    return HttpResponseRedirect(reverse("blog:post_detail", args=[post_id]))
