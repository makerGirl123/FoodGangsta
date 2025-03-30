import json

def load_allergen_substitutes():
    return {
        "milk": "almond milk",
        "eggs": "flaxseed meal mixed with water",
        "peanuts": "sunflower seed butter",
        "tree nuts": "pumpkin seeds",
        "wheat": "gluten-free flour",
        "soy": "coconut aminos",
        "fish": "tofu",
        "shellfish": "mushrooms"
    }

def identify_allergens(ingredients, instructions, user_allergies):
    substitutes = load_allergen_substitutes()
    print("Substitutes loaded:", substitutes)  # Debugging line to check if substitutes are loaded correctly

    # Process ingredients
    updated_ingredients = []
    for ingredient in ingredients:
        # Normalize the ingredient for comparison
        ingredient_lower = ingredient.lower()

        # Check if the ingredient matches any user allergy
        matched = False
        for allergy in user_allergies:
            allergy_lower = allergy.split()[0].lower()

            # Check if the allergy is a word in the ingredient
            if allergy_lower in ingredient_lower.split():
                print(f"Allergy found: {allergy} in ingredient: {ingredient}")  # Debugging line
                substitute = substitutes.get(allergy_lower, "No substitute available")
                updated_ingredients.append(f"{ingredient} (Substitute: {substitute})")
                matched = True
                break

        if not matched:
            # If no allergy matches, keep the ingredient as is
            updated_ingredients.append(ingredient)

    # Process instructions
    updated_instructions = []
    for instruction in instructions:
        updated_instruction = instruction
        for allergy in user_allergies:
            allergy_lower = allergy.split()[0].lower()

            # Check if the allergy is mentioned in the instruction
            if allergy_lower in instruction.lower():
                substitute = substitutes.get(allergy_lower, "No substitute available")
                updated_instruction = updated_instruction.replace(
                    allergy_lower, f"{allergy_lower} (Substitute: {substitute})"
                )
        updated_instructions.append(updated_instruction)

    return updated_ingredients, updated_instructions