import torch
import comfy.utils


class ImageBatch:

    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"image1": ("IMAGE",), "image2": ("IMAGE",)}}

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "batch"

    CATEGORY = "image"

    def batch(self, image1, image2):
        if image1.shape[1:] != image2.shape[1:]:
            image2 = comfy.utils.common_upscale(
                image2.movedim(-1, 1),
                image1.shape[2],
                image1.shape[1],
                "bilinear",
                "center",
            ).movedim(1, -1)
        s = torch.cat((image1, image2), dim=0)
        return (s,)
