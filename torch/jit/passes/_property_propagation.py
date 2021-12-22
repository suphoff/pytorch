"""
Tools to help with tensor property propagation.

This is not intended to be imported directly; please use the exposed
functionalities in `torch.jit`.
"""

from typing import Any, List

import torch
from torch import TensorType
from torch._C import Graph


def apply_input_props_using_example(graph: Graph, example_input: List[Any]):
    """
    Applies properties for each tensor in the graph inputs
    using the example supplied.

    Currently only supports dtype and shape, but will support
    device in the near future.
    """
    graph_inputs = list(graph.inputs())
    if len(graph_inputs) == 0:
        return

    # Strip self args off for methods
    in_0 = graph_inputs[0]
    if isinstance(in_0.type(), torch._C.ClassType) and in_0.debugName() == "self":
        graph_inputs = graph_inputs[1:]

    if not len(graph_inputs) == len(example_input):
        raise RuntimeError(
            "Number of inputs in graph does not match number of inputs in the example")

    for i, (graph_i, example_i) in enumerate(zip(graph_inputs, example_input)):
        if example_i is None:
            continue  # Skip the type check

        if isinstance(example_i, torch.Tensor) != isinstance(graph_i.type(), TensorType):
            raise RuntimeError(f"Input {i} does not match type of example", graph_i, example_i)

        if isinstance(example_i, torch.Tensor):
            dtype = example_i.dtype
            shape = example_i.shape
            graph_i.setType(graph_i.type().with_dtype(dtype).with_sizes(shape))  # type: ignore[arg-type]
