from typing import List, Optional
import bpy


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
    root_collection: bpy.props.PointerProperty(  # type: ignore
        type=bpy.types.Collection
    )
    joints_collection: bpy.props.PointerProperty(  # type: ignore
        type=bpy.types.Collection
    )
    rigidbodies_collection: bpy.props.PointerProperty(  # type: ignore
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
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == "ARMATURE" and obj.mode == "POSE"

    def init_collection(self) -> None:
        props = bpy.context.scene.yurerig
        if props.root_collection is None:
            if "YureRig" in bpy.data.collections:
                props.root_collection = bpy.data.collections["YureRig"]
            else:
                props.root_collection = bpy.data.collections.new(name="YureRig")
                bpy.context.scene.collection.children.link(props.root_collection)

        if props.joints_collection is None:
            if "YureRig Joints" in bpy.data.collections:
                props.joints_collection = bpy.data.collections["YureRig Joints"]
            else:
                props.joints_collection = bpy.data.collections.new(
                    name="YureRig Joints"
                )
                props.root_collection.children.link(props.joints_collection)

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

    def execute(self, context):
        self.init_collection()

        armature: bpy.types.Object = context.active_object
        selected_bones = context.selected_pose_bones
        active_bone = bpy.context.active_pose_bone

        bone_tree = BoneRelation.get_bone_tree(selected_bones, active_bone)

        print(armature)
        for rel in bone_tree:
            print("Bone Relation:")
            print(f"    parent: {rel.parent}")
            for c in rel.children:
                print(f"        child: {c}")

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
        col.operator("orito_itsuki.yurerig_setup")

        col.label(text="YureRig Collections")
        col.prop_search(props, "root_collection", bpy.data, "collections")
        col.prop_search(props, "joints_collection", bpy.data, "collections")
        col.prop_search(props, "rigidbodies_collection", bpy.data, "collections")
