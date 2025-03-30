import sys
sys.path.append('C:/Users/mercy/AppData/Local/Programs/Python/Python313/Lib/site-packages')
from urllib.parse import quote
from recipe_scrapers import scrape_me
import requests

def findRecipes(search_term):
    encoded_search_term = search_term.replace(" ", "+")
    print(encoded_search_term)
    search_url = f"https://www.allrecipes.com/search?q={encoded_search_term}"
    featured = scrape_me(search_url).links()
    listFeat = []

    for item in featured:
        if "recipe/" in item["href"]:
            listFeat.append(item["href"])

    return listFeat

def recipeScrape(url):
    scraper = scrape_me(url)
    listIngre = []

    for index in scraper.ingredients():
        if index.count(" ") == 1:
            ingredients = index.split(" ", 1)
        else:
            ingredients = []
            temp = index.split(" ", 2)
            ingredients.append(temp[0] + " " + temp[1])
            ingredients.append(temp[2])

        listIngre.append(ingredients)

    listInstru = scraper.instructions().split("\n")
    strInstru = "\n"

    for i in range(len(listInstru)):
        strInstru = strInstru + "Step " + str((i + 1)) + ") " + listInstru[i] + "\n\n"

    strIngre = "\n"

    for i in range(len(listIngre)):
        strIngre = strIngre + "- " + listIngre[i][0] + " " + listIngre[i][1] + "\n"

    recipeDict = {
        "title": scraper.title(),
        "total time": scraper.total_time(),
        "yields": scraper.yields(),
        "ingredients": strIngre,
        "instructions": strInstru,
        "image": scraper.image(),
        "host": scraper.host(),
        "nutrients": scraper.nutrients()
    }

    return recipeDict

def main(search_term):
    recipe_urls = findRecipes(search_term)
    for url in recipe_urls:
        importantInfo = recipeScrape(url)

        # Print the recipe information to the screen
        print("Title:", importantInfo["title"])
        print("Total Time:", importantInfo["total time"])
        print("Yields:", importantInfo["yields"])
        print("Ingredients:", importantInfo["ingredients"])
        print("Instructions:", importantInfo["instructions"])
        print("Image URL:", importantInfo["image"])
        print("Host:", importantInfo["host"])
        print("Nutrients:", importantInfo["nutrients"])
        print("\n" + "="*40 + "\n")

# Example usage
search_term = "chocolate cake"
main(search_term)