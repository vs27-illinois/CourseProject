import json
import lucene

from flask import Flask
from flask import jsonify
from java.nio.file import Paths
from org.apache.lucene.store import MMapDirectory
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.search import IndexSearcher, Sort, SortField
from org.apache.lucene.analysis.en import EnglishAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.queryparser.classic import QueryParser

app = Flask(__name__)
vm = lucene.initVM()
mmDir = MMapDirectory(Paths.get('index'))
searcher = IndexSearcher(DirectoryReader.open(mmDir))
print(f"Total number of documents: {searcher.getIndexReader().numDocs()}")


def convert_to_list(doc, key):
    return [value for value in doc.getValues(key)]


def convert_to_json(doc):
    return {
        'id': doc.get('id'),
        'name': doc.get('name'),
        'image': doc.get('image'),
        'calories': doc.get('calories'),
        'total_time': doc.get('total_time'),
        'avg_rating': doc.get('avg_rating'),
        'total_reviews': doc.get('total_reviews'),
        'ingredients': convert_to_list(doc, "ingredients")
    }


@app.route('/recipe/search/<ingredient>')
def get_recipes(ingredient):
    vm.attachCurrentThread()
    query_parser = QueryParser("ingredients", EnglishAnalyzer())
    query_parser.setSplitOnWhitespace(True)
    query_parser.setAutoGeneratePhraseQueries(True)

    sort = Sort([SortField("total_reviews", SortField.Type.FLOAT, True),
                 SortField("avg_rating", SortField.Type.FLOAT, True),
                 SortField.FIELD_SCORE])

    query = query_parser.parse(ingredient)
    hits = searcher.search(query, 20, sort)

    recipes = []
    for hit in hits.scoreDocs:
        doc = searcher.doc(hit.doc)
        recipes.append(convert_to_json(doc))

    return jsonify(recipes)


@app.route('/recipe/details/<recipe_id>')
def get_recipe_details(recipe_id):
    vm.attachCurrentThread()
    query_parser = QueryParser("id", StandardAnalyzer())
    query = query_parser.parse(recipe_id)
    hits = searcher.search(query, 5)

    recipe = {}
    for hit in hits.scoreDocs:
        doc = searcher.doc(hit.doc)
        recipe['id'] = doc.get('id')
        recipe['name'] = doc.get('name')
        recipe['image'] = doc.get('image')
        recipe['calories'] = doc.get('calories')
        recipe['total_time'] = doc.get('total_time')
        recipe['avg_rating'] = doc.get('avg_rating')
        recipe['total_reviews'] = doc.get('total_reviews')
        recipe['ingredients'] = convert_to_list(doc, "ingredients")
        recipe['directions'] = convert_to_list(doc, "directions")
        recipe['nutrition'] = json.loads(doc.get('nutrition'))

    return jsonify(recipe)


@app.route('/recipe/recommend/<recipe_id>')
def get_recommended_recipes(recipe_id):
    vm.attachCurrentThread()
    query_parser = QueryParser("id", StandardAnalyzer())
    query = query_parser.parse(recipe_id)
    hits = searcher.search(query, 5)

    recipes = []
    for hit in hits.scoreDocs:
        doc = searcher.doc(hit.doc)
        calories = doc.get('calories')
        total_time = doc.get('total_time')
        ingredients = convert_to_list(doc, "ingredients")
        # recipes = get_recommended_recipes(ingredients, calories, total_time)

    recipe = {"id": recipe_id, "name": "Onion Chutney"}
    recipes.append(recipe)
    return jsonify(recipes)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000)
