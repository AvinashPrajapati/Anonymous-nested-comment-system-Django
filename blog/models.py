from django.db import models
from django.shortcuts import render
from django.urls import reverse


class IpModel(models.Model):
    ip = models.CharField(max_length=100)

    def __str__(self):
        return self.ip


class Blog(models.Model):
    title = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=550)
    views = models.ManyToManyField(IpModel, related_name="post_views", blank=True)
    likes = models.ManyToManyField(IpModel, related_name="post_likes", blank=True)

    def __str__(self):
        return self.title

    def total_views(self):
        return self.views.count()

    def total_likes(self):
        return self.likes.count()

    def get_absolute_url(self):
        return reverse("blog:post_detail", args=[self.id])

    def get_comments(self):
        return self.comments.filter(parent=None).filter(active=True)


class MailBox(models.Model):
    email = models.EmailField(null=True, blank=True)
    token = models.CharField(max_length=10, null=True, blank=True)
    recieved = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class Comment(models.Model):
    post = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="comments")
    commenter = models.OneToOneField(
        MailBox, on_delete=models.SET_NULL, null=True, blank=True
    )
    name = models.CharField(max_length=50)
    email = models.EmailField()
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE)
    body = models.TextField()
    level = models.PositiveSmallIntegerField(default=0)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ("created",)

    def __str__(self):
        return self.body

    def get_comments(self):
        return Comment.objects.filter(parent=self).filter(active=True)


# Create your models here.
