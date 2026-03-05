from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow requests from external websites (like GitHub Pages)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Question(BaseModel):
    question: str

@app.post("/")
async def ask(q: Question):

    question = q.question.lower()

    if "anterior hip" in question:
        answer = "The direct anterior approach may allow faster recovery and lower dislocation risk compared to traditional hip approaches."
    elif "revision" in question:
        answer = "Revision hip arthroplasty is performed when an existing hip implant fails or complications occur."
    else:
        answer = "Dr. Sarpong’s research focuses on hip and knee arthroplasty outcomes, implant design, and surgical technique."

    return {"answer": answer}
