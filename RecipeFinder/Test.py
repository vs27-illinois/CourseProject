from flask import Flask
from flask import jsonify

app = Flask(__name__)  # Flask constructor


# A decorator used to tell the application
# which URL is associated function
@app.route('/recipe/summary/<ingredient>')
def getRecipeSummary(ingredient):

    recipes = []

    recipe1 = {}
    recipe1['id'] = 1
    recipe1['name'] = 'Onion chutney'

    recipe2 = {}
    recipe2['id'] = 2
    recipe2['name'] = 'Onion gravy'

    recipes.append(recipe1)
    recipes.append(recipe2)

    return jsonify(recipes)


@app.route('/recipe/details/<recipeId>')
def getRecipeDetails(recipeId):

    recipe1 = {}
    recipe1['id'] = recipeId
    recipe1['name'] = 'Onion chutney'

    return jsonify(recipe1)

if __name__ == '__main__':
    app.run()