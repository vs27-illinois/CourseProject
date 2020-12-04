import ast
import json
import lucene
import pandas as pd

from java.nio.file import Paths
from org.apache.lucene.store import MMapDirectory
from org.apache.lucene.analysis.en import EnglishAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, IndexOptions, DocValuesType

if __name__ == "__main__":
    lucene.initVM()
    mmDir = MMapDirectory(Paths.get('index'))
    writerConfig = IndexWriterConfig(EnglishAnalyzer())
    writer = IndexWriter(mmDir, writerConfig)

    t1 = FieldType()
    t1.setStored(True)
    t1.setIndexOptions(IndexOptions.NONE)

    t2 = FieldType()
    t2.setStored(True)
    t2.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

    t3 = FieldType()
    t3.setStored(True)
    t3.setDocValuesType(DocValuesType.NUMERIC)
    t3.setIndexOptions(IndexOptions.NONE)

    print(f"{writer.numRamDocs()} docs in index")

    for df in pd.read_csv('dataset/recipe.csv', chunksize=5000, iterator=True):
        df.drop("reviews", axis=1, inplace=True)
        for index, row in df.iterrows():
            print(f"Indexing row {index}...")

            doc = Document()

            doc.add(Field("id", row["recipe_id"], t3))
            doc.add(Field("name", row["recipe_name"], t1))
            doc.add(Field("avg_rating", row["aver_rate"], t3))
            doc.add(Field("image", row["image_url"], t1))
            doc.add(Field("total_reviews", row["review_nums"], t3))

            ingredients = row["ingredients"].split("^")
            for ingredient in ingredients:
                doc.add(Field("ingredients", ingredient, t2))

            parsed = ast.literal_eval(row["cooking_directions"])
            directions = parsed["directions"].split("\n")
            total_time = '0'
            for idx, direction in enumerate(directions):
                doc.add(Field("directions", direction, t1))
                if direction.lower() == 'ready in' and idx <= 4:
                    total_time = directions[idx+1]

            total_time = total_time.replace('d', '* 24 * 60 +')\
                .replace('h', '* 60 +').replace('m', '').strip()
            total_time = total_time[:-1] if total_time.endswith('+')\
                else total_time
            total_time = eval(total_time)
            doc.add(Field("total_time", total_time, t3))

            nutrition = ast.literal_eval(row["nutritions"])
            doc.add(Field("calories", nutrition["calories"]["amount"], t3))

            nutrition = json.dumps(nutrition)
            doc.add(Field("nutrition", nutrition, t1))

            writer.addDocument(doc)

    print(f"Closing index of {writer.numRamDocs()} docs...")

    writer.close()
