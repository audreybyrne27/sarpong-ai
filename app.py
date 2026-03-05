from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from Bio import Entrez
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Question(BaseModel):
    question: str

# PubMed setup
Entrez.email = "example@example.com"

def fetch_publications():

    search = Entrez.esearch(
        db="pubmed",
        term="Sarpong NO[Author]",
        retmax=20
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

papers = fetch_publications()

@app.post("/")
async def ask(q: Question):

    question = q.question.lower()

    context = ""

    for p in papers:

        if any(word in p["abstract"].lower() for word in question.split()):
            context += p["title"] + "\n" + p["abstract"] + "\n\n"

    if context == "":
        return {
            "answer": "No relevant publication found. Try a more specific question about hip or knee arthroplasty."
        }

    answer = f"Based on Dr. Sarpong's publications:\n\n{context[:800]}"

    return {"answer": answer}
