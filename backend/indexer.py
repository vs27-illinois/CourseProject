import ast
import json
import lucene
import pandas as pd

from java.nio.file import Paths
from org.apache.lucene.store import MMapDirectory
from org.apache.lucene.analysis.en import EnglishAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, IndexOptions, DocValuesType

def get_field_type():
    t = FieldType()
    t.setStored(True)
    return t

def get_numeric_field_type():
    t = get_field_type()
    t.setDocValuesType(DocValuesType.NUMERIC)
    return t

def parse_cooking_directions(row):
    parsed = ast.literal_eval(row["cooking_directions"])
    directions = parsed["directions"].split("\n")
    arr = [d.lower() for d in directions]
    for key in ['ready in', 'cook', 'prep']:
        try:
            idx = arr.index(key.lower()) + 2
            return directions[:idx], directions[idx:]
        except ValueError:
            pass
    return [], directions

def index_data():
    t1 = get_field_type()
    t1.setIndexOptions(IndexOptions.NONE)

    t2 = get_field_type()
    t2.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

    t3 = get_numeric_field_type()
    t3.setIndexOptions(IndexOptions.DOCS)

    t4 = get_numeric_field_type()
    t4.setIndexOptions(IndexOptions.NONE)

    index = 0
    for df in pd.read_csv('dataset/recipe.csv', chunksize=3000, iterator=True):
        df.drop("reviews", axis=1, inplace=True)

        index += 1
        mm_dir = MMapDirectory(Paths.get('index'))
        writer = IndexWriter(mm_dir, IndexWriterConfig(EnglishAnalyzer()))
        print(f"Opening index {index} with {writer.numRamDocs()} docs...")

        for num, row in df.iterrows():
            print(f"Indexing row {num+1}...")

            doc = Document()
            doc.add(Field("id", row["recipe_id"], t3))
            doc.add(Field("name", row["recipe_name"], t1))
            doc.add(Field("image", row["image_url"], t1))
            doc.add(Field("avg_rating", row["aver_rate"], t4))
            doc.add(Field("total_reviews", row["review_nums"], t4))

            ingredients = row["ingredients"].split("^")
            for ingredient in ingredients:
                doc.add(Field("ingredients", ingredient, t2))

            time_taken, directions = parse_cooking_directions(row)
            if len(time_taken) == 0:
                doc.add(Field("time_taken", '', t1))
            else:
                for value in time_taken:
                    doc.add(Field("time_taken", value, t1))
            for direction in directions:
                doc.add(Field("directions", direction, t1))

            nutrition = ast.literal_eval(row["nutritions"])
            doc.add(Field("calories", nutrition["calories"]["amount"], t4))
            doc.add(Field("protein", nutrition["protein"]["amount"], t4))
            doc.add(Field("carbohydrates", nutrition["carbohydrates"]["amount"], t4))
            doc.add(Field("fat", nutrition["fat"]["amount"], t4))

            nutrition = json.dumps(nutrition)
            doc.add(Field("nutrition", nutrition, t1))

            writer.addDocument(doc)

        print(f"Closing index {index} with {writer.numRamDocs()} docs...")
        writer.close()

if __name__ == "__main__":
    lucene.initVM()
    index_data()
