import re
from typing import List, Tuple

import bpy


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


class YURERIG_Props(bpy.types.PropertyGroup):
    """
    Addon-wide properties class.
    """

    bl_idname = "YURERIG_Props"
    controller_bone_radius: bpy.props.FloatProperty(  # type: ignore
        default=0.05, name="Controller Bone Radius"
    )
    controller_slider_size: bpy.props.FloatProperty(  # type: ignore
        default=0.25, name="Controller Slider Size"
    )
    rigidbody_root_size: bpy.props.FloatProperty(  # type: ignore
        default=0.01, name="RigidBody Root Size"
    )
    rigidbody_size_x: bpy.props.FloatProperty(  # type: ignore
        default=0.05, name="RigidBody Size X"
    )
    rigidbody_size_z: bpy.props.FloatProperty(  # type: ignore
        default=0.02, name="RigidBody Size Z"
    )
    rigidbody_gap: bpy.props.FloatProperty(  # type: ignore
        default=0.04, name="RigidBody Gap"
    )
    rigidbody_mass: bpy.props.FloatProperty(  # type: ignore
        default=1, name="RigidBody Mass"
    )
    rigidbody_joint_use_angular_limit_x: bpy.props.BoolProperty(  # type: ignore
        default=False, name="X Angle"
    )
    rigidbody_joint_angular_limit_lower_x: bpy.props.FloatProperty(  # type: ignore
        default=-45, name="X Lower"
    )
    rigidbody_joint_angular_limit_upper_x: bpy.props.FloatProperty(  # type: ignore
        default=45, name="X Upper"
    )
    rigidbody_joint_use_angular_limit_y: bpy.props.BoolProperty(  # type: ignore
        default=False, name="Y Angle"
    )
    rigidbody_joint_angular_limit_lower_y: bpy.props.FloatProperty(  # type: ignore
        default=-45, name="Y Lower"
    )
    rigidbody_joint_angular_limit_upper_y: bpy.props.FloatProperty(  # type: ignore
        default=45, name="Y Upper"
    )
    rigidbody_joint_use_angular_limit_z: bpy.props.BoolProperty(  # type: ignore
        default=False, name="Z Angle"
    )
    rigidbody_joint_angular_limit_lower_z: bpy.props.FloatProperty(  # type: ignore
        default=-45, name="Z Lower"
    )
    rigidbody_joint_angular_limit_upper_z: bpy.props.FloatProperty(  # type: ignore
        default=45, name="Z Upper"
    )
    rigidbody_joint_use_linear_limit_x: bpy.props.BoolProperty(  # type: ignore
        default=True, name="X Axis"
    )
    rigidbody_joint_linear_limit_lower_x: bpy.props.FloatProperty(  # type: ignore
        default=0, name="X Lower"
    )
    rigidbody_joint_linear_limit_upper_x: bpy.props.FloatProperty(  # type: ignore
        default=0, name="X Upper"
    )
    rigidbody_joint_use_linear_limit_y: bpy.props.BoolProperty(  # type: ignore
        default=True, name="Y Axis"
    )
    rigidbody_joint_linear_limit_lower_y: bpy.props.FloatProperty(  # type: ignore
        default=0, name="Y Lower"
    )
    rigidbody_joint_linear_limit_upper_y: bpy.props.FloatProperty(  # type: ignore
        default=0, name="Y Upper"
    )
    rigidbody_joint_use_linear_limit_z: bpy.props.BoolProperty(  # type: ignore
        default=True, name="Z Axis"
    )
    rigidbody_joint_linear_limit_lower_z: bpy.props.FloatProperty(  # type: ignore
        default=0, name="Z Lower"
    )
    rigidbody_joint_linear_limit_upper_z: bpy.props.FloatProperty(  # type: ignore
        default=0, name="Z Upper"
    )
    rigidbody_joint_use_angular_spring_x: bpy.props.BoolProperty(  # type: ignore
        default=True, name="X Angle"
    )
    rigidbody_joint_angular_spring_stiffness_x: bpy.props.FloatProperty(  # type: ignore
        default=0.1, name="X Stiffness"
    )
    rigidbody_joint_angular_spring_damping_x: bpy.props.FloatProperty(  # type: ignore
        default=0.5, name="X Dampinpg"
    )
    rigidbody_joint_use_angular_spring_y: bpy.props.BoolProperty(  # type: ignore
        default=True, name="Y Angle"
    )
    rigidbody_joint_angular_spring_stiffness_y: bpy.props.FloatProperty(  # type: ignore
        default=0.1, name="Y Stiffness"
    )
    rigidbody_joint_angular_spring_damping_y: bpy.props.FloatProperty(  # type: ignore
        default=0.5, name="Y Dampinpg"
    )
    rigidbody_joint_use_angular_spring_z: bpy.props.BoolProperty(  # type: ignore
        default=True, name="Z Angle"
    )
    rigidbody_joint_angular_spring_stiffness_z: bpy.props.FloatProperty(  # type: ignore
        default=0.1, name="Z Stiffness"
    )
    rigidbody_joint_angular_spring_damping_z: bpy.props.FloatProperty(  # type: ignore
        default=0.5, name="Z Dampinpg"
    )
    rigidbody_joint_use_linear_spring_x: bpy.props.BoolProperty(  # type: ignore
        default=False, name="X Axis"
    )
    rigidbody_joint_linear_spring_stiffness_x: bpy.props.FloatProperty(  # type: ignore
        default=10, name="X Stiffness"
    )
    rigidbody_joint_linear_spring_damping_x: bpy.props.FloatProperty(  # type: ignore
        default=0.5, name="X Dampinpg"
    )
    rigidbody_joint_use_linear_spring_y: bpy.props.BoolProperty(  # type: ignore
        default=False, name="Y Axis"
    )
    rigidbody_joint_linear_spring_stiffness_y: bpy.props.FloatProperty(  # type: ignore
        default=10, name="Y Stiffness"
    )
    rigidbody_joint_linear_spring_damping_y: bpy.props.FloatProperty(  # type: ignore
        default=0.5, name="Y Dampinpg"
    )
    rigidbody_joint_use_linear_spring_z: bpy.props.BoolProperty(  # type: ignore
        default=False, name="Z Axis"
    )
    rigidbody_joint_linear_spring_stiffness_z: bpy.props.FloatProperty(  # type: ignore
        default=10, name="Z Stiffness"
    )
    rigidbody_joint_linear_spring_damping_z: bpy.props.FloatProperty(  # type: ignore
        default=0.5, name="Z Dampinpg"
    )
    root_collection: bpy.props.PointerProperty(  # type: ignore
        type=bpy.types.Collection
    )
    joints_collection: bpy.props.PointerProperty(  # type: ignore
        type=bpy.types.Collection
    )
    rigidbodies_collection: bpy.props.PointerProperty(  # type: ignore
        type=bpy.types.Collection
    )
    rigidbodies_reset_goal_collection: bpy.props.PointerProperty(  # type: ignore
        type=bpy.types.Collection
    )
    controllers_collection: bpy.props.PointerProperty(  # type: ignore
        type=bpy.types.Collection
    )
    deform_bone_color: bpy.props.FloatVectorProperty(  # type: ignore
        default=(0.5, 0.5, 0.5), name="Deform Bone Color", subtype="COLOR"
    )
    controller_bone_color: bpy.props.FloatVectorProperty(  # type: ignore
        default=(0.5, 0.5, 1.0), name="Controller Bone Color", subtype="COLOR"
    )
    physics_bone_color: bpy.props.FloatVectorProperty(  # type: ignore
        default=(1.0, 0.5, 0.5), name="Physics Bone Color", subtype="COLOR"
    )

    def ctrl_bones(self, context: bpy.types.Context) -> List[Tuple[str, str, str]]:
        is_ctrl_bone_pattern = re.compile(r"^CTRL_.+")
        is_slider_bone_pattern = re.compile(r"^CTRL_physics_influence_slider_.+")
        armature = context.active_object
        ret = [("NONE", "None", "Remove")]
        if armature and armature.type == "ARMATURE" and armature.mode == "POSE":
            for item in [
                (bone.name, bone.name, "")
                for bone in armature.data.bones
                if is_ctrl_bone_pattern.match(bone.name)
                and not is_slider_bone_pattern.match(bone.name)
            ]:
                ret.append(item)
        return ret

    selected_ctrl_bone1: bpy.props.EnumProperty(items=ctrl_bones)  # type: ignore
    selected_ctrl_bone2: bpy.props.EnumProperty(items=ctrl_bones)  # type: ignore
    bone1_joint_pos_tail: bpy.props.BoolProperty(default=True)  # type: ignore
    bone2_joint_pos_tail: bpy.props.BoolProperty(default=True)  # type: ignore
