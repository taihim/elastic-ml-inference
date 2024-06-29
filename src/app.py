from typing import Annotated

from litestar import Litestar, post, get
from litestar.datastructures import UploadFile
from litestar.enums import RequestEncodingType, MediaType
from litestar.params import Body
from msgspec.json import encode
from pydantic import BaseConfig, BaseModel

from src.model import ResnetClassifier
from src.utils import load_img


class FormData(BaseModel):
    image: UploadFile
    filename: str

    class Config(BaseConfig):
        arbitrary_types_allowed = True


@get("/")
async def index() -> str:
    return "This is the Elastic ML Inference."


@post("/predict", media_type=MediaType.JSON)
async def predict(data: Annotated[FormData, Body(media_type=RequestEncodingType.MULTI_PART)],
                  results: int = 5) -> bytes:
    content = await data.image.read()
    input_img = load_img(content)
    predictions = encode(ResnetClassifier.get_or_create_instance().predict(img=input_img, n_results=results))
    return predictions


app = Litestar([index, predict])
