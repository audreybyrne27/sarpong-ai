from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from Bio import Entrez
from openai import OpenAI

import os


# ------------------------------------
# Initialize API clients
# ------------------------------------

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

Entrez.email = "research@example.com"


# ------------------------------------
# FastAPI setup
# ------------------------------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------
# Request schema
# ------------------------------------

class Question(BaseModel):
    question: str


# ------------------------------------
# PubMed search function
# ------------------------------------

def search_pubmed(query):

    search = Entrez.esearch(
        db="pubmed",
        term=query,
        retmax=5
    )

    record = Entrez.read(search)
    ids = record["IdList"]

    papers = []

    for id in ids:

        fetch = Entrez.efetch(
            db="pubmed",
            id=id,
            retmode="xml"
        )

        data = Entrez.read(fetch)

        article = data["PubmedArticle"][0]["MedlineCitation"]["Article"]

        title = article["ArticleTitle"]

        abstract = ""

        if "Abstract" in article:
            abstract = " ".join(article["Abstract"]["AbstractText"])

        papers.append({
            "title": title,
            "abstract": abstract
        })

    return papers


# ------------------------------------
# Chat endpoint
# ------------------------------------

@app.post("/")
async def ask(q: Question):

    papers = search_pubmed(q.question)

    if len(papers) == 0:
        return {"answer": "No relevant PubMed papers found."}

    context = ""

    for p in papers:
        context += f"{p['title']}\n{p['abstract']}\n\n"

    response = client.chat.completions.create(

        model="gpt-4o-mini",

        messages=[
            {
                "role": "system",
                "content": "You are an orthopedic research assistant summarizing biomedical literature from PubMed."
            },
            {
                "role": "user",
                "content": f"Using the following PubMed abstracts, answer the question and summarize the literature. Cite key findings.\n\n{context}\n\nQuestion: {q.question}"
            }
        ],

        temperature=0.3
    )

    answer = response.choices[0].message.content

    return {"answer": answer}
