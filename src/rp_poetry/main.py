from contextlib import asynccontextmanager
from typing import Optional, Union, Annotated
from sqlmodel import SQLModel, create_engine, Session, select, Field
from fastapi import FastAPI, Depends, HTTPException
from rp_poetry import settings
from fastapi.middleware.cors import CORSMiddleware

class Todo(SQLModel, table = True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str =  Field(index=True)
    status: bool = Field(default=False)

connectionstring = str(settings.DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg"
)

engine = create_engine(connectionstring, connect_args={"sslmode": "require"}, pool_recycle=600)

def create_db_and_table():
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def life_span(app:FastAPI):
    print("Create database...")
    create_db_and_table()
    yield 

app = FastAPI(
    lifespan=life_span,
    title="Todo API",
    version="0.0.1",
    servers=[
        {
            "url": "http://0.0.0.0:8000", # ADD NGROK URL Here Before Creating GPT Action
            "description": "Development Server"
        }
        ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PUT"],
    allow_headers=["*"],
)

def get_session():
    with Session(engine) as session:
        yield session

@app.get("/")
async def root():
    return {"greeting": "Welcome To Todo App!"}

@app.post("/todos", response_model=Todo)
def create_todo(todo: Todo, session: Annotated[Session, Depends(get_session)]):
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo

@app.get("/todos", response_model=list[Todo])
def get_todo(session: Annotated[Session, Depends(get_session)]):
    todos = session.exec(select(Todo)).all()
    return todos

@app.delete("/todos/{todo_id}", response_model=Todo)
def delete_todo(todo_id: int, session: Annotated[Session, Depends(get_session)]):
    todo = session.exec(select(Todo).where(Todo.id == todo_id)).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    session.delete(todo)
    session.commit()
    return todo

# Create a function that take the id of the todo and update the status of the given id of the todo and return a updated list of the todo

class updateTodo():
    status: bool

@app.put("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, todo: Todo, session: Annotated[Session, Depends(get_session)]):
    todo_query = session.exec(select(Todo).where(Todo.id == todo_id)).first()
    if not todo_query:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo_query.status = todo.status
    session.commit()
    session.refresh(todo_query)
    return todo_query
