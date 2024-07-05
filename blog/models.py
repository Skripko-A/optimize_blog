from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Count, Prefetch


class PostQuerySet(models.QuerySet):
    def popular(self):
        popular_posts = Post.objects.annotate(likes_count=Count('likes')).order_by('-likes_count')
        return popular_posts

    def fetch_with_comments_count(self):
        """ Функция позволяет получить QuerySet постов с указанием количества коментов к каждому посту

        Когда вам нужно "сериализовать" объекты Post. С использованием popular().annotate
        вы получите время загрузки около 11 с. С данной фукцией - несколько сотен мс, ценой в 3 запроса.
        """
        posts_with_comments_count = Post.objects.filter(id__in=self).annotate(comments_count=Count('comments'))
        return posts_with_comments_count

    def fresh_posts(self):
        fresh_posts = Post.objects.annotate(comments_count=Count('comments')).order_by('-published_at')
        return fresh_posts

    def fetch_with_tags(self):
        posts_with_tags = self.fetch_with_comments_count().prefetch_related(Prefetch('tags',
                                                                                     queryset=Tag.objects.popular()))
        return posts_with_tags


class TagQuerySet(models.QuerySet):
    def popular(self):
        popular_tags = self.annotate(posts_count=Count('posts')).order_by('-posts_count')
        return popular_tags


class Post(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    text = models.TextField('Текст')
    slug = models.SlugField('Название в виде url', max_length=200)
    image = models.ImageField('Картинка')
    published_at = models.DateTimeField('Дата и время публикации')

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        limit_choices_to={'is_staff': True})
    likes = models.ManyToManyField(
        User,
        related_name='liked_posts',
        verbose_name='Кто лайкнул',
        blank=True)
    tags = models.ManyToManyField(
        'Tag',
        related_name='posts',
        verbose_name='Теги')

    objects = PostQuerySet.as_manager()

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'пост'
        verbose_name_plural = 'посты'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args={'slug': self.slug})


class Tag(models.Model):
    title = models.CharField('Тег', max_length=20, unique=True)

    objects = TagQuerySet.as_manager()

    class Meta:
        ordering = ['title']
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('tag_filter', args={'tag_title': self.slug})

    def clean(self):
        self.title = self.title.lower()


class Comment(models.Model):
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        verbose_name='Пост, к которому написан',
        related_name='comments')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='comments')

    text = models.TextField('Текст комментария')
    published_at = models.DateTimeField('Дата и время публикации')

    class Meta:
        ordering = ['published_at']
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'

    def __str__(self):
        return f'{self.author.username} under {self.post.title}'
