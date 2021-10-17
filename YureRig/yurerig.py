import math
import re
from typing import List, Optional

import bpy
from mathutils import Vector


def update_panel(
    self: Optional[bpy.props.StringProperty], context: bpy.types.Context
) -> None:
    """
    Update Category of Panel by preferences 'Addon Tab' setting.
    """

    try:
        if "bl_rna" in YURERIG_PT_PanelUI.__dict__:
            bpy.utils.unregister_class(YURERIG_PT_PanelUI)
        YURERIG_PT_PanelUI.bl_category = context.preferences.addons[
            __package__
        ].preferences.category
        bpy.utils.register_class(YURERIG_PT_PanelUI)
    except Exception:
        pass


def register_props() -> None:
    """
    Register addon-wide properties.
    """

    bpy.types.Scene.yurerig = bpy.props.PointerProperty(type=YURERIG_Props)


def unregister_props() -> None:
    """
    Unregister addon-wide properties.
    """

    del bpy.types.Scene.yurerig


class YURERIG_Preferences(bpy.types.AddonPreferences):
    """
    Addon preferences class.
    """

    bl_idname = __package__

    category: bpy.props.StringProperty(  # type: ignore
        default="YureRig", name="Addon Tab", update=update_panel
    )

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        col = layout.column()
        col.prop(self, "category")


class YURERIG_Props(bpy.types.PropertyGroup):
    """
    Addon-wide properties class.
    """

    param: bpy.props.BoolProperty(default=False, name="Check Box")  # type: ignore
    controller_radius: bpy.props.FloatProperty(default=0.2)  # type: ignore
    root_collection: bpy.props.PointerProperty(  # type: ignore
        type=bpy.types.Collection
    )
    joints_collection: bpy.props.PointerProperty(  # type: ignore
        type=bpy.types.Collection
    )
    rigidbodies_collection: bpy.props.PointerProperty(  # type: ignore
        type=bpy.types.Collection
    )
    controllers_collection: bpy.props.PointerProperty(  # type: ignore
        type=bpy.types.Collection
    )


class BoneRelation:
    """
    Class for represent bone relations.
    bonerelation has only one parent bone and multiple children.
    """

    def __init__(self, parent: bpy.types.PoseBone):
        self.parent = parent
        self.children: List[bpy.types.PoseBone] = []

    def set_children(self, selected_bones: List[bpy.types.PoseBone]) -> None:
        pass

    @classmethod
    def get_bone_tree(
        cls, selected_bones: List[bpy.types.PoseBone], active_bone: bpy.types.PoseBone
    ) -> List["BoneRelation"]:
        """
        Search chained bone from active_bone in `selected_bones` and
        make tree of bones chaining start from `active_bone`.

        ## Parameters
        `selected_bones`
            Selected bones.
            Search chained bones from these bones.
        `active_bone`
            Active bone.
            This bone will the root of bones tree.
        """

        relations: List[BoneRelation] = []

        parent = active_bone
        while len(selected_bones) > 0:
            selected_bones.remove(parent)
            relation = BoneRelation(parent)
            for b in selected_bones:
                if b.parent == parent:
                    relation.children.append(b)
            relations.append(relation)
            for r in relations:
                for c in r.children:
                    if c in selected_bones:
                        parent = c
                        break
                else:
                    continue
                break
            else:
                break
            continue

        return relations


class YURERIG_OT_SetupOperator(bpy.types.Operator):
    """
    Setup DEF_ bones, CTRL_ bones and PHYS_ bones, add rigidbody objects and
    generic joints, add controller for turn on physics.
    """

    bl_idname = "orito_itsuki.yurerig_setup"
    bl_label = "Setup Yure Rig"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        obj = context.active_object
        if obj and obj.type == "ARMATURE" and obj.mode == "POSE":
            return (
                obj.data.bones.active is not None
                and len(bpy.context.selected_pose_bones) > 0
            )
        return False

    def init_collection(self) -> None:
        props = bpy.context.scene.yurerig
        if props.root_collection is None:
            if "YureRig" in bpy.data.collections:
                props.root_collection = bpy.data.collections["YureRig"]
            else:
                props.root_collection = bpy.data.collections.new(name="YureRig")
                bpy.context.scene.collection.children.link(props.root_collection)
            props.root_collection.hide_viewport = True
            props.root_collection.hide_render = True

        if props.joints_collection is None:
            if "YureRig Joints" in bpy.data.collections:
                props.joints_collection = bpy.data.collections["YureRig Joints"]
            else:
                props.joints_collection = bpy.data.collections.new(
                    name="YureRig Joints"
                )
                props.root_collection.children.link(props.joints_collection)
            props.joints_collection.hide_viewport = True
            props.joints_collection.hide_render = True

        if props.rigidbodies_collection is None:
            if "YureRig RigidBodies" in bpy.data.collections:
                props.rigidbodies_collection = bpy.data.collections[
                    "YureRig RigidBodies"
                ]
            else:
                props.rigidbodies_collection = bpy.data.collections.new(
                    name="YureRig RigidBodies"
                )
                props.root_collection.children.link(props.rigidbodies_collection)
            props.rigidbodies_collection.hide_viewport = True
            props.rigidbodies_collection.hide_render = True

        if props.controllers_collection is None:
            if "YureRig Controller Objects" in bpy.data.collections:
                props.controllers_collection = bpy.data.collections[
                    "YureRig Controller Objects"
                ]
            else:
                props.controllers_collection = bpy.data.collections.new(
                    name="YureRig Controller Objects"
                )
                props.root_collection.children.link(props.controllers_collection)
            props.controllers_collection.hide_viewport = True
            props.controllers_collection.hide_render = True

    def make_controller_object(
        self, name: str, head: Vector, tail: Vector
    ) -> bpy.types.Object:
        length = (head - tail).length
        radius = bpy.context.scene.yurerig.controller_radius
        verts: List[Vector] = []
        for i in range(6):
            theta = math.radians(i * 60)
            verts.append(
                Vector((math.cos(theta) * radius, 0, math.sin(theta) * radius))
            )
            verts.append(
                Vector((math.cos(theta) * radius, length, math.sin(theta) * radius))
            )
        faces = [
            [0, 1, 3, 2],
            [2, 3, 5, 4],
            [4, 5, 7, 6],
            [6, 7, 9, 8],
            [8, 9, 11, 10],
            [10, 11, 1, 0],
            [0, 2, 4, 6, 8, 10],
            [1, 3, 5, 7, 9, 11],
        ]
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(verts, [], faces)
        mesh.update(calc_edges=True)
        obj = bpy.data.objects.new(name, object_data=mesh)
        obj.display_type = "WIRE"
        bpy.context.scene.yurerig.controllers_collection.objects.link(obj)
        return obj

    def update_controller_object_radius(
        self, obj: bpy.types.Object, head: Vector, tail: Vector
    ) -> None:
        obj.display_type = "WIRE"
        length = (head - tail).length
        radius = bpy.context.scene.yurerig.controller_radius
        verts: List[Vector] = []
        for i in range(6):
            theta = math.radians(i * 60)
            verts.append(
                Vector((math.cos(theta) * radius, 0, math.sin(theta) * radius))
            )
            verts.append(
                Vector((math.cos(theta) * radius, length, math.sin(theta) * radius))
            )
        faces = [
            [0, 1, 3, 2],
            [2, 3, 5, 4],
            [4, 5, 7, 6],
            [6, 7, 9, 8],
            [8, 9, 11, 10],
            [10, 11, 1, 0],
            [0, 2, 4, 6, 8, 10],
            [1, 3, 5, 7, 9, 11],
        ]
        name = obj.name
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(verts, [], faces)
        mesh.update(calc_edges=True)
        obj.data = mesh

    def execute(self, context):
        self.init_collection()

        armature: bpy.types.Object = context.active_object
        selected_bones = context.selected_pose_bones
        active_bone = bpy.context.active_pose_bone

        bone_tree = BoneRelation.get_bone_tree(selected_bones, active_bone)

        def_bones: List[bpy.types.PoseBone] = []
        ctrl_bones: List[bpy.types.PoseBone] = []

        armature.data.layers = [layer == 0 or layer == 8 for layer in range(32)]

        bpy.ops.object.mode_set(mode="EDIT")

        # Setup rig bones
        is_def_bone_pattern = re.compile(r"DEF_.+")
        is_ctrl_bone_pattern = re.compile(r"CTRL_.+")
        for rel in bone_tree:
            for child_bone in rel.children:
                if is_ctrl_bone_pattern.match(child_bone.name):
                    continue

                child_bone.bone.hide_select = True

                # Add `DEF_` prefix to the bone
                name = child_bone.bone.name
                if not is_def_bone_pattern.match(name):
                    name = f"DEF_{name}"
                    child_bone.bone.name = name
                parent_name = rel.parent.bone.name
                if parent_name == active_bone.name:
                    parent_is_active_bone = True
                else:
                    parent_is_active_bone = False
                    if not is_def_bone_pattern.match(parent_name):
                        parent_name = f"DEF_{parent_name}"
                def_bones.append(child_bone)

                # Create a `CTRL_` bone
                ctrl_name = f"CTRL_{name[4:]}"
                if ctrl_name in armature.data.edit_bones:
                    ctrl_bone = armature.data.edit_bones[ctrl_name]
                else:
                    ctrl_bone = armature.data.edit_bones.new(ctrl_name)
                ctrl_bone.head = child_bone.head
                ctrl_bone.tail = child_bone.tail
                if parent_is_active_bone:
                    ctrl_bone.parent = armature.data.edit_bones[active_bone.name]
                else:
                    parent_ctrl_name = f"CTRL_{parent_name[4:]}"
                    ctrl_bone.parent = armature.data.edit_bones[parent_ctrl_name]
                ctrl_bone.roll = armature.data.edit_bones[name].roll
                ctrl_bone.use_connect = child_bone.bone.use_connect
                ctrl_bone.show_wire = True
                armature.update_from_editmode()
                ctrl_pose_bone = armature.pose.bones[ctrl_name]
                if ctrl_pose_bone.custom_shape is None:
                    ctrl_obj = self.make_controller_object(
                        f"{ctrl_name}_Controller", ctrl_bone.head, ctrl_bone.tail
                    )
                    ctrl_pose_bone.custom_shape = ctrl_obj
                    ctrl_pose_bone.use_custom_shape_bone_size = False
                else:
                    self.update_controller_object_radius(
                        ctrl_pose_bone.custom_shape, ctrl_bone.head, ctrl_bone.tail
                    )
                ctrl_bones.append(ctrl_pose_bone)
                ctrl_bone.layers = [layer == 8 for layer in range(32)]

        bpy.ops.object.mode_set(mode="POSE")

        # Set DEF_ and PHYS_ bone non selectable
        for b in def_bones:
            b.bone.hide_select = True

        # Select CTRL_ bones
        for b in armature.data.bones:
            b.select = False
        for b in ctrl_bones:
            b.bone.select = True
        armature.data.bones.active = active_bone.bone
        return {"FINISHED"}


class YURERIG_PT_PanelUI(bpy.types.Panel):
    """
    UserInterface class for YureRig addon.
    """

    bl_label = "Yure Rig"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "YureRig"

    @classmethod
    def search_collections(cls) -> List[str]:
        collection_names = [c.name for c in bpy.data.collections]
        return collection_names

    def draw(self, context):
        props = context.scene.yurerig

        col = self.layout.column()
        col.prop(props, "controller_radius")
        col.operator("orito_itsuki.yurerig_setup")

        col.separator()
        col.label(text="YureRig Collections")
        col.prop_search(props, "root_collection", bpy.data, "collections")
        col.prop_search(props, "joints_collection", bpy.data, "collections")
        col.prop_search(props, "rigidbodies_collection", bpy.data, "collections")
        col.prop_search(props, "controllers_collection", bpy.data, "collections")
