import torch
from transformers import pipeline
import time
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp


def remove_background(file_path: str, device: torch.device):
    time.sleep(5)
    pipe = pipeline(
        "image-segmentation",
        model="briaai/RMBG-1.4",
        trust_remote_code=True,
        device=device,
    )
    pillow_mask = pipe(file_path, return_mask=True)  # outputs a pillow mask
    pillow_image = pipe(file_path)  # applies mask on input and returns a pillow image

    removed_background_image = pillow_image
    return removed_background_image


class RemoveBackground:
    def __init__(self, file_path: str):
        self.file_path = file_path
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
        else:
            self.device = torch.device("cpu")

    def remove_background(self, *args):
        executor = ProcessPoolExecutor(mp_context=mp.get_context("spawn"))
        self.future = executor.submit(remove_background, self.file_path, self.device)

    def save_image(self, save_path: str):
        self.removed_background_image = self.future.result()

        if self.removed_background_image is not None:
            self.removed_background_image.save(save_path)
