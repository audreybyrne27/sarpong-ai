from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

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