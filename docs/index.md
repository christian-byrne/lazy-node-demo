# A Better Way to Write Custom Nodes in ComfyUI

**Problem**:

- On startup, all custom nodes and modules are initialized, leading to extremely long startup times and a lot of memory overhead.
- However, only the node's class attributes like `INPUT_TYPES`, `OUTPUT_NAMES`, etc. need to be accessed on startup. (So the user can interact the with node in the UI.)

**Solution**: 

- Create a wrapper around nodes that only initializes the class attributes
- The wrapper lazily initializes the actual node instance and its parent module upon first access of the node instance.

**Benefits**:

- Users can put the node on the graph and interact with it in the UI without any performance overhead.
- The nodes and its module will only be initialized once the graph is executed such that all expensive imports and initialization operations are deferred until necessary.
- If all custom nodes a user is using do this, they can start ComfyUI with 100+ node packs in a few seconds.
- Making custom nodes this way is much nicer to the user.

# Example


**File Structure**:

```
__init__.py
nodes/
    __init__.py
    image_batch_node.py
```

## Non-Lazy


<details>

<summary>&nbsp; Show <code>__init__.py</code> Code</summary>


<br>


```python
# /__init__.py

from .nodes.image_batch_node import ImageBatch

NODE_CLASS_MAPPINGS = {
    "ImageBatch": ImageBatch,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageBatch": "Batch Images",
}
```


<br>


</details>


<details>

<summary>&nbsp; Show <code>nodes/image_batch_node.py</code> Code</summary>


<br>


```python
# /nodes/image_batch_node.py

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
```

<br>


</details>


## Lazy

<details>

<summary>&nbsp; Show <code>__init__.py</code> Code</summary>


<br>



```python
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
    "ImageBatch1": ImageBatch,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageBatch1": "Lazy Batch Images",
}
```

<br>



</details>

<details>

<summary>&nbsp; Show <code>nodes/image_batch_node.py</code> Code</summary>


<br>


```python
# /nodes/image_batch_node.py

import torch
import comfy.utils


class ImageBatch:
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
```


<br>


</details>