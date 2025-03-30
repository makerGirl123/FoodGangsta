from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import authenticate, login
from django.contrib import messages
from . import recipescraper
from .models import User  # Import your custom User model
from .substitutions import identify_allergens

from django.views.decorators.cache import cache_page
from django.core.cache import cache

@cache_page(60 * 15)  # Cache the entire view for 15 minutes
def recipesearch(request):
    print("recipesearch view called")  # Debugging line
    if request.method == "POST":
        search_term = request.POST.get('search', '').strip()  # Get the search term from the form
        print(f"Searching for: {search_term}")  # Debugging line

        # Initialize variables
        searched_recipes = []
        submitflag = False

        # Check if the search term is cached
        cache_key = f"search_results_{search_term}"
        cached_results = cache.get(cache_key)

        if cached_results:
            print("Using cached results")
            searched_recipes = cached_results
            submitflag = True
        else:
            # If search term is provided, fetch the recipes
            if search_term:
                recipe_urls = recipescraper.findRecipes(search_term)  # Fetch recipe URLs
                print(f"Recipe URLs: {recipe_urls}\n")

                # Check if recipe_urls is empty
                if recipe_urls:
                    searched_recipes = [recipescraper.recipeScrape(url) for url in recipe_urls]  # Scrape details
                    print(f"Searched recipes: {searched_recipes}")  # Debugging line
                    submitflag = True  # Indicate that the form has been submitted

                    # Cache the results for future use
                    cache.set(cache_key, searched_recipes, 60 * 15)  # Cache for 15 minutes
                else:
                    print("No recipes found for the given search term.")

        # Return the rendered template with the results
        return render(request, 'index.html', {
            'searched_recipes': searched_recipes,
            'submitFlag': submitflag
        })

    # If not a POST request, redirect to home
    return redirect('home')

def profile(request):
    user = request.user
    # Parse the user's allergens, severities, and substitutions
    current_allergies = user.allergies.split(',') if user.allergies else []
    allergens = []

    for allergy in current_allergies:
        if '(' in allergy and ')' in allergy:
            allergen, rest = allergy.split('(', 1)
            severity, substitution = rest.split(')', 1) if ')' in rest else (rest, "")
            allergens.append({
                'name': allergen.strip(),
                'severity': severity.strip(),
                'substitution': substitution.strip().replace("Substitution: ", ""),
            })

    context = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'username': user.username,
        'allergens': allergens,
    }
    return render(request, 'profile.html', context)

def allergy(request):
    if request.method == 'POST':
        # Get the allergens, severities, and substitutions from the form
        allergens = request.POST.getlist('allergens[]')
        severities = request.POST.getlist('severities[]')
        substitutions = request.POST.getlist('substitutions[]')

        # Combine allergens, severities, and substitutions into a single list
        combined_allergies = []
        for allergen, severity, substitution in zip(allergens, severities, substitutions):
            if substitution.strip():  # Include substitution if provided
                combined_allergies.append(f"{allergen} ({severity}) - Substitution: {substitution}")
            else:
                combined_allergies.append(f"{allergen} ({severity})")

        # Save the updated allergies as a comma-separated string
        user = request.user
        user.allergies = ','.join(combined_allergies)
        user.save()

        return redirect('profile')  # Redirect to the profile page after saving the allergies

    # If GET request, load the current allergens and severities
    user = request.user
    current_allergies = user.allergies.split(',') if user.allergies else []
    allergens_with_severities = []

    for allergy in current_allergies:
        if '(' in allergy and ')' in allergy:
            allergen, rest = allergy.split('(', 1)
            severity, substitution = rest.split(')', 1) if ')' in rest else (rest, "")
            allergens_with_severities.append({
                'allergen': allergen.strip(),
                'severity': severity.strip(),
                'substitution': substitution.strip().replace("Substitution: ", ""),
            })

    return render(request, 'allergy.html', {'allergens_with_severities': allergens_with_severities})

@cache_page(60 * 15)  # Cache for 15 minutes
def home(request):
    searched_recipes = []

    # If the request is a POST (search), handle the search term
    if request.method == "POST":
        search_term = request.POST.get('search', '').strip()
        if search_term:
            recipe_urls = recipescraper.findRecipes(search_term)
            if recipe_urls:  # Check if recipe_urls is not empty
                searched_recipes = [recipescraper.recipeScrape(url) for url in recipe_urls]
            else:
                print("No recipes found for the given search term.")
    else:
        # Default behavior: scrape recipes from the default URL
        recipe_urls = recipescraper.findRecipes("fast")
        if recipe_urls:  # Check if recipe_urls is not empty
            searched_recipes = [recipescraper.recipeScrape(url) for url in recipe_urls]
        else:
            print("No recipes found for the default URL.")

    # Pass the first 8 recipes to the template
    return render(request, 'index.html', {
        'searched_recipes': searched_recipes[:8],  # Limit to 8 recipes
        'submitFlag': request.method == "POST"  # True if a search was performed
    })

def about(request):

         # Pass the user's info to the template
    context = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'username': request.user.username,
    }
    return render(request, 'about.html', context)


def savedrecipes(request):
    # Pass the user's info to the template
    context = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'username': request.user.username,
    }
    return render(request, 'savedrecipes.html', context)


def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to homepage or dashboard
        else:
            messages.error(request, "Invalid username or password")
    print(f"Current user: {request.user}")  # Print the current user (AnonymousUser if not logged in)
    return render(request, 'login.html')

def signup(request):
    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        password = request.POST['password']

        try:
            # Create the user using your custom User model
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            return redirect('home')  # Redirect after successful signup

        except IntegrityError:
            # Handle the case where the username already exists
            return render(request, 'signup.html', {
                'error_message': 'Username already exists. Please choose a different username.',
                'first_name': first_name,
                'last_name': last_name,
            })

    return render(request, 'signup.html')


from .recipescraper import recipeScrape
from django.shortcuts import render
from .recipescraper import recipeScrape
from .substitutions import identify_allergens

def recipe(request):
    # Get the recipe URL from the query parameters
    recipe_url = request.GET.get('url')

    if not recipe_url:
        return redirect('home')

    # Get the user's allergies (assuming they are stored as a comma-separated string)
    user = request.user
    user_allergies = user.allergies.split(",") if user.allergies else []

    try:
        # Use the recipeScrape function to fetch recipe details
        recipe_data = recipeScrape(recipe_url)

        # Process the ingredients and instructions to apply substitutions
        ingredients = recipe_data["ingredients"].split("\n")
        instructions = recipe_data["instructions"].split("\n")
        updated_ingredients, updated_instructions = identify_allergens(ingredients, instructions, user_allergies)

        # Update the recipe data with substituted ingredients and instructions
        recipe_data["ingredients"] = "\n".join(updated_ingredients)
        recipe_data["instructions"] = "\n".join(updated_instructions)
    except Exception as e:
        return redirect('home')

    # Pass the recipe details to the template
    return render(request, 'recipe.html', recipe_data)