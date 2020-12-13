import re
import json
import lucene
import pandas as pd

from scipy.spatial.distance import euclidean
from sklearn.preprocessing import normalize
from flask import Flask, render_template
from flask import jsonify
from java.nio.file import Paths
from java.io import StringReader
from org.apache.lucene.store import MMapDirectory
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.search import IndexSearcher, Sort, SortField, MatchAllDocsQuery
from org.apache.lucene.analysis.en import EnglishAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search.highlight import Highlighter, QueryScorer, SimpleHTMLFormatter


# Initializes the Flask App and Lucene Searcher
app = Flask(__name__)
vm = lucene.initVM()
mmDir = MMapDirectory(Paths.get('index'))
searcher = IndexSearcher(DirectoryReader.open(mmDir))


def convert_to_list(doc, key, highlight=False, query=None):
    if key == "ingredients" and highlight is True and query is not None:
        analyzer = EnglishAnalyzer()
        hl = Highlighter(SimpleHTMLFormatter('<strong>', '</strong>'), QueryScorer(query))

        values = []
        for text in doc.getValues(key):
            ts = analyzer.tokenStream("ingredients", StringReader(text))
            value = hl.getBestFragment(ts, text)
            if value is None:
                values.append(text)
            else:
                values.insert(0, value)

        return values
    else:
        return [value for value in doc.getValues(key)]


def convert_to_json(doc, highlight=False, query=None):
    return {
        'id': int(doc.get('id')),
        'name': doc.get('name'),
        'image': doc.get('image'),
        'calories': float(doc.get('calories')),
        'protein': float(doc.get('protein')),
        'carbohydrates': float(doc.get('carbohydrates')),
        'fat': float(doc.get('fat')),
        'avg_rating': float(doc.get('avg_rating')),
        'total_reviews': int(doc.get('total_reviews')),
        'ingredients': convert_to_list(doc, "ingredients", highlight, query)
    }


def get_all_recipes():
    hits = searcher.search(MatchAllDocsQuery(), 50000)

    recipe_list = {}
    recipes = []
    for hit in hits.scoreDocs:
        doc = searcher.doc(hit.doc)

        recipe = convert_to_json(doc)
        recipe_id = recipe['id']
        recipe_list[recipe_id] = recipe

        new_recipe = {
            'id': recipe['id'],
            'calories': recipe['calories'],
            'protein': recipe['protein'],
            'carbohydrates': recipe['carbohydrates'],
            'fat': recipe['fat']
        }
        recipes.append(new_recipe)

    df_pre = pd.DataFrame(recipes)
    df = df_pre.drop('id', axis=1)
    df.index = df_pre['id']
    df_norm = pd.DataFrame(normalize(df, axis=0))
    df_norm.columns = df.columns
    df_norm.index = df.index

    return recipe_list, df


# Initializes the Recipe List and Normalized Dataframe for the Recommendation Service
all_recipes, data_frame = get_all_recipes()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/recipe/search/<ingredient>')
def get_recipes(ingredient):
    vm.attachCurrentThread()
    recipes = []
    ingredient = re.sub('[^a-zA-Z0-9 ]', '', ingredient).strip()
    if len(ingredient) > 0:
        query_parser = QueryParser("ingredients", EnglishAnalyzer())
        query_parser.setSplitOnWhitespace(True)
        query_parser.setAutoGeneratePhraseQueries(True)

        sort = Sort([SortField.FIELD_SCORE,
                     SortField("total_reviews", SortField.Type.FLOAT, True),
                     SortField("avg_rating", SortField.Type.FLOAT, True)])

        query = query_parser.parse(ingredient)
        hits = searcher.search(query, 20, sort)

        for hit in hits.scoreDocs:
            doc = searcher.doc(hit.doc)
            recipe = convert_to_json(doc, highlight=True, query=query)
            recipes.append(recipe)

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
        recipe = convert_to_json(doc)
        recipe['time_taken'] = convert_to_list(doc, "time_taken")
        recipe['directions'] = convert_to_list(doc, "directions")
        recipe['nutrition'] = json.loads(doc.get('nutrition'))

    return jsonify(recipe)


@app.route('/recipe/recommend/<recipe_id>')
def get_recommended_recipes(recipe_id):
    base_id = int(recipe_id)
    indices = pd.DataFrame(data_frame.index)
    indices = indices[indices.id != base_id]
    indices['distance'] = indices['id'].apply(lambda x: euclidean(data_frame.loc[base_id], data_frame.loc[x]))
    result = indices.sort_values(['distance']).head(4).sort_values(by=['distance', 'id'])

    recipes = []
    for index in result.id:
        recipes.append(all_recipes[index])

    return jsonify(recipes)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
