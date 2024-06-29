from typing import ClassVar, Optional

from PIL import Image
from torchvision.models import resnet18, ResNet18_Weights


class ResnetClassifier:
    _instance: ClassVar[Optional["ResnetClassifier"]] = None

    def __init__(self) -> None:
        self._weights = ResNet18_Weights.IMAGENET1K_V1
        self._model = resnet18(weights=self._weights)

        # Set model to evaluation mode
        self._model.eval()

    @classmethod
    def get_or_create_instance(cls) -> "ResnetClassifier":
        if cls._instance is None:
            cls._instance = ResnetClassifier()
        return cls._instance

    def _preprocess(self, img: Image) -> Image:
        return self._weights.transforms()(img).unsqueeze(0)

    def predict(self, img: Image, n_results: int = 5) -> dict[str, float]:
        """Returns predictions for the input image.

        Args:
            img (Image): PIL Image
            n_results (int): Number of predictions to return

        Returns:
            dict[str, float]: Dictionary containing the class names and the confidence scores
        
        """

        preprocessed_img = self._preprocess(img)
        predictions = self._model(preprocessed_img).squeeze(0)

        return {
            self._weights.meta["categories"][idx]: predictions[idx].item()
            for idx in list(predictions.sort()[1])[-1:-n_results - 1:-1]
        }
