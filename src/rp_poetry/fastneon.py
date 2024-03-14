# fastapi_neon/main.py
from contextlib import asynccontextmanager
from typing import Union, Optional, Annotated
from rp_poetry import settings
from sqlmodel import Field, Session, SQLModel, create_engine, select
from fastapi import FastAPI, Depends


class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str = Field(index=True)


# only needed for psycopg 3 - replace postgresql
# with postgresql+psycopg in settings.DATABASE_URL
connection_string = str(settings.DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg"
)


# recycle connections after 5 minutes
# to correspond with the compute scale down
engine = create_engine(
    connection_string, connect_args={"sslmode": "require"}, pool_recycle=300
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# The first part of the function, before the yield, will
# be executed before the application starts.
# https://fastapi.tiangolo.com/advanced/events/#lifespan-function
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables..")
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, title="Hello World API with DB", 
    version="0.0.1",
    servers=[
        {
            "url": "http://0.0.0.0:8000", # ADD NGROK URL Here Before Creating GPT Action
            "description": "Development Server"
        }
        ])

def get_session():
    with Session(engine) as session:
        yield session


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/todos/", response_model=Todo)
def create_todo(todo: Todo, session: Annotated[Session, Depends(get_session)]):
        session.add(todo)
        session.commit()
        session.refresh(todo)
        return todo


@app.get("/todos/", response_model=list[Todo])
def read_todos(session: Annotated[Session, Depends(get_session)]):
        todos = session.exec(select(Todo)).all()
        return todos

# @fastapp.get("/users/me")
# def read_user():
#     return {"Message": "Hello Abbasi"}

# # @fastapp.get("/users/{user_id}")
# # async def read_user_by_id(user_id: str):
# #     return {"user_id: Hello": user_id}

# # class ModelName(str, Enum):
# #     alexnet = "alexnet"
# #     resnet = "resnet"
# #     lenet = "lenet"



# # @fastapp.get("/models/{model_name}")
# # async def get_model(model_name: ModelName):
# #     if model_name.value == "alexnet":
# #         return {"model_name": model_name, "message": "Deep Learning FTW!"}

# #     if model_name.value == "lenet":
# #         return {"model_name": model_name, "message": "LeCNN all the images"}

# #     return {"model_name": model_name, "message": "Have some residuals"}

# # @fastapp.get("/files/{file_path:path}")
# # async def read_file(file_path: str):
# #     return {"file_path": file_path.split('/')}

# # fake_items_db = [
# #     {"item_name": "Foo"}, 
# #     {"item_name": "Bar"},
# #     {"item_name": "Baz"},
# #     {"item_name": "Bar"},
# #     {"item_name": "Baz"},
# #     {"item_name": "Bar"},
# #     {"item_name": "Baz"}
# #     ]

# # # Query Parameters
# # @fastapp.get("/items/")
# # async def read_item(skip: int = 0, limit: int = 10):
# #     print(fake_items_db[skip : skip + limit])
# #     return fake_items_db[skip : skip + limit]

# # # Optional Query Parameters
# # # @fastapp.get("/items/{item_id}")
# # # async def read_items(item_id: str, q: str | None = None):
# # #     if q:
# # #         return {"item_id": item_id, "q": q}
# # #     return {"item_id": item_id}

# # # Query Parameters with type conventions
# # # @fastapp.get("/items/{item_id}")
# # # async def read_item_set(item_id: str, q: str | None = None, short: bool = False):
# # #     item = {"item_id": item_id}
# # #     if q:
# # #         item.update({"q": q})
# # #     if not short:
# # #         item.update(
# # #             {"description": "This is an amazing item that has a long description"}
# # #         )
# # #     return item

# # # Multiple Path & Query Parameters
# # @fastapp.get("/users/{user_id}/items/{item_id}")
# # async def read_user_item(
# #     user_id: int, item_id: str, q: str | None = None, short: bool = False
# # ):
# #     item = {"item_id": item_id, "owner_id": user_id}
# #     if q:
# #         item.update({"q": q})
# #     if not short:
# #         item.update(
# #             {"description": "This is an amazing item that has a long description"}
# #         )
# #     return item

# # # Required Parameters
# # @fastapp.get("/items/{item_id}")
# # async def read_user_item_required(item_id: str, needy: str):
# #     item = {"item_id": item_id, "needy": needy}
# #     return item

# # @fastapp.get("/product/{item_id}")
# # async def read_users_item(
# #     item_id: str, needy: str, skip: int = 0, limit: int | None = None
# # ):
# #     item = {"item_id": item_id, "needy": needy, "skip": skip, "limit": limit}
# #     return item

# # from pydantic import BaseModel

# # class Item(BaseModel):
# #     name: str
# #     description: str | None = None
# #     price: int | float
# #     tax: int | float | None = None


# # @fastapp.post("/items/")
# # async def create_item(item: Item):
# #     item_dict = item.dict()
# #     if item.tax:
# #         price_with_tax = item.price + item.tax
# #         item_dict.update({"price_with_tax": price_with_tax})
# #     return item_dict

# # @fastapp.put("/items/{item_id}")
# # async def update_item(item_id: int, item: Item, q: str | None = None):
# #     result = {"item_id": item_id, **item.dict()}
# #     if q:
# #         result.update({"q": q})
# #     return result

# # Path Parameters:

# # Create an endpoint /users/{user_id} that retrieves user details based on the provided user_id.
# # Implement an endpoint /items/{item_id}/details that returns detailed information about a specific item identified by item_id.

# @fastapp.get("/user/{user_id}")
# async def get_user_details(user_id: str):
#     return {"user_id": user_id}

# # Question 3
# # items_db: dict[int, dict[str, str]] = {
# #     1: {"name" : "Muhammad Ahsaan", "description": "Hello World"},
# #     2: {"name" : "Muhammad Ahmed", "description": "Hello World"},
# #     3: {"name" : "Muhammad Abbas", "description": "Hello World"}
# # }

# # @fastapp.get("/items/{item_id}/details")
# # async def get_item_details(item_id: int):
# #     if item_id not in items_db:
# #         raise HTTPException(status_code=404, detail="Item not found")
# #     return items_db[item_id]


# # Dynamic Item Retrieval:
# # Extend the /items/{item_id}/details endpoint to handle dynamic item details retrieval. The item details should include attributes such as name, description, price, and quantity.
# from typing import Union
# items_details: dict[int, dict[str, Union[str | int]]] = {
#     1: {"name" : "Mobile", "description": "Hello World", "price": 100, "quantity": 10},
#     2: {"name" : "Tablet", "description": "Hello World", "price": 200, "quantity": 10},
#     3: {"name" : "Laptop", "description": "Hello World", "price": 300, "quantity": 10},
# }

# # @ fastapp.get("/items/{item_id}/details")
# # async def get_item(item_id:int):
# #     return items_details[item_id]


# # Question 4
# # Validation and Error Handling:
# # Enhance the /items/{item_id}/details endpoint to include validation checks for the item_id path parameter. Return an appropriate error message if the item_id provided in the request is not valid or does not exist in the database.

# # @fastapp.get("/items/{item_id}/details")
# # async def item_id_validation(item_id: int):
# #     if item_id not in items_details:
# #         raise HTTPException(status_code=404, detail="Item not found")
# #     return items_details[item_id]


# # Question 5
# # Authorization and Authentication:
# # Implement authentication and authorization mechanisms for the /items/{item_id}/details endpoint. Ensure that only authorized users with specific roles can access detailed information about items.
# users: dict[int, dict[str, str]] = {
#     1: {"username": "Muhammad Ahsaan", "role": "admin"},
#     2: {"username": "Muhammad Ahmed", "role": "user"},
#     3: {"username": "Muhammad Abbas", "role": "user"},
#     4: {"username": "Muhammad Ali", "role": "user"},
#     5: {"username": "Muhammad Usman", "role": "user"},
#     6: {"username": "Muhammad Emad", "role": "user"},
# }

# @fastapp.get("/items/{item_id}/details")
# async def get_item_details(item_id: int, user_id: int):
#     if item_id not in items_details:
#         raise HTTPException(status_code=404, detail="Item not found")
#     if user_id not in users:
#         raise HTTPException(status_code=401, detail="Unauthorized")
#     if users[user_id]["role"] == "admin":
#         return items_details[item_id]
#     else:
#         raise HTTPException(status_code=403, detail="Forbidden")

# # Query Parameters:
# # Question 6
# # Develop an endpoint /search that accepts query parameters category, price_min, and price_max to filter items based on these criteria.
# data: dict[int, dict[str, Union[str | int]]] = {
#     1: {"name" : "Mobile", "category": "Electronics", "price": 10000},
#     2: {"name" : "Tablet", "category": "Electronics", "price": 20000},
#     3: {"name" : "Laptop", "category": "Electronics", "price": 30000},
#     4: {"name" : "Laptop", "category": "Electronics", "price": 30000},
#     5: {"name" : "Laptop", "category": "Electronics", "price": 30000},
# }
# @fastapp.get("/items/search")
# async def search_items(category: str, price_min: int, price_max: int):
#     return [item for item in data.values() if item["category"] == category and int(item["price"]) >= price_min and int(item["price"]) <= price_max]

# # Create an endpoint /users that retrieves a list of users filtered by role query parameter.
# @fastapp.get("/users/{user_id}")
# async def get_users(user_id:int, role:str):
#     if user_id not in users:
#         raise HTTPException(status_code=401, detail="Unauthorized")
#     if users[user_id]["role"] == "admin":
#         return users
#     else:
#         raise HTTPException(status_code=403, detail="Forbidden")

# # Request Body (POST, PUT, DELETE):
# # Question 7
# # Implement a POST endpoint /users to create a new user with the provided user details in the request body.
# from pydantic import BaseModel
# class User(BaseModel):
#     name: str
#     role: str
    
# @fastapp.post("/users")
# async def create_user(users: User):
#     return users.dict()

# # Develop a PUT endpoint /items/{item_id} to update the details of a specific item identified by item_id based on the data provided in the request body.
# class Item(BaseModel):
#     name: str
#     description: str | None = None
#     price: int | float
#     tax: int | float | None = None
# @fastapp.put("/items/{item_id}")
# async def update_item(item_id: int, item: Item):
#     return {"item_id": item_id, **item.dict()}

# # Create a DELETE endpoint /users/{user_id} to delete a user with the specified user_id.
# @fastapp.delete("/users/{user_id}")
# async def delete_user(user_id: int, user: User):
#     if user_id not in users:
#         raise HTTPException(status_code=404, detail="User not found")
#     if users[user_id]:
#         del users[user_id]
#         return {"message": "User deleted successfully"}
#     else:
#         raise HTTPException(status_code=403, detail="Forbidden")

# from random import choice
# from typing import Union
# quotes: list[dict[str, Union[str, int]]] = [
#     {
#         "id": 1,
#         "quote": "The art of losing isn't hard to master; so many things seem filled with the intent to be lost that their loss is no disaster.",
#         "author": "Agha Shahid Ali"
#     },
#     {
#         "id": 2,
#         "quote": "I searched for God and found only myself. I searched for myself and found only God.",
#         "author": "Rumi"
#     },
#     {
#         "id": 3,
#         "quote": "where the mind is without fear and the head is held high; where knowledge is free.",
#         "author": "Rabindranath Tagore"
#     },
#     {
#         "id": 4,
#         "quote": "I searched everywhere for love, and only found myself; I sought everywhere for peace, and only found turmoil.",
#         "author": "Rumi"
#     },
#     {
#         "id": 5,
#         "quote": "I took the path less traveled by, and that has made all the difference",
#         "author": "Robert Frost"
#     },
#     {
#         "id": 6,
#         "quote": "Love is the bridge between you and everything.",
#         "author": "Rumi"
#     },
# ]

# async def get_random_quote(author:str)->list[dict]:
#     get_quotes_by_author = [quote for quote in quotes if quote["author"] == author]
#     if not get_quotes_by_author:
#         raise HTTPException(status_code=404, detail="Quote not found")
#     return get_quotes_by_author

# @fastapp.get("/quotes")
# async def get_quotes(author: str | None = None):
#     if author:
#         get_author_quotes = await get_random_quote(author)
#         return get_author_quotes
#     else:
#         random_quotes = choice(quotes)
#         return random_quotes

from enum import Enum 

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}