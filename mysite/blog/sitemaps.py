from django.contrib.sitemaps import Sitemap
from .models import Post
from django.urls import reverse
from django.utils import timezone
from taggit.models import Tag, TaggedItem
from django.db.models import Count, Max

class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9
    def items(self):
        all_posts = Post.published.all()
        return (
         all_posts
        )
    def lastmod(self, obj):
        return obj.updated

class TaggedSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return (Tag.objects.annotate(
            post_count = Count('taggit_taggeditem_items')
        ).filter(post_count__gt = 0)
        )

    def location(self, obj):
        return reverse('blog:post_list_by_tag', args=[obj.slug])


    def lastmod(self, obj):
        # latest = (
        #     TaggedItem.objects
        #         .filter(tag=obj)
        #         .order_by('-content_object__updated')   # or .created
        #         .values_list('content_object__updated', flat=True)
        #         .first()
        # )
        latest = (
            Post.published
                .filter(tags=obj)                 # <-- direct M2M filter
                .aggregate(latest=Max('updated')) # or 'created'
        )
        return latest['latest']