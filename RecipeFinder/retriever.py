import lucene

from datetime import datetime
from java.nio.file import Paths
from org.apache.lucene.store import MMapDirectory
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.search import IndexSearcher, Sort, SortField
from org.apache.lucene.analysis.en import EnglishAnalyzer
from org.apache.lucene.queryparser.classic import QueryParser

def convert_to_list(doc, key):
    return [value for value in doc.getValues(key)]

def convert_to_json(doc):
    return {
        'id': doc.get('id'),
        'name': doc.get('name'),
        'image': doc.get('image'),
        'avg_rating': doc.get('avg_rating'),
        'total_reviews': doc.get('total_reviews'),
        'ingredients': convert_to_list(doc, "ingredients"),
        'directions': convert_to_list(doc, "directions"),
        'nutrition': doc.get('nutrition')
    }

if __name__ == "__main__":
    print(f"Current Time = {datetime.now()}")

    lucene.initVM()
    mmDir = MMapDirectory(Paths.get('index'))
    searcher = IndexSearcher(DirectoryReader.open(mmDir))

    queryParser = QueryParser("ingredients", EnglishAnalyzer())
    queryParser.setSplitOnWhitespace(True)
    queryParser.setAutoGeneratePhraseQueries(True)

    searchTerm = input("Enter query: ")
    query = queryParser.parse(searchTerm)

    sortFields = [SortField("total_reviews", SortField.Type.FLOAT, True),
                  SortField("avg_rating", SortField.Type.FLOAT, True),
                  SortField.FIELD_SCORE]
    sort = Sort(sortFields)

    print(f"Current Time = {datetime.now()}")
    hits = searcher.search(query, 20, sort)
    print(f"Current Time = {datetime.now()}")

    print(f"Found {hits.totalHits.value} document(s) that matched query '{query}':")
    for hit in hits.scoreDocs:
        doc = searcher.doc(hit.doc)
        print(convert_to_json(doc))

    print(f"Current Time = {datetime.now()}")
