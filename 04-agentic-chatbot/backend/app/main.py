from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from google import genai
from google.genai import types
import os
import uuid
import asyncio


# AGNO OPEN AI
import markdown
from rich.pretty import pprint
from dotenv import load_dotenv
load_dotenv()
from agno.models.openai import OpenAIChat
model=OpenAIChat(id="gpt-4o-mini")
import logging
logging.getLogger("httpx").setLevel(logging.WARNING)

from textwrap import dedent
from typing import Iterator
from agno.agent import Agent, RunResponse
from agno.embedder.openai import OpenAIEmbedder
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.utils.pprint import pprint_run_response

from agno.knowledge.combined import CombinedKnowledgeBase
from agno.knowledge.csv import CSVKnowledgeBase
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.knowledge.website import WebsiteKnowledgeBase

from pathlib import Path
import os

import re

def strip_html_tags(text):
    return re.sub(r'<[^>]+>', '', text)

instructions=dedent("""\
    You are a passionate and knowledgeable Thai cuisine expert! 🧑‍🍳
    Think of yourself as a combination of a warm, encouraging cooking instructor,
    a Thai food historian, and a cultural ambassador.

    Follow these steps when answering questions:
    1. If the user asks a about Thai cuisine, ALWAYS search your knowledge base for authentic Thai recipes and cooking information
    2. If the information in the knowledge base is incomplete OR if the user asks a question better suited for the web, search the web to fill in gaps
    3. If you find the information in the knowledge base, no need to search the web
    4. Always prioritize knowledge base information over web results for authenticity
    5. If needed, supplement with web searches for:
        - Modern adaptations or ingredient substitutions
        - Cultural context and historical background
        - Additional cooking tips and troubleshooting

    Communication style:
    1. Start each response with a relevant cooking emoji
    2. Structure your responses clearly:
        - Brief introduction or context
        - Main content (recipe, explanation, or history)
        - Pro tips or cultural insights
        - Encouraging conclusion
    3. For recipes, include:
        - List of ingredients with possible substitutions
        - Clear, numbered cooking steps
        - Tips for success and common pitfalls
    4. Use friendly, encouraging language

    Special features:
    - Explain unfamiliar Thai ingredients and suggest alternatives
    - Share relevant cultural context and traditions
    - Provide tips for adapting recipes to different dietary needs
    - Include serving suggestions and accompaniments

    End each response with an uplifting sign-off like:
    - 'Happy cooking! ขอให้อร่อย (Enjoy your meal)!'
    - 'May your Thai cooking adventure bring joy!'
    - 'Enjoy your homemade Thai feast!'

    Remember:
    - Always verify recipe authenticity with the knowledge base
    - Clearly indicate when information comes from web sources
    - Be encouraging and supportive of home cooks at all skill levels\
""")
agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini"),
    instructions=dedent("""\
        You are a helpful assistant.
        Communication style:
        1. Use simple HTML inline formatting.
    """),
    # markdown=True,
    add_history_to_messages=True,
    # Number of historical responses to add to the messages.
    num_history_responses=3,
)

# Comment out after the knowledge base is loaded
if agent.knowledge is not None:
    agent.knowledge.load()


app = FastAPI()

# Add permissive CORS middleware (no restrictions)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    message = body.get("message")

    if not message:
        raise HTTPException(status_code=400, detail="Message not provided")

    async def generate():
        try:

            chunk: Iterator[RunResponse] = agent.run(message, stream=False) #, debug_mode=True)
            pprint(chunk.content)
            # yield f"data: {chunk.content}"
            pprint(
                [
                    m.model_dump(include={"role", "content"})
                    for m in agent.get_messages_for_session()
                ]
            )

            # yield f"data: {chunk.content} {yt}"
            yield f"data: {strip_html_tags(chunk.content)}"

        except Exception as e:
            print(f"Error during generation: {e}")
            yield f"data: An error occurred.\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


