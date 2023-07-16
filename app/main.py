import json

from fastapi import Cookie, FastAPI, Form, Request, Response, templating
from fastapi.responses import RedirectResponse
from jose import jwt


from .flowers_repository import Flower, FlowersRepository
from .purchases_repository import Purchase, PurchasesRepository
from .users_repository import User, UsersRepository


app = FastAPI()
templates = templating.Jinja2Templates("templates")


flowers_repository = FlowersRepository()
purchases_repository = PurchasesRepository()
users_repository = UsersRepository()


@app.get("/")
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get('/signup')
def get_sign_up(request: Request):
    return templates.TemplateResponse("app/sign_up.html", {"request": request})


@app.post("/signup")
def post_sign_up(
        request: Request,
        email: str = Form(),
        full_name: str = Form(),
        password: str = Form(),
):
    user = User(email=email, full_name=full_name, password=password)
    users_repository.save(user)
    return RedirectResponse("/login", status_code=303)


def create_jwt(user_id: int) -> str:
    body = {"user_id": user_id}
    token = jwt.encode(body, "qwert", "HS256")
    return token


def decode_jwt(token: str) -> int:
    data = jwt.decode(token, "qwert", "HS256")
    return data["user_id"]




@app.get('/login')
def get_sign_up(request: Request):
    return templates.TemplateResponse("app/sign_in.html", {"request": request})


@app.post("/login")
def post_sign_up(
        request: Request,
        response: Response,
        email: str = Form(),
        password: str = Form(),
):
    user = users_repository.get_by_email(email)
    if user.password == password:
        response = RedirectResponse("/profile", status_code=303)
        token = create_jwt(int(user.id))
        response.set_cookie("token", token)
        return response
    return Response("Permission denied")


@app.get("/profile")
def get_profile(request: Request, token: str = Cookie()):
    user_id = decode_jwt(token)
    user = users_repository.get_by_id(int(user_id))
    return templates.TemplateResponse(
        "app/profile.html",
        {
          "request": request,
          "user": user,

        },
    )


@app.get("/flowers")
def get_flowers(request: Request):
    flowers = flowers_repository.get_all()
    return templates.TemplateResponse(
        "flowers/flowers.html",
        {
            "request": request,
            "flowers": flowers,

        }
    )


@app.post("/flowers")
def post_flowers(
        request: Request,
        name: str = Form(),
        count: int = Form(),
        cost: int = Form(),
):

    flower = Flower(name=name, count=count, cost=cost)
    flowers_repository.save(flower)
    return RedirectResponse("/flowers", status_code=303)


@app.post("/cart/items")
def add_carts(
    flower_id: int = Form(),
    cart: str = Cookie(default="[]"),
):
    cart_json = json.loads(cart)
    response = RedirectResponse("/flowers", status_code=303)
    if flower_id != None:
        cart_json.append(flower_id)
        new_cart = json.dumps(cart_json)
        response.set_cookie(key='cart', value=new_cart)
    return response


@app.get("/cart/items")
def get_carts(request: Request):
    cart = request.cookies.get("cart")
    flowers = flowers_repository.get_list(cart)
    return templates.TemplateResponse(
        "app/cart.html",
        {
            "request": request,
            "flowers": flowers
        }
    )
