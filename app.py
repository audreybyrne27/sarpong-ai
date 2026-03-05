from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from Bio import Entrez
import openai

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = "YOUR_OPENAI_API_KEY"

class Question(BaseModel):
    question: str

Entrez.email = "research@example.com"

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

        papers.append(f"{title}\n{abstract}")

    return papers

@app.post("/")
async def ask(q: Question):

    papers = search_pubmed(q.question)

    context = "\n\n".join(papers)

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an orthopedic research assistant summarizing PubMed literature."},
            {"role": "user", "content": f"Answer this question using these papers:\n\n{context}\n\nQuestion: {q.question}"}
        ]
    )

    return {"answer": response.choices[0].message.content}
