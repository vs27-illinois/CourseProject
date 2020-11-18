import ast
import json
import lucene
import pandas as pd

from java.nio.file import Paths
from org.apache.lucene.store import MMapDirectory
from org.apache.lucene.analysis.en import EnglishAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, IndexOptions

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

    print(f"{writer.numRamDocs()} docs in index")

    for df in pd.read_csv('dataset/recipe.csv', chunksize=5000, iterator=True):
        df.drop("reviews", axis=1, inplace=True)
        for index, row in df.iterrows():
            print(f"Indexing row {index}...")

            doc = Document()

            doc.add(Field("id", row["recipe_id"], t1))
            doc.add(Field("name", row["recipe_name"], t1))
            doc.add(Field("avg_rating", row["aver_rate"], t1))
            doc.add(Field("image", row["image_url"], t1))
            doc.add(Field("total_reviews", row["review_nums"], t1))

            ingredients = row["ingredients"].split("^")
            for ingredient in ingredients:
                doc.add(Field("ingredients", ingredient, t2))

            parsed = ast.literal_eval(row["cooking_directions"])
            directions = parsed["directions"].split("\n")
            for direction in directions:
                doc.add(Field("directions", direction, t1))

            nutrition = ast.literal_eval(row["nutritions"])
            doc.add(Field("calories", nutrition["calories"]["amount"], t1))

            nutrition = json.dumps(nutrition)
            doc.add(Field("nutrition", nutrition, t1))

            writer.addDocument(doc)

    print(f"Closing index of {writer.numRamDocs()} docs...")

    writer.close()
