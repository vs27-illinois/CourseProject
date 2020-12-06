import json
import lucene
import pandas

from flask import Flask
from flask import jsonify
from java.nio.file import Paths
from org.apache.lucene.store import MMapDirectory
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.search import IndexSearcher, Sort, SortField, MatchAllDocsQuery
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


def parse_results(results):
    recipes = []
    for hit in results.scoreDocs:
        doc = searcher.doc(hit.doc)
        recipes.append(convert_to_json(doc))
    return recipes


all_hits = searcher.search(MatchAllDocsQuery(), 50000)
all_recipes = parse_results(all_hits)
df = pandas.DataFrame(all_recipes)
del all_hits
del all_recipes


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

    recipes = parse_results(hits)

    return jsonify(recipes)


@app.route('/recipe/details/<recipe_id>')
def get_recipe_details(recipe_id):
    vm.attachCurrentThread()
    query_parser = QueryParser("id", StandardAnalyzer())
    query = query_parser.parse(recipe_id)
    hits = searcher.search(query, 1)

    recipe = {}
    for hit in hits.scoreDocs:
        doc = searcher.doc(hit.doc)
        recipe.update(convert_to_json(doc))
        recipe['directions'] = convert_to_list(doc, "directions")
        recipe['nutrition'] = json.loads(doc.get('nutrition'))

    return jsonify(recipe)


@app.route('/recipe/recommend')
def get_recommended_recipes():
    # id = '<from_post_request>'
    # ingredients = '<from_post_request>'
    # calories = '<from_post_request>'

    # recommended recipes should be based on similar ingredients and calories
    recipes = [{"count": df.shape[0]}] # get_recommended_recipes(df, id, ingredients, calories)

    return jsonify(recipes)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000)
