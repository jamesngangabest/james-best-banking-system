from rest_framework import serializers
from bridge.models.articles import *
class ArticleSerializer(serializers.ModelSerializer):
    summary = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    def get_summary(self,obj):
        if obj.content:
            return obj.content[0:100]
        else:
            return None
    def get_category_name(self,obj):
        if obj.article_category:
            return obj.article_category.name

            
    class Meta:
        model = Articles
        fields = ('title','content','date_pub','article_category','category_name','summary','id','article_type')

class ArticleCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name','id')
