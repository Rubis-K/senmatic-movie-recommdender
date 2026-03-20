import pandas as pd
import numpy as np
import os

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma


# Load movie dataset once (safe at import)
movies = pd.read_csv("movies_with_emotions.csv")

movies["poster"] = movies["poster"] + "&fife=w800"
movies["poster"] = np.where(
    movies["poster"].isna(),
    "cover_coming_soon.png",
    movies["poster"],
)


# ----------------------------
# Vector DB Initialization
# ----------------------------

def get_vector_db():
    """
    Safely initialize or load the Chroma vector database.
    This prevents crashes during module import.
    """

    embeddings = OpenAIEmbeddings()

    if not os.path.exists("chroma_movies"):

        raw_docs = TextLoader(
            "tagged_description.txt",
            encoding="latin-1"
        ).load()

        text_splitter = CharacterTextSplitter(
            chunk_size=449,
            chunk_overlap=0,
            separator="\n"
        )

        docs = text_splitter.split_documents(raw_docs)

        db = Chroma.from_documents(
            docs,
            embeddings,
            persist_directory="chroma_movies"
        )

        db.persist()
        return db

    else:
        return Chroma(
            persist_directory="chroma_movies",
            embedding_function=embeddings
        )


# ----------------------------
# Semantic Search
# ----------------------------

def retrive_semantic_recommendations(
        query: str,
        category: str = None,
        tone: str = None,
        initial_top_k: int = 50,
        final_top_k: int = 16,
) -> pd.DataFrame:

    db_movies = get_vector_db()

    recs = db_movies.similarity_search_with_score(query, k=initial_top_k)

    movies_list = []

    for doc, score in recs:
        try:
            movie_id = int(doc.page_content.strip('"').split()[0])
            movies_list.append(movie_id)
        except Exception as e:
            print("Error parsing doc:", doc.page_content, e)

    movies_recs = movies[movies["movie_id"].isin(movies_list)].head(final_top_k)

    # Category filtering
    if category and category != "All":
        movies_recs = movies_recs[
            movies_recs["simplified_categories"] == category
        ].head(final_top_k)

    # Tone sorting
    if tone == "Happy":
        movies_recs = movies_recs.sort_values(by="joy", ascending=False)

    elif tone == "Surprising":
        movies_recs = movies_recs.sort_values(by="surprise", ascending=False)

    elif tone == "Angry":
        movies_recs = movies_recs.sort_values(by="anger", ascending=False)

    elif tone == "Suspenseful":
        movies_recs = movies_recs.sort_values(by="fear", ascending=False)

    elif tone == "Sad":
        movies_recs = movies_recs.sort_values(by="sadness", ascending=False)

    return movies_recs.head(final_top_k)


# ----------------------------
# Final Recommendation Output
# ----------------------------

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