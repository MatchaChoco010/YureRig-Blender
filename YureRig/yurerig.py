import bpy


def update_panel(self, context):
    try:
        if "bl_rna" in YURERIG_PT_PanelUI.__dict__:
            bpy.utils.unregister_class(YURERIG_PT_PanelUI)
        YURERIG_PT_PanelUI.bl_category = context.preferences.addons[
            __package__].preferences.category
        bpy.utils.register_class(YURERIG_PT_PanelUI)
    except Exception:
        pass


def register_props():
    bpy.types.Scene.yurerig = bpy.props.PointerProperty(type=YURERIG_Props)


def unregister_props():
    del bpy.types.Scene.yurerig


class YURERIG_Preferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    category: bpy.props.StringProperty(
        default="YureRig",
        name="Addon Tab",
        update=update_panel
    )

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, "category")


class YURERIG_Props(bpy.types.PropertyGroup):
    param: bpy.props.BoolProperty(default=False, name="Check Box")


class YURERIG_OT_SetupOperator(bpy.types.Operator):
    bl_idname = "orito_itsuki.yurerig_setup"
    bl_label = "Setup Yure Rig"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print("Hello world!")
        return {'FINISHED'}


class YURERIG_PT_PanelUI(bpy.types.Panel):
    bl_label = "Yure Rig"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "YureRig"

    def draw(self, context):
        col = self.layout.column()
        col.operator("orito_itsuki.yurerig_setup")
        col.prop(context.scene.yurerig, "param")
