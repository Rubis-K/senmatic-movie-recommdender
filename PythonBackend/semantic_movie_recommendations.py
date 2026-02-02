import pandas as pd
import numpy as np
from dotenv import load_dotenv
import re
import os

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

movies = pd.read_csv('movies_with_emotions.csv')
movies["poster"] = movies["poster"] + "&fife=w800"
movies["poster"] = np.where(
    movies["poster"].isna(),
    "cover_coming_soon.png",
    movies["poster"],
)

raw_docs = TextLoader("tagged_description.txt", encoding="latin-1").load()
text_splitter = CharacterTextSplitter(chunk_size=449, chunk_overlap=0, separator="\n")
docs = text_splitter.split_documents(raw_docs)
#Load or build vector DB
if not os.path.exists("chroma_movies"):
    raw_docs = TextLoader("tagged_description.txt", encoding="latin-1").load()
    text_splitter = CharacterTextSplitter(chunk_size=449, chunk_overlap=0, separator="\n")
    docs = text_splitter.split_documents(raw_docs)
    db_movies = Chroma.from_documents(docs, OpenAIEmbeddings(), persist_directory="chroma_movies")
    db_movies.persist()
else:
    db_movies = Chroma(persist_directory="chroma_movies", embedding_function=OpenAIEmbeddings())





def retrive_semantic_recommendations(
        query: str,
        category: str = None,
        tone: str = None,
        initial_top_k: int = 50,
        final_top_k: int = 16,
) -> pd.DataFrame:

   # recs = db_movies.similarity_search_with_score(query, k=initial_top_k)
   # movies_list = [int(doc.page_content.strip('"').split()[0]) for doc, score in recs]
    #movies_recs = movies[movies["movie_id"].isin(movies_list)].head(final_top_k)

    recs = db_movies.similarity_search_with_score(query, k=initial_top_k)
    movies_list = []
        
    for doc, score in recs:
        try:
            movie_id = int(doc.page_content.strip('"').split()[0])
            movies_list.append(movie_id)
        except Exception as e:
            print("Error parsing doc:", doc.page_content, e)
    print("Movie IDs:", movies_list)
    movies_recs = movies[movies["movie_id"].isin(movies_list)].head(final_top_k)

    if category != "All":
        movies_recs = movies_recs[movies_recs["simplified_categories"] == category].head(final_top_k)
    else:
        movies_recs = movies_recs.head(final_top_k)

    if tone == "Happy":
        movies_recs.sort_values(by="joy", ascending=False, inplace=True)
    if tone == "Surprising":
        movies_recs.sort_values(by="surprise", ascending=False, inplace=True)
    if tone == "Angry":
        movies_recs.sort_values(by="anger", ascending=False, inplace=True)
    if tone == "Suspenseful":
        movies_recs.sort_values(by="fear", ascending=False, inplace=True)
    if tone == "Sad":
        movies_recs.sort_values(by="sadness", ascending=False, inplace=True)

    return movies_recs


def recommend_movies(
        query: str,
        category: str,
        tone: str
):
        recommendations = retrive_semantic_recommendations(query, category, tone)
        results = []

        for _, row in recommendations.iterrows():
            description = row["description"]
            truncated_desc_split = description.split()
            truncated_description = " ".join(truncated_desc_split[:28]) + "..."

            writer = str(row["writer"]) if not pd.isna(row["writer"]) else "Unknown"
            writer_split = writer.split(";")
            if len(writer_split) == 2:
                writer_str = f"{writer_split[0]}...{writer_split[1]}"
            elif len(writer_split) > 2:
                writer_str = f"{', '.join(writer_split[:-1])}, and {writer_split[-1]}"
            else:
                writer_str = writer

            caption = f"{row['title']} by {writer_str}: {truncated_description}"
            results.append((row["poster"], caption))

        return results
