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
import httpx
import json

def strip_html_tags(text):
    return re.sub(r'<[^>]+>', '', text)


# Create CSV knowledge base
csv_kb = CSVKnowledgeBase(
    path=Path("data/csvs"),
    # vector_db=PgVector(
    #     table_name="csv_documents",
    #     db_url=db_url,
    # ),
    vector_db=LanceDb(
        uri="tmp/lancedb",
        table_name="csv",
    )
)

# Create PDF URL knowledge base
pdf_url_kb = PDFUrlKnowledgeBase(
    urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
    # vector_db=PgVector(
    #     table_name="pdf_documents",
    #     db_url=db_url,
    # ),
    vector_db=LanceDb(
        uri="tmp/lancedb",
        table_name="pdf_url",
    )
)

# Create Website knowledge base
website_kb = WebsiteKnowledgeBase(
    urls=["https://blog.schogini.com/html_files/Furniture-Product-Knowledge-Base-RAG-Demo.html"],
    max_links=10,
    # vector_db=PgVector(
    #     table_name="website_documents",
    #     db_url=db_url,
    # ),
    vector_db=LanceDb(
        uri="tmp/lancedb",
        table_name="website_kb",
    )
)

# Create Local PDF knowledge base
local_pdf_kb = PDFKnowledgeBase(
    path="data/pdfs",
    # vector_db=PgVector(
    #     table_name="pdf_documents",
    #     db_url=db_url,
    # ),
    vector_db=LanceDb(
        uri="tmp/lancedb",
        table_name="local_pdf_kb",
    )
)

# Combine knowledge bases
knowledge_base = CombinedKnowledgeBase(
    sources=[
        csv_kb,
        pdf_url_kb,
        website_kb,
        local_pdf_kb,
    ],
    # vector_db=PgVector(
    #     table_name="combined_documents",
    #     db_url=db_url,
    #     embedder=OpenAIEmbedder(id="text-embedding-3-small"),
    # ),
    vector_db=LanceDb(
        uri="tmp/lancedb",
        table_name="recipe_knowledge",
        search_type=SearchType.hybrid,
        embedder=OpenAIEmbedder(id="text-embedding-3-small"),
    ),
)




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
    knowledge=knowledge_base,
    tools=[DuckDuckGoTools()],
    show_tool_calls=False,
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
            chunk: Iterator[RunResponse] = agent.run(message, stream=False)
            bot_response = strip_html_tags(chunk.content)

            # Send chat interaction to the external API
            try:
                interaction = {
                    "user_message": message,
                    "bot_response": bot_response,
                }
                async with httpx.AsyncClient() as client:
                    await client.post("https://api.schogini.com/api", json=interaction)
            except Exception as e:
                print(f"Failed to send chat interaction to API: {e}")

            yield f"data: {bot_response}"

        except Exception as e:
            print(f"Error during generation: {e}")
            yield f"data: An error occurred.\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
