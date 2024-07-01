import time
from typing import Annotated

from litestar import Litestar, get, post
from litestar.contrib.prometheus import PrometheusConfig, PrometheusController
from litestar.enums import MediaType, RequestEncodingType
from litestar.params import Body
from litestar.status_codes import HTTP_200_OK
from msgspec.json import encode

from src.api_models import FormData
from src.metrics import GET_REQUEST_LATENCY, PREDICT_REQUEST_LATENCY
from src.resnet_model import ResnetClassifier
from src.utils import load_img_from_bytes

prometheus_config = PrometheusConfig()


# TODO: add index.html and favicon.ico
@get("/")
async def index() -> str:
    """Returns the index page."""
    start_time = time.time()
    end_time = time.time()
    GET_REQUEST_LATENCY.observe(end_time - start_time)
    return "Welcome to the Elastic ML Inference API."


@post("/predict", media_type=MediaType.JSON, status_code=HTTP_200_OK)
async def predict(
    data: Annotated[FormData, Body(media_type=RequestEncodingType.MULTI_PART)], results: int = 5
) -> bytes:
    """Returns the predictions for the input image."""
    start_time = time.time()
    content = await data.image.read()
    input_img = load_img_from_bytes(content)
    # TODO: create a return type model for the predict function
    result = {
        "predictions": ResnetClassifier.get_or_create_instance().predict(img=input_img, n_results=results),
        "latency": 0,
    }
    end_time = time.time()
    result["latency"] = end_time - start_time
    PREDICT_REQUEST_LATENCY.observe(result["latency"])
    return encode(result)


app = Litestar(route_handlers=[PrometheusController, index, predict], middleware=[prometheus_config.middleware])
