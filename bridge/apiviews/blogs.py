
from bridge.serializers.articleSerializer import *
from bridge.models.articles import *
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter, OrderingFilter
from bridge.errors import AppValidation

class AdminArticlesViews(generics.ListCreateAPIView):
    serializer_class = ArticleSerializer
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('title', 'content', 'article_category__name','article_type')
    ordering_fields = ('title', 'content', 'article_category__name','article_type')

    def get_queryset(self):
        return Articles.objects.filter(company=self.request.user.systemCompany)

    def perform_create(self, serializer):
        a = Articles.objects.filter(
        article_type=self.request.data['article_type'], company=self.request.user.systemCompany)
        if a.exists():
                raise AppValidation(
                    self.request.data['article_type']+" already exists.Please search and edit the existing article", status_code=400)
        else:
            serializer.save(company=self.request.user.systemCompany,
                            article_category=Category.objects.get(
                                id=self.request.data['article_category'])
                            )


class AdminArticleView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ArticleSerializer
    lookup_field = 'id'
    queryset = Articles.objects.all()



class PublicArticlesViews(generics.ListAPIView):
    serializer_class = ArticleSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        return Articles.objects.filter(company__domain=self.kwargs['domain_name'],article_type=ArticleTypes.blog.value)

class TermsPrivacyListView(generics.RetrieveAPIView):
    serializer_class = ArticleSerializer
    permission_classes = (AllowAny,)
    lookup_field = 'article_type'
    def get_queryset(self):
        return Articles.objects.filter(company__domain=self.kwargs['domain_name'])
class ArticleTypesView(APIView):
    def get(self,request):
        return Response([{"type": ArticleTypes.blog.value},
                      {"type": ArticleTypes.user_terms.value},
                      {"type":ArticleTypes.privacy_policy.value}
                     ])
class PublicArticleView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ArticleSerializer
    lookup_field = 'id'
    queryset = Articles.objects.all()


class CategoryViews(generics.ListCreateAPIView):
    serializer_class = ArticleCategorySerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        return Category.objects.filter(company=self.request.user.systemCompany)

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.systemCompany)


class CategoryView(generics.RetrieveUpdateDestroyAPIView, generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ArticleCategorySerializer
    queryset = Category.objects.all()
    lookup_field = 'id'

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.systemCompany)


class BlogByCategoryView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ArticleCategorySerializer
    lookup_field = 'article_category'
    queryset = Articles.objects.all()
