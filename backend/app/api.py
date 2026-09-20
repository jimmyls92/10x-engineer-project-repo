"""FastAPI routes for PromptLab"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from app.models import (
    Prompt, PromptCreate, PromptUpdate, PromptPatch,
    Collection, CollectionCreate,
    PromptList, CollectionList, HealthResponse,
    get_current_time
)
from app.storage import storage
from app.utils import sort_prompts_by_date, filter_prompts_by_collection, search_prompts
from app import __version__


app = FastAPI(
    title="PromptLab API",
    description="AI Prompt Engineering Platform",
    version=__version__
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== Health Check ==============

@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(status="healthy", version=__version__)


# ============== Prompt Endpoints ==============

@app.get("/prompts", response_model=PromptList)
def list_prompts(
    collection_id: Optional[str] = None,
    search: Optional[str] = None
):
    prompts = storage.get_all_prompts()
    
    # Filter by collection if specified
    if collection_id:
        prompts = filter_prompts_by_collection(prompts, collection_id)
    
    # Search if query provided
    if search:
        prompts = search_prompts(prompts, search)
    
    # Sort by date (newest first)
    # Note: There might be an issue with the sorting...
    prompts = sort_prompts_by_date(prompts, descending=True)
    
    return PromptList(prompts=prompts, total=len(prompts))


@app.get("/prompts/{prompt_id}", response_model=Prompt)
def get_prompt(prompt_id: str):
    """Return a single prompt by its identifier.

    Args:
        prompt_id: Identifier of the prompt to return.

    Returns:
        The stored prompt.

    Raises:
        HTTPException: With status 404 if no prompt has that identifier.
    """
    prompt = storage.get_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt


@app.post("/prompts", response_model=Prompt, status_code=201)
def create_prompt(prompt_data: PromptCreate):
    # Validate collection exists if provided
    if prompt_data.collection_id:
        collection = storage.get_collection(prompt_data.collection_id)
        if not collection:
            raise HTTPException(status_code=400, detail="Collection not found")
    
    prompt = Prompt(**prompt_data.model_dump())
    return storage.create_prompt(prompt)


@app.put("/prompts/{prompt_id}", response_model=Prompt)
def update_prompt(prompt_id: str, prompt_data: PromptUpdate):
    """Replace a prompt in full and refresh its update timestamp.

    Every client-supplied field is taken from the request body, so a field the
    body leaves out is reset to its default rather than kept -- omitting
    collection_id unfiles the prompt. The creation timestamp is carried over
    from the stored prompt and the update timestamp is set to the current time.

    Args:
        prompt_id: Identifier of the prompt to replace.
        prompt_data: The full replacement body. Title and content are required;
            description and collection_id are optional.

    Returns:
        The stored prompt as it stands after the replacement.

    Raises:
        HTTPException: With status 404 if no prompt has that identifier, or
            status 400 if collection_id is given but names no existing
            collection.
    """
    existing = storage.get_prompt(prompt_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    # Validate collection if provided
    if prompt_data.collection_id:
        collection = storage.get_collection(prompt_data.collection_id)
        if not collection:
            raise HTTPException(status_code=400, detail="Collection not found")
    
    updated_prompt = Prompt(
        id=existing.id,
        title=prompt_data.title,
        content=prompt_data.content,
        description=prompt_data.description,
        collection_id=prompt_data.collection_id,
        created_at=existing.created_at,
        updated_at=get_current_time()
    )
    
    return storage.update_prompt(prompt_id, updated_prompt)


@app.patch("/prompts/{prompt_id}", response_model=Prompt)
def patch_prompt(prompt_id: str, prompt_data: PromptPatch):
    """Update only the fields that the request body carries.

    Presence is judged by whether a key appears in the body, not by whether its
    value is null, so an explicit null collection_id unfiles the prompt while
    leaving the key out keeps the prompt in its collection. The update timestamp
    is refreshed only when the body carries at least one field; an empty body is
    not an edit.

    Args:
        prompt_id: Identifier of the prompt to update.
        prompt_data: The partial update body. Every field is optional, but a
            field that is present must satisfy the same constraints as it does
            on create.

    Returns:
        The stored prompt as it stands after the merge.

    Raises:
        HTTPException: With status 404 if no prompt has that identifier, or
            status 400 if collection_id is present and not null but names no
            existing collection.
    """
    existing = storage.get_prompt(prompt_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Prompt not found")

    changes = prompt_data.model_dump(exclude_unset=True)

    # Validate the collection only when one was actually sent. An explicit null
    # means "unfile", which is not a collection to look up.
    if changes.get("collection_id") is not None:
        collection = storage.get_collection(changes["collection_id"])
        if not collection:
            raise HTTPException(status_code=400, detail="Collection not found")

    updated_prompt = Prompt(
        id=existing.id,
        title=changes.get("title", existing.title),
        content=changes.get("content", existing.content),
        description=changes.get("description", existing.description),
        collection_id=changes.get("collection_id", existing.collection_id),
        created_at=existing.created_at,
        updated_at=get_current_time() if changes else existing.updated_at
    )

    return storage.update_prompt(prompt_id, updated_prompt)


@app.delete("/prompts/{prompt_id}", status_code=204)
def delete_prompt(prompt_id: str):
    if not storage.delete_prompt(prompt_id):
        raise HTTPException(status_code=404, detail="Prompt not found")
    return None


# ============== Collection Endpoints ==============

@app.get("/collections", response_model=CollectionList)
def list_collections():
    collections = storage.get_all_collections()
    return CollectionList(collections=collections, total=len(collections))


@app.get("/collections/{collection_id}", response_model=Collection)
def get_collection(collection_id: str):
    collection = storage.get_collection(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return collection


@app.post("/collections", response_model=Collection, status_code=201)
def create_collection(collection_data: CollectionCreate):
    collection = Collection(**collection_data.model_dump())
    return storage.create_collection(collection)


# Why the prompts are unfiled rather than deleted, and why deleting a non-empty
# collection is allowed at all: the data model treats collection membership as
# incidental, not essential. A prompt's collection_id is optional, it is the one
# client-supplied field carrying no validation constraint, and a collection
# declares no back-reference to its prompts. Cascade-deleting would destroy the
# required fields, title and content, for the sake of an optional one; refusing
# to delete a non-empty collection would enforce an integrity rule the model
# never declares. A full update already unfiles a prompt when the body omits
# collection_id, so "unfiled" is an existing, tested state rather than one
# invented here.
@app.delete("/collections/{collection_id}", status_code=204)
def delete_collection(collection_id: str):
    """Delete a collection and unfile the prompts that belonged to it.

    The prompts themselves are kept; each one that pointed at this collection
    has its collection_id cleared. Their update timestamp is left alone, since
    unfiling is a consequence of deleting the collection rather than an edit the
    client made to the prompt.

    Args:
        collection_id: Identifier of the collection to delete.

    Returns:
        None. The route responds with 204 No Content.

    Raises:
        HTTPException: With status 404 if no collection has that identifier.
    """
    if not storage.delete_collection(collection_id):
        raise HTTPException(status_code=404, detail="Collection not found")

    for prompt in storage.get_prompts_by_collection(collection_id):
        storage.update_prompt(
            prompt.id, prompt.model_copy(update={"collection_id": None})
        )

    return None
