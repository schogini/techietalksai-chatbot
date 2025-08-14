from fastapi import FastAPI, Request, Depends, HTTPException
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
os.makedirs("data/csvs", exist_ok=True)


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

    # knowledge=PDFUrlKnowledgeBase(
    #     urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
    #     vector_db=LanceDb(
    #         uri="tmp/lancedb",
    #         table_name="recipe_knowledge",
    #         search_type=SearchType.hybrid,
    #         embedder=OpenAIEmbedder(id="text-embedding-3-small"),
    #     ),
    # ),

    # AGENT SETTINGS
    # """Run `pip install duckduckgo-search pgvector google.genai` to install dependencies."""

    # from agno.agent import Agent
    # from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
    # from agno.memory.v2.db.postgres import PostgresMemoryDb
    # from agno.memory.v2.memory import Memory
    # from agno.models.google import Gemini
    # from agno.storage.postgres import PostgresStorage
    # from agno.tools.duckduckgo import DuckDuckGoTools
    # from agno.vectordb.pgvector import PgVector

    # db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

    # knowledge_base = PDFUrlKnowledgeBase(
    #     urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
    #     vector_db=PgVector(table_name="recipes", db_url=db_url),
    # )
    # knowledge_base.load(recreate=True)  # Comment out after first run

    # agent = Agent(
    #     model=Gemini(id="gemini-2.0-flash-001"),
    #     tools=[DuckDuckGoTools()],
    #     knowledge=knowledge_base,
    #     storage=PostgresStorage(table_name="agent_sessions", db_url=db_url),
    #     # Store the memories and summary in a database
    #     memory=Memory(
    #         db=PostgresMemoryDb(table_name="agent_memory", db_url=db_url),
    #     ),
    #     enable_user_memories=True,
    #     enable_session_summaries=True,
    #     show_tool_calls=True,
    #     # This setting adds a tool to search the knowledge base for information
    #     search_knowledge=True,
    #     # This setting adds a tool to get chat history
    #     read_chat_history=True,
    #     # Add the previous chat history to the messages sent to the Model.
    #     add_history_to_messages=True,
    #     # This setting adds 6 previous messages from chat history to the messages sent to the LLM
    #     num_history_responses=6,
    #     markdown=True,
    #     debug_mode=True,
    # )

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
    # knowledge=PDFUrlKnowledgeBase(
    #     urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
    #     vector_db=LanceDb(
    #         uri="tmp/lancedb",
    #         table_name="recipe_knowledge",
    #         search_type=SearchType.hybrid,
    #         embedder=OpenAIEmbedder(id="text-embedding-3-small"),
    #     ),
    # ),
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

# Define allowed origins for CORS
origins = [
    "http://localhost",
    "http://localhost:8080",
    # Add any other origins you want to allow
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# In-memory session storage (for demonstration purposes)
# In a production environment, use a more persistent storage like Redis
sessions = {}

# Dependency to get the session ID from the token
async def get_session_id(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        scheme, token = auth_header.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        return token
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")

@app.post("/chat")
async def chat(request: Request, session_id: str = Depends(get_session_id)):
    body = await request.json()
    message = body.get("message")

    if not message:
        raise HTTPException(status_code=400, detail="Message not provided")

    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Invalid session")

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


            yt = """
                <table>
                <tr>
                <td>
                <a href="https://www.youtube.com/watch?v=vIcyjWAPCkw" target="_blank">
                <img src="https://img.youtube.com/vi/vIcyjWAPCkw/hqdefault.jpg" alt="🚀 Build Your SaaS Agent with Memory in Minutes! 🔥" width="120" />
                </a>
                </td>
                <td style="vertical-align: middle; padding-left: 10px;">
                <strong>🚀 Build Your SaaS Agent with Memory in Minutes! 🔥</strong>
                </td>
                </tr>
                <tr>
                <td>
                <a href="https://cdn.pixabay.com/photo/2024/05/15/01/13/cat-8762411_1280.png" target="_blank">
                <img src="https://cdn.pixabay.com/photo/2024/05/15/01/13/cat-8762411_1280.png" alt="Cat" width="120" />
                </a>
                </td>
                <td style="vertical-align: middle; padding-left: 10px;">
                <strong>🚀 Cat 🔥</strong>
                </td>
                </tr>
                </table>
"""
            img = """
                <table>
                <tr>
                <td>
                <a href="https://cdn.pixabay.com/photo/2024/05/15/01/13/cat-8762411_1280.png" target="_blank">
                <img src="https://cdn.pixabay.com/photo/2024/05/15/01/13/cat-8762411_1280.png" alt="Cat" width="120" />
                </a>
                </td>
                <td style="vertical-align: middle; padding-left: 10px;">
                <strong>🚀 Cat 🔥</strong>
                </td>
                </tr>
                </table>
"""

            # yield f"data: {chunk.content} {yt}"
            yield f"data: {chunk.content}"

            """
            streaming_response_content = ""
            chunk: Iterator[RunResponse] = agent.run(message, stream=True) #, debug_mode=True)
            for response in chunk:
                # pprint_run_response(chunk, markdown=True, show_time=True)
                # pprint(response)
                # pprint(response.content)
                # pprint(response.extra_data)
                # # pprint(dir(response))
                # pprint(vars(response))
                # yield f"data: {chunk.content}\n\n"

                # if response.content:  # skip empty
                if response.content and not response.content.startswith("search_knowledge_base"):
                    new_text = response.content.replace("\\", "")
                    # new_text = markdown.markdown(response.content)
                    pprint(new_text)
                    streaming_response_content += new_text
            yield f"data: {streaming_response_content}"  # send piece to client

           """

        except Exception as e:
            print(f"Error during generation: {e}")
            yield f"data: An error occurred.\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

# curl -X POST localhost:8001/session -d '{}'
# {"session_id":"73caf3e3-6e98-4e19-aa76-274f37b8db4a"}
@app.post("/session")
async def create_session():
    session_id = str(uuid.uuid4())
    sessions[session_id] = [] # We'll store message history here
    return {"session_id": session_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

