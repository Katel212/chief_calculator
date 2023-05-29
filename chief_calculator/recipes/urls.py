from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
from .views import HomeView

urlpatterns = [

    path('', HomeView.as_view(), name='index'),
    path('profile', views.profile, name='profile'),
    path('recipe/<int:id_item>', views.show_recipe, name='recipe_detail'),
    path('recipe/<int:id_item>/price/<str:store>', views.recipe_price, name='recipe_price'),
    path('recipe/<int:pk>/edit', HomeView.as_view(), name='edit_recipe'),
    path('recipe/add', HomeView.as_view(), name='add_recipe'),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
