import re
from typing import List, Optional, Tuple

import bpy


def update_panel(
    self: Optional[bpy.props.StringProperty], context: bpy.types.Context
) -> None:
    """
    Update Category of Panel by preferences 'Addon Tab' setting.
    """

    panels: List[bpy.types.Panel] = [
        YURERIG_PT_MAIN_PanelUI,
        YURERIG_PT_ControllerParameter_PanelUI,
        YURERIG_PT_RigidBodyParameter_PanelUI,
        YURERIG_PT_RigidBodyJointParameter_PanelUI,
        YURERIG_PT_RigidBodyJointLimitParameter_PanelUI,
        YURERIG_PT_RigidBodyJointLimitAngleParameter_PanelUI,
        YURERIG_PT_RigidBodyJointLimitLinearParameter_PanelUI,
        YURERIG_PT_RigidBodyJointSpringLinearrParameter_PanelUI,
        YURERIG_PT_RigidBodyJointSpringParameter_PanelUI,
        YURERIG_PT_RigidBodyJointSpringAngularParameter_PanelUI,
        YURERIG_PT_RigidBodyJointSpringLinearrParameter_PanelUI,
        YURERIG_PT_BoneColorSet_PanelUI,
        YURERIG_PT_Setup_PanelUI,
    ]

    try:
        for panel in panels:
            if "bl_rna" in panel.__dict__:
                bpy.utils.unregister_class(panel)
            panel.bl_category = context.preferences.addons[
                __package__
            ].preferences.category
            bpy.utils.register_class(panel)
    except Exception:
        pass


class YURERIG_PT_ControllerParameter_PanelUI(bpy.types.Panel):
    bl_label = "Controller Parameter"
    bl_idname = "YURERIG_PT_ControllerParameter_PanelUI"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "YURERIG_PT_MAIN_PanelUI"

    def draw(self, context: bpy.types.Context) -> None:
        props = context.scene.yurerig

        col = self.layout.column()
        col.use_property_split = True
        col.prop(props, "controller_bone_radius")
        col.prop(props, "controller_slider_size")


class YURERIG_PT_RigidBodyParameter_PanelUI(bpy.types.Panel):
    bl_label = "RigidBody Parameter"
    bl_idname = "YURERIG_PT_RigidBodyParameter_PanelUI"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "YURERIG_PT_MAIN_PanelUI"

    def draw(self, context: bpy.types.Context) -> None:
        props = context.scene.yurerig

        col = self.layout.column()
        col.use_property_split = True
        col.prop(props, "rigidbody_root_size", text="Root Size")
        col.prop(props, "rigidbody_size_x", text="Size X")
        col.prop(props, "rigidbody_size_z", text="Size Z")
        col.prop(props, "rigidbody_gap", text="Gap")
        col.prop(props, "rigidbody_mass", text="Mass")


class YURERIG_PT_RigidBodyJointParameter_PanelUI(bpy.types.Panel):
    bl_label = "RigidBody Joint Parameter"
    bl_idname = "YURERIG_PT_RigidBodyJointParameter_PanelUI"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "YURERIG_PT_MAIN_PanelUI"

    def draw(self, context: bpy.types.Context) -> None:
        pass


class YURERIG_PT_RigidBodyJointLimitParameter_PanelUI(bpy.types.Panel):
    bl_label = "Limit"
    bl_idname = "YURERIG_PT_RigidBodyJointLimitParameter_PanelUI"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "YURERIG_PT_RigidBodyJointParameter_PanelUI"

    def draw(self, context: bpy.types.Context) -> None:
        pass


class YURERIG_PT_RigidBodyJointLimitAngleParameter_PanelUI(bpy.types.Panel):
    bl_label = "Angular"
    bl_idname = "YURERIG_PT_RigidBodyJointLimitAngleParameter_PanelUI"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "YURERIG_PT_RigidBodyJointLimitParameter_PanelUI"

    def draw(self, context: bpy.types.Context) -> None:
        props = context.scene.yurerig
        col = self.layout.column()
        col.use_property_split = True

        flow = col.grid_flow(
            row_major=True, columns=0, even_columns=True, even_rows=False, align=True
        )

        flow_col = flow.column()
        flow_col.prop(props, "rigidbody_joint_use_angular_limit_x")
        sub = flow_col.column(align=True)
        sub.active = props.rigidbody_joint_use_angular_limit_x
        sub.prop(props, "rigidbody_joint_angular_limit_lower_x", text="X Lower")
        sub.prop(props, "rigidbody_joint_angular_limit_upper_x", text="Upper")

        flow_col = flow.column()
        flow_col.prop(props, "rigidbody_joint_use_angular_limit_y")
        sub = flow_col.column(align=True)
        sub.active = props.rigidbody_joint_use_angular_limit_y
        sub.prop(props, "rigidbody_joint_angular_limit_lower_y", text="Y Lower")
        sub.prop(props, "rigidbody_joint_angular_limit_upper_y", text="Upper")

        flow_col = flow.column()
        flow_col.prop(props, "rigidbody_joint_use_angular_limit_z")
        sub = flow_col.column(align=True)
        sub.active = props.rigidbody_joint_use_angular_limit_z
        sub.prop(props, "rigidbody_joint_angular_limit_lower_z", text="Z Lower")
        sub.prop(props, "rigidbody_joint_angular_limit_upper_z", text="Upper")


class YURERIG_PT_RigidBodyJointLimitLinearParameter_PanelUI(bpy.types.Panel):
    bl_label = "Linear"
    bl_idname = "YURERIG_PT_RigidBodyJointLimitLinearParameter_PanelUI"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "YURERIG_PT_RigidBodyJointLimitParameter_PanelUI"

    def draw(self, context: bpy.types.Context) -> None:
        props = context.scene.yurerig
        col = self.layout.column()
        col.use_property_split = True

        flow = col.grid_flow(
            row_major=True, columns=0, even_columns=True, even_rows=False, align=True
        )

        flow_col = flow.column()
        flow_col.prop(props, "rigidbody_joint_use_linear_limit_x")
        sub = flow_col.column(align=True)
        sub.active = props.rigidbody_joint_use_linear_limit_x
        sub.prop(props, "rigidbody_joint_linear_limit_lower_x", text="X Lower")
        sub.prop(props, "rigidbody_joint_linear_limit_upper_x", text="Upper")

        flow_col = flow.column()
        flow_col.prop(props, "rigidbody_joint_use_linear_limit_y")
        sub = flow_col.column(align=True)
        sub.active = props.rigidbody_joint_use_linear_limit_y
        sub.prop(props, "rigidbody_joint_linear_limit_lower_y", text="Y Lower")
        sub.prop(props, "rigidbody_joint_linear_limit_upper_y", text="Upper")

        flow_col = flow.column()
        flow_col.prop(props, "rigidbody_joint_use_linear_limit_z")
        sub = flow_col.column(align=True)
        sub.active = props.rigidbody_joint_use_linear_limit_z
        sub.prop(props, "rigidbody_joint_linear_limit_lower_z", text="Z Lower")
        sub.prop(props, "rigidbody_joint_linear_limit_upper_z", text="Upper")


class YURERIG_PT_RigidBodyJointSpringParameter_PanelUI(bpy.types.Panel):
    bl_label = "Spring"
    bl_idname = "YURERIG_PT_RigidBodyJointSpringParameter_PanelUI"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "YURERIG_PT_RigidBodyJointParameter_PanelUI"

    def draw(self, context: bpy.types.Context) -> None:
        pass


class YURERIG_PT_RigidBodyJointSpringAngularParameter_PanelUI(bpy.types.Panel):
    bl_label = "Angular"
    bl_idname = "YURERIG_PT_RigidBodyJointSpringAngularParameter_PanelUI"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "YURERIG_PT_RigidBodyJointSpringParameter_PanelUI"

    def draw(self, context: bpy.types.Context) -> None:
        props = context.scene.yurerig
        col = self.layout.column()
        col.use_property_split = True

        flow = col.grid_flow(
            row_major=True, columns=0, even_columns=True, even_rows=False, align=True
        )

        flow_col = flow.column()
        flow_col.prop(props, "rigidbody_joint_use_angular_spring_x")
        sub = flow_col.column(align=True)
        sub.active = props.rigidbody_joint_use_angular_spring_x
        sub.prop(
            props, "rigidbody_joint_angular_spring_stiffness_x", text="X Stiffness"
        )
        sub.prop(props, "rigidbody_joint_angular_spring_damping_x", text="Damping")

        flow_col = flow.column()
        flow_col.prop(props, "rigidbody_joint_use_angular_spring_y")
        sub = flow_col.column(align=True)
        sub.active = props.rigidbody_joint_use_angular_spring_y
        sub.prop(
            props, "rigidbody_joint_angular_spring_stiffness_y", text="Y Stiffness"
        )
        sub.prop(props, "rigidbody_joint_angular_spring_damping_y", text="Damping")

        flow_col = flow.column()
        flow_col.prop(props, "rigidbody_joint_use_angular_spring_z")
        sub = flow_col.column(align=True)
        sub.active = props.rigidbody_joint_use_angular_spring_z
        sub.prop(
            props, "rigidbody_joint_angular_spring_stiffness_z", text="Z Stiffness"
        )
        sub.prop(props, "rigidbody_joint_angular_spring_damping_z", text="Damping")


class YURERIG_PT_RigidBodyJointSpringLinearrParameter_PanelUI(bpy.types.Panel):
    bl_label = "Linear"
    bl_idname = "YURERIG_PT_RigidBodyJointSpringLinearrParameter_PanelUI"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "YURERIG_PT_RigidBodyJointSpringParameter_PanelUI"

    def draw(self, context: bpy.types.Context) -> None:
        props = context.scene.yurerig
        col = self.layout.column()
        col.use_property_split = True

        flow = col.grid_flow(
            row_major=True, columns=0, even_columns=True, even_rows=False, align=True
        )

        flow_col = flow.column()
        flow_col.prop(props, "rigidbody_joint_use_linear_spring_x")
        sub = flow_col.column(align=True)
        sub.active = props.rigidbody_joint_use_linear_spring_x
        sub.prop(props, "rigidbody_joint_linear_spring_stiffness_x", text="X Stiffness")
        sub.prop(props, "rigidbody_joint_linear_spring_damping_x", text="Damping")

        flow_col = flow.column()
        flow_col.prop(props, "rigidbody_joint_use_linear_spring_y")
        sub = flow_col.column(align=True)
        sub.active = props.rigidbody_joint_use_linear_spring_y
        sub.prop(props, "rigidbody_joint_linear_spring_stiffness_y", text="Y Stiffness")
        sub.prop(props, "rigidbody_joint_linear_spring_damping_y", text="Damping")

        flow_col = flow.column()
        flow_col.prop(props, "rigidbody_joint_use_linear_spring_z")
        sub = flow_col.column(align=True)
        sub.active = props.rigidbody_joint_use_linear_spring_z
        sub.prop(props, "rigidbody_joint_linear_spring_stiffness_z", text="Z Stiffness")
        sub.prop(props, "rigidbody_joint_linear_spring_damping_z", text="Damping")


class YURERIG_PT_BoneColorSet_PanelUI(bpy.types.Panel):
    bl_label = "Bone Color Set"
    bl_idname = "YURERIG_PT_BoneColorSet_PanelUI"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "YURERIG_PT_MAIN_PanelUI"

    def draw(self, context: bpy.types.Context) -> None:
        props = context.scene.yurerig

        col = self.layout.column()
        col.use_property_split = True
        col.prop(props, "deform_bone_color")
        col.prop(props, "controller_bone_color")
        col.prop(props, "physics_bone_color")


class YURERIG_PT_Setup_PanelUI(bpy.types.Panel):
    bl_label = "Setup"
    bl_idname = "YURERIG_PT_Setup_PanelUI"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "YURERIG_PT_MAIN_PanelUI"

    def ctrl_bones(self, context: bpy.types.Context) -> List[Tuple[str, str, str]]:
        armature = bpy.context.active_object
        is_ctrl_bone_pattern = re.compile(r"^CTRL_.+")
        is_slider_bone_pattern = re.compile(r"^CTRL_physics_influence_slider_.+")
        return [
            (bone.name, bone.name, "")
            for bone in armature.data.bones
            if is_ctrl_bone_pattern.match(bone.name)
            and not is_slider_bone_pattern.match(bone.name)
        ]

    def draw(self, context: bpy.types.Context) -> None:
        props = context.scene.yurerig

        col = self.layout.column()

        col.separator()
        col.operator("orito_itsuki.yurerig_setup")

        col.separator()
        box = col.box()
        box.label(text="Add Extra Joint")

        split = box.split(factor=0.8)
        split.prop(
            props,
            "selected_ctrl_bone1",
            icon="BONE_DATA",
            text="Bone 1",
        )
        label = "Tail" if props.bone1_joint_pos_tail else "Head"
        split.prop(props, "bone1_joint_pos_tail", text=label, toggle=True)

        split = box.split(factor=0.8)
        split.prop(
            props,
            "selected_ctrl_bone2",
            icon="BONE_DATA",
            text="Bone 2",
        )
        label = "Tail" if props.bone2_joint_pos_tail else "Head"
        split.prop(props, "bone2_joint_pos_tail", text=label, toggle=True)
        box.operator("orito_itsuki.yurerig_add_extra_joint")

        col.separator()
        col.operator("orito_itsuki.yurerig_remove")


class YURERIG_PT_MAIN_PanelUI(bpy.types.Panel):
    """
    UserInterface class for YureRig addon.
    """

    bl_label = "Yure Rig"
    bl_idname = "YURERIG_PT_MAIN_PanelUI"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "YureRig"

    def draw(self, context: bpy.types.Context) -> None:
        pass
