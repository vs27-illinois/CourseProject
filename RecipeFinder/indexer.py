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
    return parsed["directions"].split("\n")

def parse_total_time(total_time):
    total_time = total_time.replace('d', '* 24 * 60 +') \
        .replace('h', '* 60 +').replace('m', '').strip()
    total_time = total_time[:-1] if total_time.endswith('+') \
        else total_time
    return eval(total_time)

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

            directions = parse_cooking_directions(row)
            total_time = '0'
            for idx, direction in enumerate(directions):
                doc.add(Field("directions", direction, t1))
                if direction.lower() == 'ready in' and idx <= 4:
                    total_time = directions[idx + 1]

            total_time = parse_total_time(total_time)
            doc.add(Field("total_time", total_time, t4))

            nutrition = ast.literal_eval(row["nutritions"])
            doc.add(Field("calories", nutrition["calories"]["amount"], t4))

            nutrition = json.dumps(nutrition)
            doc.add(Field("nutrition", nutrition, t1))

            writer.addDocument(doc)

        print(f"Closing index {index} with {writer.numRamDocs()} docs...")
        writer.close()

if __name__ == "__main__":
    lucene.initVM()
    index_data()
