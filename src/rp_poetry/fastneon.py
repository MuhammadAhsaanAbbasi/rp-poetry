# fastapi_neon/main.py
from contextlib import asynccontextmanager
from typing import Union, Optional, Annotated
from rp_poetry import settings
from sqlmodel import Field, Session, SQLModel, create_engine, select
from fastapi import FastAPI, Depends, Body


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

from pydantic import BaseModel


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


# @app.put("/items/{item_id}")
# async def update_item(
#     *,
#     item_id: int,
#     item: Annotated[
#         Item,
#         Body(
#             openapi_examples={
#                 "normal": {
#                     "summary": "A normal example",
#                     "description": "A **normal** item works correctly.",
#                     "value": {
#                         "name": "Foo",
#                         "description": "A very nice Item",
#                         "price": 35.4,
#                         "tax": 3.2,
#                     },
#                 },
#                 "converted": {
#                     "summary": "An example with converted data",
#                     "description": "FastAPI can convert price `strings` to actual `numbers` automatically",
#                     "value": {
#                         "name": "Bar",
#                         "price": "35.4",
#                     },
#                 },
#                 "invalid": {
#                     "summary": "Invalid data is rejected with an error",
#                     "value": {
#                         "name": "Baz",
#                         "price": "thirty five point four",
#                     },
#                 },
#             },
#         ),
#     ],
# ):
#     results = {"item_id": item_id, "item": item}
#     return results


from datetime import datetime, time, timedelta
from uuid import UUID
from fastapi import Body, Cookie, Header

# @app.put("/items/{item_id}")
# async def read_items(
#     item_id: UUID,
#     start_datetime: Annotated[datetime | None, Body()] = None,
#     end_datetime: Annotated[datetime | None, Body()] = None,
#     repeat_at: Annotated[time | None, Body()] = None,
#     process_after: Annotated[timedelta | None, Body()] = None,
# ):
#     start_process = start_datetime + process_after
#     duration = end_datetime - start_process
#     return {
#         "item_id": item_id,
#         "start_datetime": start_datetime,
#         "end_datetime": end_datetime,
#         "repeat_at": repeat_at,
#         "process_after": process_after,
#         "start_process": start_process,
#         "duration": duration,
#     }

class User(BaseModel):
    username: str
    age: int | None = None
    email: str | None = None
    password: str | None = None

@app.put("/items/{item_id}")
async def read_items(
    item_id: UUID,
    item: Annotated[Item, Body()],
    user: Annotated[User, Body()],
):
    results = {"item_id": item_id, "item": item, "user": user}
    return results

# @app.get("/items")
# async def get_cookies(
#     cookie_id: Annotated[str | None, Cookie(description="the id of the cookie")] = None):
#     return {"cookie_id": cookie_id}

# @app.get("/items")
# async def get_headers(user_agent: Annotated[str | None, Header()] = None):
#     return {"User-Agent": user_agent}

# @app.get("/items/")
# async def get_headers(
#     strange_header: Annotated[str | None, Header(convert_underscores=False)] = None,
# ):
#     return {"strange_header": strange_header}

# @app.get("/items/")
# async def get_headers(x_token: Annotated[list[str] | None, Header()] = None):
#     return {"X-Token values": x_token}

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: list[str] = []


@app.post("/items/")
async def create_item(item: Item) -> Item:
    return item


@app.get("/items/")
async def list_read_items() -> list[Item]:
    return [
        Item(name="Portal Gun", price=42.0),
        Item(name="Plumbus", price=32.0),
    ]

from typing import Any
from pydantic import BaseModel, EmailStr

# class UserIn(BaseModel):
#     username: str
#     password: str
#     email: EmailStr
#     full_name: str | None = None


# class UserOut(BaseModel):
#     username: str
#     email: EmailStr
#     full_name: str | None = None


# @app.post("/user/", response_model=UserOut)
# async def create_user(user: UserIn) -> Any:
#     return user

class BaseUser(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


class UserIn(BaseUser):
    password: str


@app.post("/user/")
async def create_user(user: UserIn) -> BaseUser:
    return user


from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse, RedirectResponse

app = FastAPI()

# @app.get("/portal")
# async def get_portal(teleport: bool = False) -> Response:
#     if teleport:
#         return RedirectResponse(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
#     return JSONResponse(content={"message": "Here's your interdimensional portal."})

# @app.get("/portal")
# async def get_portal(teleport: bool = False) -> Response | dict:
#     if teleport:
#         return RedirectResponse(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
#     return {"message": "Here's your interdimensional portal."}

@app.get("/portal", response_model=None)
async def get_portal(teleport: bool = False) -> Response | dict:
    if teleport:
        return RedirectResponse(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    return {"message": "Here's your interdimensional portal."}

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# class Item(BaseModel):
#     name: str
#     description: str | None = None
#     price: float
#     tax: float = 10.5
#     tags: list[str] = []


# items = {
#     "foo": {"name": "Foo", "price": 50.2},
#     "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
#     "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
# }


# @app.get("/items/{item_id}", response_model=Item, response_model_exclude_unset=True)
# async def an_read_item(item_id: str):
#     return items[item_id]


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float = 10.5


items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The Bar fighters", "price": 62, "tax": 20.2},
    "baz": {
        "name": "Baz",
        "description": "There goes my baz",
        "price": 50.2,
        "tax": 10.5,
    },
}


@app.get(
    "/items/{item_id}/name",
    response_model=Item,
    response_model_include={"name", "description"},
)
async def read_item_name(item_id: str):
    return items[item_id]


@app.get("/items/{item_id}/public", response_model=Item, response_model_exclude={"tax"})
async def read_item_public_data(item_id: str):
    return items[item_id]


from fastapi import File, UploadFile


# @app.post("/files/")
# async def create_file(file: Annotated[bytes, File()]):
#     return {"file_size": len(file)}


# @app.post("/uploadfile/")
# async def create_upload_file(file: UploadFile):
#     content = await file.read(size=11)
#     return {"filename": content}

# @app.post("/files/")
# async def create_file(file: Annotated[bytes | None, File()] = None):
#     if not file:
#         return {"message": "No file sent"}
#     else:
#         return {"file_size": len(file)}


# @app.post("/uploadfile/")
# async def create_upload_file(file: UploadFile | None = None):
#     if not file:
#         return {"message": "No upload file sent"}
#     else:
#         return {"filename": file.filename}

# @app.post("/files/")
# async def create_file(file: Annotated[bytes, File(description="A file read as bytes")]):
#     return {"file_size": len(file)}


# @app.post("/uploadfile/")
# async def create_upload_file(
#     file: Annotated[UploadFile, File(description="A file read as UploadFile")],
# ):
#     return {"filename": file.filename}

# @app.post("/files/")
# async def create_files(files: Annotated[list[bytes], File()]):
#     return {"file_sizes": [len(file) for file in files]}


# @app.post("/uploadfiles/")
# async def create_upload_files(files: list[UploadFile]):
#     return {"filenames": [file.filename for file in files]}

# from fastapi.responses import HTMLResponse
# @app.get("/")
# async def main():
#     content = """
# <body>
# <form action="/files/" enctype="multipart/form-data" method="post">
# <input name="files" type="file" multiple>
# <input type="submit">
# </form>
# <form action="/uploadfiles/" enctype="multipart/form-data" method="post">
# <input name="files" type="file" multiple>
# <input type="submit">
# </form>
# </body>
#     """
#     return HTMLResponse(content=content)
from fastapi import FastAPI, File, Form, UploadFile

@app.post("/files/")
async def create_file(
    file: Annotated[bytes, File()],
    fileb: Annotated[UploadFile, File()],
    token: Annotated[str, Form()],
):
    return {
        "file_size": len(file),
        "token": token,
        "fileb_content_type": fileb.content_type,
    }

# from fastapi import FastAPI, Request
# from fastapi.responses import JSONResponse


# class UnicornException(Exception):
#     def __init__(self, name: str):
#         self.name = name


# @app.exception_handler(UnicornException)
# async def unicorn_exception_handler(request: Request, exc: UnicornException):
#     return JSONResponse(
#         status_code=418,
#         content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
#     )


# @app.get("/unicorns/{name}")
# async def read_unicorn(name: str):
#     if name == "yolo":
#         raise UnicornException(name=name)
#     return {"unicorn_name": name}

# from fastapi import FastAPI, HTTPException
# from fastapi.exceptions import RequestValidationError
# from fastapi.responses import PlainTextResponse
# from starlette.exceptions import HTTPException as StarletteHTTPException


# @app.exception_handler(StarletteHTTPException)
# async def http_exception_handler(request, exc):
#     return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request, exc):
#     return PlainTextResponse(str(exc), status_code=400)


# @app.get("/items/{item_id}")
# async def read_item(item_id: int):
#     if item_id == 3:
#         raise HTTPException(status_code=418, detail="Nope! I don't like 3.")
#     return {"item_id": item_id}

from enum import Enum

from fastapi import FastAPI

app = FastAPI()


class Tags(Enum):
    items = "items"
    users = "users"


@app.get("/items/", tags=[Tags.items, "other tag"])
async def get_items():
    return ["Portal gun", "Plumbus"]


@app.get("/users/", tags=[Tags.users])
async def read_users():
    return ["Rick", "Morty"]


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()


# @app.post("/items/", response_model=Item, summary="Create an item")
# async def create_item(item: Item):
#     """
#     Create an item with all the information:

#     - **name**: each item must have a name
#     - **description**: a long description
#     - **price**: required
#     - **tax**: if the item doesn't have tax, you can omit this
#     - **tags**: a set of unique tag strings for this item
#     """
#     return item

@app.get("/elements/", tags=["items"], deprecated=True)
async def read_elements():
    return [{"item_id": "Foo"}]

@app.post(
    "/items/",
    response_model=Item,
    summary="Create an item",
    response_description="The created item",
)
async def create_item(item: Item):
    """
    Create an item with all the information:

    - **name**: each item must have a name
    - **description**: a long description
    - **price**: required
    - **tax**: if the item doesn't have tax, you can omit this
    - **tags**: a set of unique tag strings for this item
    """
    return item