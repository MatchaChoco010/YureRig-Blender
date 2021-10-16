import bpy
from types import ModuleType
import typing
from typing import Iterable, Set, Dict, Any, List, Optional, Union, Type
import inspect
import pkgutil
import importlib
from pathlib import Path

__all__ = (
    "init",
    "register",
    "unregister",
)

MyClass = Union[
    Type[bpy.types.Panel],
    Type[bpy.types.Operator],
    Type[bpy.types.PropertyGroup],
    Type[bpy.types.AddonPreferences],
    Type[bpy.types.Header],
    Type[bpy.types.Menu],
    Type[bpy.types.Node],
    Type[bpy.types.NodeSocket],
    Type[bpy.types.NodeTree],
    Type[bpy.types.UIList],
    Type[bpy.types.RenderEngine],
    Type[bpy.types.Gizmo],
    Type[bpy.types.GizmoGroup],
]
MyClassBase = Union[
    bpy.types.Panel,
    bpy.types.Operator,
    bpy.types.PropertyGroup,
    bpy.types.AddonPreferences,
    bpy.types.Header,
    bpy.types.Menu,
    bpy.types.Node,
    bpy.types.NodeSocket,
    bpy.types.NodeTree,
    bpy.types.UIList,
    bpy.types.RenderEngine,
    bpy.types.Gizmo,
    bpy.types.GizmoGroup,
]

blender_version = bpy.app.version

modules: Optional[List[ModuleType]] = None
ordered_classes: Optional[List[MyClass]] = None


def init() -> None:
    global modules
    global ordered_classes

    modules = get_all_submodules(Path(__file__).parent)
    ordered_classes = get_ordered_classes_to_register(modules)


def register() -> None:
    if ordered_classes is None:
        return

    for cls in ordered_classes:
        bpy.utils.register_class(cls)

    if modules is None:
        return

    for module in modules:
        if module.__name__ == __name__:
            continue
        if hasattr(module, "register"):
            module.register()  # type: ignore


def unregister() -> None:
    if ordered_classes is None:
        return

    for cls in reversed(ordered_classes):
        bpy.utils.unregister_class(cls)

    if modules is None:
        return

    for module in modules:
        if module.__name__ == __name__:
            continue
        if hasattr(module, "unregister"):
            module.unregister()  # type: ignore


# Import modules
#################################################


def get_all_submodules(directory: Path) -> List[ModuleType]:
    return list(iter_submodules(directory, directory.name))


def iter_submodules(path: Path, package_name: str) -> Iterable[ModuleType]:
    for name in sorted(iter_submodule_names(path)):
        yield importlib.import_module("." + name, package_name)


def iter_submodule_names(path: Path, root: str = "") -> Iterable[str]:
    for _, module_name, is_package in pkgutil.iter_modules([str(path)]):
        if is_package:
            sub_path = path / module_name
            sub_root = root + module_name + "."
            yield from iter_submodule_names(sub_path, sub_root)
        else:
            yield root + module_name


# Find classes to register
#################################################


def get_ordered_classes_to_register(modules: List[ModuleType]) -> List[MyClass]:
    return toposort(get_register_deps_dict(modules))


def get_register_deps_dict(
    modules: List[ModuleType],
) -> Dict[MyClass, Set[MyClass]]:
    my_classes = set(iter_my_classes(modules))
    my_classes_by_idname = {
        cls.bl_idname: cls for cls in my_classes if hasattr(cls, "bl_idname")
    }

    deps_dict = {}
    for cls in my_classes:
        deps_dict[cls] = set(
            iter_my_register_deps(cls, my_classes, my_classes_by_idname)
        )
    return deps_dict


def iter_my_register_deps(
    cls: MyClass,
    my_classes: Set[MyClass],
    my_classes_by_idname: Dict[str, MyClass],
) -> Iterable[MyClass]:
    yield from iter_my_deps_from_annotations(cls, my_classes)
    yield from iter_my_deps_from_parent_id(cls, my_classes_by_idname)


def iter_my_deps_from_annotations(
    cls: MyClass, my_classes: Set[MyClass]
) -> Iterable[MyClass]:
    for value in typing.get_type_hints(cls, {}, {}).values():
        dependency = get_dependency_from_annotation(value)
        if dependency is not None:
            if dependency in my_classes:
                yield dependency


def get_dependency_from_annotation(value: Any) -> Optional[Any]:
    if isinstance(value, bpy.props._PropertyDeferred):
        return value.keywords.get("type")
    return None


def iter_my_deps_from_parent_id(cls: Any, my_classes_by_idname: Any) -> Any:
    if bpy.types.Panel in cls.__bases__:
        parent_idname = getattr(cls, "bl_parent_id", None)
        if parent_idname is not None:
            parent_cls = my_classes_by_idname.get(parent_idname)
            if parent_cls is not None:
                yield parent_cls


def iter_my_classes(modules: List[ModuleType]) -> Iterable[MyClass]:
    base_types = get_register_base_types()
    for cls in get_classes_in_modules(modules):
        if any(base in base_types for base in cls.__bases__):
            if not getattr(cls, "is_registered", False):
                yield cls


def get_classes_in_modules(modules: List[ModuleType]) -> Set[Any]:
    classes = set()
    for module in modules:
        for cls in iter_classes_in_module(module):
            classes.add(cls)
    return classes


def iter_classes_in_module(module: ModuleType) -> Iterable[Any]:
    for value in module.__dict__.values():
        if inspect.isclass(value):
            yield value


def get_register_base_types() -> Set[MyClassBase]:
    return set(
        getattr(bpy.types, name)
        for name in [
            "Panel",
            "Operator",
            "PropertyGroup",
            "AddonPreferences",
            "Header",
            "Menu",
            "Node",
            "NodeSocket",
            "NodeTree",
            "UIList",
            "RenderEngine",
            "Gizmo",
            "GizmoGroup",
        ]
    )


# Find order to register to solve dependencies
#################################################


def toposort(deps_dict: Dict[MyClass, Set[MyClass]]) -> List[MyClass]:
    sorted_list: List[MyClass] = []
    sorted_values: Set[MyClass] = set()
    while len(deps_dict) > 0:
        unsorted: List[MyClass] = []
        for value, deps in deps_dict.items():
            if len(deps) == 0:
                sorted_list.append(value)
                sorted_values.add(value)
            else:
                unsorted.append(value)
        deps_dict = {value: deps_dict[value] - sorted_values for value in unsorted}
    return sorted_list
