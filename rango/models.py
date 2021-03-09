from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if self.views < 0:
            self.views = 0
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Page(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    url = models.URLField()
    views = models.IntegerField(default=0)
    last_visit = models.DateTimeField(default=timezone.now())

    def save(self, *args, **kwargs):
        if self.last_visit > timezone.now():
            self.last_visit = timezone.now()
        super(Page, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class UserProfile(models.Model):
    # links userprofile to user a User model instance
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # additional attributes
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)

    def __str__(self):
        return self.user.username


class Chat(models.Model):
    users = models.ManyToManyField(UserProfile)
    name = models.CharField(max_length=128)

    def __str__(self):
        out = self.name + ' '
        for user in self.users:
            out = out + user
        return out


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, default=0)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)

    content = models.CharField(max_length=1024)
    date = models.DateTimeField(default=timezone.now())
