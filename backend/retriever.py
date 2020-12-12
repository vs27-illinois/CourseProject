import json
import lucene
import pandas as pd

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


app = Flask(__name__)
vm = lucene.initVM()
mmDir = MMapDirectory(Paths.get('index'))
searcher = IndexSearcher(DirectoryReader.open(mmDir))
print(f"Total number of documents: {searcher.getIndexReader().numDocs()}")


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
        'avg_rating': float(doc.get('avg_rating')),
        'total_reviews': int(doc.get('total_reviews')),
        'ingredients': convert_to_list(doc, "ingredients", highlight, query)
    }


def parse_results(results, highlight=False, query=None):
    recipes = []
    for hit in results.scoreDocs:
        doc = searcher.doc(hit.doc)
        recipes.append(convert_to_json(doc, highlight, query))
    return recipes


def get_all_recipes():
    hits = searcher.search(MatchAllDocsQuery(), 50000)
    recipes = parse_results(hits)
    return pd.DataFrame(recipes)


df = get_all_recipes()


@app.route('/')
def home():
    return render_template('index.html')


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

    recipes = parse_results(hits, highlight=True, query=query)

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
        recipe['time_taken'] = convert_to_list(doc, "time_taken")
        recipe['directions'] = convert_to_list(doc, "directions")
        recipe['nutrition'] = json.loads(doc.get('nutrition'))

    return jsonify(recipe)


@app.route('/recipe/recommend/<recipe_id>')
def get_recommended_recipes(recipe_id):
    # recommended recipes should be based on similar ingredients and calories
    recipes = [{"count": df.shape[0]}] # get_recommended_recipes(df, recipe_id)

    return jsonify(recipes)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
