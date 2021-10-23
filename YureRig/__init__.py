import bpy

__all__ = ["auto_load", "panel_ui", "preferences", "property_group", "yurerig"]
from . import auto_load, panel_ui, preferences, property_group, yurerig

bl_info = {
    "name": "YureRig",
    "author": "Orito Itsuki",
    "description": 'Create rig for "Yuremono"',
    "blender": (2, 93, 0),
    "version": (0, 0, 1),
    "location": "VIEW_3D > <<Addon Tab>>",
    "warning": "",
    "doc_url": "https://github.com/MatchaChoco010/YureRig-Blender",
    "tracker_url": "https://github.com/MatchaChoco010/YureRig-Blender/issues",
    "category": "Rigging",
}
auto_load.init()


def register():
    auto_load.register()
    property_group.register_props()
    panel_ui.update_panel(None, bpy.context)


def unregister():
    auto_load.unregister()
    property_group.unregister_props()
