import bpy

from . import auto_load, yurerig

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
    yurerig.register_props()
    yurerig.update_panel(None, bpy.context)


def unregister():
    auto_load.unregister()
    yurerig.unregister_props()
