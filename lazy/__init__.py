import os
import importlib

MODULE_NAME = os.path.basename(os.path.dirname((__file__)))


def init_node(node_module_path, node_class_name):
    print(f"Initializing node: {node_module_path}.{node_class_name}")
    module = importlib.import_module(f"{MODULE_NAME}.{node_module_path}")
    return getattr(module, node_class_name)()


class LazyNode:
    def __init__(self):
        self.NODE_INSTANCE = None

    def __getattr__(self, name):
        class_name = self.__class__.__name__
        if self.NODE_INSTANCE is None:
            self.NODE_INSTANCE = init_node(self.MODULE_PATH, class_name)
        return getattr(self.NODE_INSTANCE, name)


class ImageBatch(LazyNode):
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"image1": ("IMAGE",), "image2": ("IMAGE",)}}

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "batch"
    CATEGORY = "image"

    MODULE_PATH = "nodes.image_batch_node"


NODE_CLASS_MAPPINGS = {
    "ImageBatch": ImageBatch,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageBatch": "Batch Images",
}
