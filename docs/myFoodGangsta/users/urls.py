from django.urls import path
from . import views

urlpatterns = [
    path('profile.html', views.profile, name='profile'),
    path('index.html', views.home, name='home'),
    path('about.html', views.about, name='about'),
    path('login.html', views.user_login, name='user_login'),
    path('signup.html', views.signup, name='signup'),
    path('allergy.html', views.allergy, name='allergy'),
    path('savedrecipes.html', views.savedrecipes, name='savedrecipes'),
    path('search/', views.recipesearch, name='search'),
    path('recipe.html', views.recipe, name='recipe'),
    #path('index.html', recipesearch, name='home'),  # Home page
]

#default code from da internet for recipe stuff (Putting in one app so they can both access the same templates and theres no weird crosswriting stuff)
# from django.urls import path
# from . import views

# urlpatterns = [
# path('run-script/', views.run_script_view, name='run_script'),
# ]    