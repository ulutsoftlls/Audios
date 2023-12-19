from django.urls import path
from .views import *
from analyzer import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.cache import cache_page

urlpatterns = [
    path('', cache_page(10)(AudiosHome.as_view()), name='home'),
    path('text/', text, name='text'),
    path('login/', login, name='login'),
    # path('register/', RegisterUser.as_view(), name='register'),
    path('audio/<int:audio_id>/', cache_page(120)(ShowAudio.as_view()), name='audio'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
