from typing import Optional, List
from fastapi import FastAPI, Form, Request, File, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
from pydantic import BaseModel


app = FastAPI()

# 임의의 db
fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


# 1. 기본 구조
@app.get("/")
def read_root():
    return {"Hello": "World"}

# 2. GET path parameter 방식
@app.get("/users/{user_id}")
def get_user(user_id):
    return {"user_id": user_id}

# 3. GET query parameter 방식
# http://127.0.0.1:8000/items/?skip=1 방식으로 인자 변경
@app.get("/items/")
def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit] # fake db의 0-9까지의 인덱스를 반환

# 4. GET optional parameter 방식 (path + query)
# http://127.0.0.1:8000/items/402?q=sehwachoi 방식으로 q 전달
@app.get("/items/{item_id}")
def read_item(item_id: str, q: Optional[str] = None): # q는 optional한 값
    if q: # q가 있으면
        return {"item_id": item_id, "q": q} # 같이 반환
    return {"item_id": item_id}

# 5. POST request body 구조
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

@app.post("/create_items/")
def create_item(item: Item):
    return item

# 6. POST response body 구조
# ex> 회원가입 정보(아이디, 비번, 폰 번호 등) 입력 후, 안녕하세요 아이디 님!만 출력하는거?/
class ItemIn(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

class ItemOut(BaseModel):
    name: str
    price: float
    tax: Optional[float] = None

@app.post("/creating_items/", response_model=ItemOut)
def create_item(item: ItemIn):
    return item

# 7. POST Form 구조
templates = Jinja2Templates(directory='./templates')

# 로그인 창 띄우기 query parameter
@app.get("/login/")
def get_login_form(request: Request):
    return templates.TemplateResponse('login_form.html', context={'request': request})

# 로그인 창 form에 입력된 정보 가지고 처리 
# post는 request body에 정보가 있으니까, form을 채워서 처리하는 애로 생각
@app.post("/login/")
def login(username: str = Form(...), password: str = Form(...)):
    return {"username": username}


# 8. file 업로드 구조
# 단일 파일 업로드
@app.post("/files/")
def create_files(files: List[bytes] = File(...)):
    return {"file_sizes": [len(file) for file in files]}

# 여러 파일 업로드 
@app.post("/uploadfiles/")
def create_upload_files(files: List[UploadFile] = File(...)):
    return {"filenames": [file.filename for file in files]}


@app.get("/upload/")
def main():
    content = """
<body>
<form action="/files/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)


# 9. validation






