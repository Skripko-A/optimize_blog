from django.contrib import admin
from blog.models import Post, Tag, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    search_fields = ('title', 'slug', 'author', 'tags')
    readonly_fields = ('published_at',)
    list_display = ('title', 'author', 'slug')
    list_filter = ('tags', 'published_at')
    raw_id_fields = ('author', 'likes', 'tags')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ('title', 'posts')
    list_display = ('title',)
    raw_id_fields = ('posts',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    search_fields = ('post', 'author')
    readonly_fields = ('published_at',)
    list_display = ('author', 'post')
    list_filter = ('published_at',)
    raw_id_fields = ('author', 'post')
