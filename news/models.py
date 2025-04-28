from django.db import models
from django.contrib.auth.models import User

# Модель Author
class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        # Суммарный рейтинг всех постов автора * 3
        post_rating = sum(post.rating for post in self.post_set.all()) * 3
        # Суммарный рейтинг всех комментариев автора
        comment_rating = sum(comment.rating for comment in self.user.comment_set.all())
        # Суммарный рейтинг всех комментариев к статьям автора
        post_comment_rating = sum(
            sum(comment.rating for comment in post.comment_set.all()) for post in self.post_set.all()
        )
        self.rating = post_rating + comment_rating + post_comment_rating
        self.save()

    def __str__(self):
        return self.user.username


# Модель Category
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Название категории должно быть уникальным

    def __str__(self):
        return self.name


# Промежуточная модель для связи Post и Category
class PostCategory(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


# Модель Post
class Post(models.Model):
    ARTICLE = 'AR'  # Константа для типа 'Статья'
    NEWS = 'NW'  # Константа для типа 'Новость'

    # Выбор между статьей и новостью
    POST_TYPE_CHOICES = [
        (ARTICLE, 'Статья'),  # Тип 'Статья' с кодом 'AR'
        (NEWS, 'Новость')  # Тип 'Новость' с кодом 'NW'
    ]

    author = models.ForeignKey(Author, on_delete=models.CASCADE)  # Автор поста
    post_type = models.CharField(max_length=2, choices=POST_TYPE_CHOICES, default=NEWS)  # Тип поста (Статья/Новость)
    created_at = models.DateTimeField(auto_now_add=True)  # Дата и время создания поста
    categories = models.ManyToManyField(Category, through=PostCategory)  # Связь с категориями через промежуточную модель
    title = models.CharField(max_length=255)  # Заголовок поста
    content = models.TextField()  # Текст поста
    rating = models.IntegerField(default=0)  # Рейтинг поста

    # Метод для предварительного просмотра поста
    def preview(self):
        return f'{self.content[:124]}...' if len(self.content) > 124 else self.content

    # Метод для увеличения рейтинга поста
    def like(self):
        self.rating += 1
        self.save()

    # Метод для уменьшения рейтинга поста
    def dislike(self):
        self.rating -= 1
        self.save()

    def __str__(self):
        return self.title


# Модель Comment
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)  # Связь с постом
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Связь с пользователем (комментарии могут оставлять разные пользователи)
    content = models.TextField()  # Текст комментария
    created_at = models.DateTimeField(auto_now_add=True)  # Дата и время создания комментария
    rating = models.IntegerField(default=0)  # Рейтинг комментария

    # Метод для увеличения рейтинга комментария
    def like(self):
        self.rating += 1
        self.save()

    # Метод для уменьшения рейтинга комментария
    def dislike(self):
        self.rating -= 1
        self.save()

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"

