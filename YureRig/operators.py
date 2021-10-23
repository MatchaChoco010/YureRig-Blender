import math
import re
from typing import List, Set

import bpy
from mathutils import Vector


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
            props.rigidbodies_collection.lineart_usage = "EXCLUDE"
            props.rigidbodies_collection.hide_viewport = True
            props.rigidbodies_collection.hide_render = True

        if props.rigidbodies_reset_goal_collection is None:
            if "YureRig RigidBodies Reset Goal" in bpy.data.collections:
                props.rigidbodies_reset_goal_collection = bpy.data.collections[
                    "YureRig RigidBodies Reset Goall"
                ]
            else:
                props.rigidbodies_reset_goal_collection = bpy.data.collections.new(
                    name="YureRig RigidBodies Reset Goal"
                )
                props.root_collection.children.link(
                    props.rigidbodies_reset_goal_collection
                )
            props.rigidbodies_reset_goal_collection.lineart_usage = "EXCLUDE"
            props.rigidbodies_reset_goal_collection.hide_viewport = True
            props.rigidbodies_reset_goal_collection.hide_render = True

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
        radius = bpy.context.scene.yurerig.controller_bone_radius
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

    def make_slider_root(
        self, name: str, fk: bpy.types.Object, phys: bpy.types.Object
    ) -> bpy.types.Object:
        slider_size = bpy.context.scene.yurerig.controller_slider_size
        slider_gap = slider_size / 6
        slider_body = slider_size / 6 * 2
        verts: List[Vector] = []
        for i in range(7):
            theta = math.radians(i * 30)
            verts.append(
                Vector((math.cos(theta) * slider_gap, 0, -math.sin(theta) * slider_gap))
            )
        for i in range(7):
            theta = math.radians(i * 30)
            verts.append(
                Vector(
                    (
                        math.cos(theta) * slider_gap,
                        0,
                        slider_body + math.sin(theta) * slider_gap,
                    )
                )
            )

        faces = [[0, 1, 2, 3, 4, 5, 6, 13, 12, 11, 10, 9, 8, 7]]
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(verts, [], faces)
        mesh.update(calc_edges=True)
        obj = bpy.data.objects.new(name, object_data=mesh)
        obj.display_type = "WIRE"
        bpy.context.scene.yurerig.controllers_collection.objects.link(obj)

        bpy.context.scene.collection.objects.link(obj)
        bpy.ops.object.mode_set(mode="OBJECT")
        for o in bpy.context.view_layer.objects:
            o.select_set(o == obj or o == fk or o == phys)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.join({"active_object": obj, "selected_objects": [obj, fk, phys]})
        bpy.context.scene.collection.objects.unlink(obj)

        return obj

    def make_slider_obj(self, name: str) -> bpy.types.Object:
        slider_size = bpy.context.scene.yurerig.controller_slider_size
        radius = slider_size / 7.5
        verts: List[Vector] = []
        for i in range(12):
            theta = math.radians(i * 30)
            verts.append(
                Vector((math.cos(theta) * radius, 0, -math.sin(theta) * radius))
            )

        faces = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]]
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(verts, [], faces)
        mesh.update(calc_edges=True)
        obj = bpy.data.objects.new(name, object_data=mesh)
        obj.display_type = "WIRE"
        bpy.context.scene.yurerig.controllers_collection.objects.link(obj)
        return obj

    def make_phys_bone_object(
        self, name: str, head: Vector, tail: Vector
    ) -> bpy.types.Object:
        x_size = bpy.context.scene.yurerig.rigidbody_size_x
        z_size = bpy.context.scene.yurerig.rigidbody_size_z
        gap = bpy.context.scene.yurerig.rigidbody_gap
        length = (head - tail).length

        verts: List[Vector] = []
        verts.append(Vector((x_size / 2, gap / 2, z_size / 2)))
        verts.append(Vector((x_size / 2, gap / 2, -z_size / 2)))
        verts.append(Vector((-x_size / 2, gap / 2, z_size / 2)))
        verts.append(Vector((-x_size / 2, gap / 2, -z_size / 2)))
        verts.append(Vector((x_size / 2, length - gap / 2, z_size / 2)))
        verts.append(Vector((x_size / 2, length - gap / 2, -z_size / 2)))
        verts.append(Vector((-x_size / 2, length - gap / 2, z_size / 2)))
        verts.append(Vector((-x_size / 2, length - gap / 2, -z_size / 2)))

        faces = [
            [0, 1, 3, 2],
            [4, 5, 7, 6],
            [0, 1, 5, 4],
            [1, 2, 6, 5],
            [2, 3, 7, 6],
            [3, 0, 4, 7],
        ]
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(verts, [], faces)
        mesh.update(calc_edges=True)

        obj = bpy.data.objects.new(name, object_data=mesh)
        obj.display_type = "WIRE"

        bpy.context.scene.yurerig.controllers_collection.objects.link(obj)
        return obj

    def make_rigidbody_object(
        self, name: str, head: Vector, tail: Vector
    ) -> bpy.types.Object:
        x_size = bpy.context.scene.yurerig.rigidbody_size_x
        z_size = bpy.context.scene.yurerig.rigidbody_size_z
        gap = bpy.context.scene.yurerig.rigidbody_gap
        length = (head - tail).length

        verts: List[Vector] = []
        verts.append(Vector((x_size / 2, -length / 2 + gap / 2, z_size / 2)))
        verts.append(Vector((x_size / 2, -length / 2 + gap / 2, -z_size / 2)))
        verts.append(Vector((-x_size / 2, -length / 2 + gap / 2, z_size / 2)))
        verts.append(Vector((-x_size / 2, -length / 2 + gap / 2, -z_size / 2)))
        verts.append(Vector((x_size / 2, length / 2 - gap / 2, z_size / 2)))
        verts.append(Vector((x_size / 2, length / 2 - gap / 2, -z_size / 2)))
        verts.append(Vector((-x_size / 2, length / 2 - gap / 2, z_size / 2)))
        verts.append(Vector((-x_size / 2, length / 2 - gap / 2, -z_size / 2)))

        faces = [
            [0, 1, 3, 2],
            [4, 5, 7, 6],
            [0, 1, 5, 4],
            [1, 2, 6, 5],
            [2, 3, 7, 6],
            [3, 0, 4, 7],
        ]
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(verts, [], faces)
        mesh.update(calc_edges=True)

        obj = bpy.data.objects.new(name, object_data=mesh)
        obj.display_type = "WIRE"
        bpy.context.scene.rigidbody_world.collection.objects.link(obj)
        obj.rigid_body.type = "ACTIVE"
        obj.rigid_body.mass = bpy.context.scene.yurerig.rigidbody_mass

        obj.location = (tail + head) / 2
        obj.rotation_mode = "QUATERNION"
        obj.rotation_quaternion = (tail - head).to_track_quat("Y", "Z")

        bpy.context.scene.yurerig.rigidbodies_collection.objects.link(obj)
        return obj

    def make_rigidbody_reset_goal_object(
        self,
        name: str,
        head: Vector,
        tail: Vector,
        physics_influence_slider_name: str,
        armature: bpy.types.Object,
        rigidbody_obj: bpy.types.Object,
    ) -> bpy.types.Object:
        x_size = bpy.context.scene.yurerig.rigidbody_size_x
        z_size = bpy.context.scene.yurerig.rigidbody_size_z
        gap = bpy.context.scene.yurerig.rigidbody_gap
        length = (head - tail).length

        verts: List[Vector] = []
        verts.append(Vector((x_size / 2, -length / 2 + gap / 2, z_size / 2)))
        verts.append(Vector((x_size / 2, -length / 2 + gap / 2, -z_size / 2)))
        verts.append(Vector((-x_size / 2, -length / 2 + gap / 2, z_size / 2)))
        verts.append(Vector((-x_size / 2, -length / 2 + gap / 2, -z_size / 2)))
        verts.append(Vector((x_size / 2, length / 2 - gap / 2, z_size / 2)))
        verts.append(Vector((x_size / 2, length / 2 - gap / 2, -z_size / 2)))
        verts.append(Vector((-x_size / 2, length / 2 - gap / 2, z_size / 2)))
        verts.append(Vector((-x_size / 2, length / 2 - gap / 2, -z_size / 2)))

        faces = [
            [0, 1, 3, 2],
            [4, 5, 7, 6],
            [0, 1, 5, 4],
            [1, 2, 6, 5],
            [2, 3, 7, 6],
            [3, 0, 4, 7],
        ]
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(verts, [], faces)
        mesh.update(calc_edges=True)

        obj = bpy.data.objects.new(name, object_data=mesh)
        obj.display_type = "WIRE"

        bpy.context.scene.rigidbody_world.collection.objects.link(obj)
        obj.rigid_body.type = "PASSIVE"
        obj.rigid_body.collision_collections = [layer == 19 for layer in range(20)]

        bpy.context.scene.rigidbody_world.constraints.objects.link(obj)
        obj.rigid_body_constraint.type = "FIXED"
        obj.rigid_body_constraint.object1 = obj
        obj.rigid_body_constraint.object2 = rigidbody_obj
        obj.rigid_body_constraint.enabled
        constraint_enabled_driver = obj.rigid_body_constraint.driver_add("enabled")
        constraint_enabled_driver.driver.type = "SCRIPTED"
        var = constraint_enabled_driver.driver.variables.new()
        var.name = "locZ"
        var.type = "TRANSFORMS"
        var.targets[0].id = armature
        var.targets[0].bone_target = physics_influence_slider_name
        var.targets[0].transform_space = "LOCAL_SPACE"
        var.targets[0].transform_type = "LOC_Z"
        constraint_enabled_driver.driver.expression = "locZ == 0"

        obj.location = (tail + head) / 2
        obj.rotation_mode = "QUATERNION"
        obj.rotation_quaternion = (tail - head).to_track_quat("Y", "Z")

        bpy.context.scene.yurerig.rigidbodies_reset_goal_collection.objects.link(obj)
        return obj

    def make_rigidbody_root_object(
        self, name: str, head: Vector, tail: Vector
    ) -> bpy.types.Object:
        size = bpy.context.scene.yurerig.rigidbody_root_size

        verts: List[Vector] = []
        verts.append(Vector((size / 2, -size / 2, size / 2)))
        verts.append(Vector((size / 2, -size / 2, -size / 2)))
        verts.append(Vector((-size / 2, -size / 2, size / 2)))
        verts.append(Vector((-size / 2, -size / 2, -size / 2)))
        verts.append(Vector((size / 2, size / 2, size / 2)))
        verts.append(Vector((size / 2, size / 2, -size / 2)))
        verts.append(Vector((-size / 2, size / 2, size / 2)))
        verts.append(Vector((-size / 2, size / 2, -size / 2)))

        faces = [
            [0, 1, 3, 2],
            [4, 5, 7, 6],
            [0, 1, 5, 4],
            [1, 2, 6, 5],
            [2, 3, 7, 6],
            [3, 0, 4, 7],
        ]
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(verts, [], faces)
        mesh.update(calc_edges=True)

        obj = bpy.data.objects.new(name, object_data=mesh)
        obj.display_type = "WIRE"
        bpy.context.scene.rigidbody_world.collection.objects.link(obj)
        obj.rigid_body.type = "PASSIVE"
        obj.rigid_body.kinematic = True

        obj.location = head
        obj.rotation_mode = "QUATERNION"
        obj.rotation_quaternion = (tail - head).to_track_quat("Y", "Z")

        bpy.context.scene.yurerig.rigidbodies_collection.objects.link(obj)
        return obj

    def update_rigidbody_rotation(
        self, obj: bpy.types.Object, head: Vector, tail: Vector
    ) -> None:
        obj.rotation_mode = "QUATERNION"
        obj.rotation_quaternion = (tail - head).to_track_quat("Y", "Z")

    def set_joint_properties(self, joint: bpy.types.RigidBodyConstraint) -> None:
        props = bpy.context.scene.yurerig
        joint.use_limit_ang_x = props.rigidbody_joint_use_angular_limit_x
        joint.limit_ang_x_lower = props.rigidbody_joint_angular_limit_lower_x
        joint.limit_ang_x_upper = props.rigidbody_joint_angular_limit_upper_x
        joint.use_limit_ang_y = props.rigidbody_joint_use_angular_limit_y
        joint.limit_ang_y_lower = props.rigidbody_joint_angular_limit_lower_y
        joint.limit_ang_y_upper = props.rigidbody_joint_angular_limit_upper_y
        joint.use_limit_ang_z = props.rigidbody_joint_use_angular_limit_z
        joint.limit_ang_z_lower = props.rigidbody_joint_angular_limit_lower_z
        joint.limit_ang_z_upper = props.rigidbody_joint_angular_limit_upper_z

        joint.use_limit_lin_x = props.rigidbody_joint_use_linear_limit_x
        joint.limit_lin_x_lower = props.rigidbody_joint_linear_limit_lower_x
        joint.limit_lin_x_upper = props.rigidbody_joint_linear_limit_upper_x
        joint.use_limit_lin_y = props.rigidbody_joint_use_linear_limit_y
        joint.limit_lin_y_lower = props.rigidbody_joint_linear_limit_lower_y
        joint.limit_lin_y_upper = props.rigidbody_joint_linear_limit_upper_y
        joint.use_limit_lin_z = props.rigidbody_joint_use_linear_limit_z
        joint.limit_lin_z_lower = props.rigidbody_joint_linear_limit_lower_z
        joint.limit_lin_z_upper = props.rigidbody_joint_linear_limit_upper_z

        joint.use_spring_ang_x = props.rigidbody_joint_use_angular_spring_x
        joint.spring_stiffness_ang_x = props.rigidbody_joint_angular_spring_stiffness_x
        joint.spring_damping_ang_x = props.rigidbody_joint_angular_spring_damping_x
        joint.use_spring_ang_y = props.rigidbody_joint_use_angular_spring_y
        joint.spring_stiffness_ang_y = props.rigidbody_joint_angular_spring_stiffness_y
        joint.spring_damping_ang_y = props.rigidbody_joint_angular_spring_damping_y
        joint.use_spring_ang_z = props.rigidbody_joint_use_angular_spring_z
        joint.spring_stiffness_ang_z = props.rigidbody_joint_angular_spring_stiffness_z
        joint.spring_damping_ang_z = props.rigidbody_joint_angular_spring_damping_z

        joint.use_spring_x = props.rigidbody_joint_use_linear_spring_x
        joint.spring_stiffness_x = props.rigidbody_joint_linear_spring_stiffness_x
        joint.spring_damping_x = props.rigidbody_joint_linear_spring_damping_x
        joint.use_spring_y = props.rigidbody_joint_use_linear_spring_y
        joint.spring_stiffness_y = props.rigidbody_joint_linear_spring_stiffness_y
        joint.spring_damping_y = props.rigidbody_joint_linear_spring_damping_y
        joint.use_spring_z = props.rigidbody_joint_use_linear_spring_z
        joint.spring_stiffness_z = props.rigidbody_joint_linear_spring_stiffness_z
        joint.spring_damping_z = props.rigidbody_joint_linear_spring_damping_z

    def execute(self, context: bpy.types.Object) -> Set[str]:
        self.init_collection()

        armature: bpy.types.Object = context.active_object
        selected_bones = context.selected_pose_bones
        active_bone = bpy.context.active_pose_bone

        bone_tree = BoneRelation.get_bone_tree(selected_bones, active_bone)

        def_bones: List[bpy.types.PoseBone] = []
        deco_bones: List[bpy.types.PoseBone] = []
        phys_bones: List[bpy.types.PoseBone] = []
        ctrl_bones: List[bpy.types.PoseBone] = []

        armature.data.layers = [
            layer == 0 or layer == 8 or layer == 16 for layer in range(32)
        ]
        def_bone_group = armature.pose.bone_groups.new(name="DEFORM_BONES")
        def_bone_group.color_set = "CUSTOM"
        def_bone_group.colors.normal = bpy.context.scene.yurerig.deform_bone_color
        def_bone_group.colors.select = bpy.context.scene.yurerig.deform_bone_color
        def_bone_group.colors.active = bpy.context.scene.yurerig.deform_bone_color
        ctrl_bone_group = armature.pose.bone_groups.new(name="CONTROLLER_BONES")
        ctrl_bone_group.color_set = "CUSTOM"
        ctrl_bone_group.colors.normal = bpy.context.scene.yurerig.controller_bone_color
        ctrl_bone_group.colors.select = bpy.context.scene.yurerig.controller_bone_color
        ctrl_bone_group.colors.active = bpy.context.scene.yurerig.controller_bone_color
        phys_bone_group = armature.pose.bone_groups.new(name="PHYSICS_BONES")
        phys_bone_group.color_set = "CUSTOM"
        phys_bone_group.colors.normal = bpy.context.scene.yurerig.physics_bone_color
        phys_bone_group.colors.select = bpy.context.scene.yurerig.physics_bone_color
        phys_bone_group.colors.active = bpy.context.scene.yurerig.physics_bone_color

        # Setup physics influence slider
        slider_size = context.scene.yurerig.controller_slider_size
        slider_gap = slider_size / 6 * 2

        bpy.ops.object.mode_set(mode="OBJECT")

        deco_phys_curve = bpy.data.curves.new(type="FONT", name="DECO_PHYS")
        deco_phys_curve.align_x = "CENTER"
        deco_phys_curve.align_y = "TOP"
        deco_phys_curve.size = slider_size / 6
        deco_phys = bpy.data.objects.new("DECO_PHYS", object_data=deco_phys_curve)
        deco_phys.data.body = "PHYS"
        deco_phys.location = Vector((0, 0, slider_size * 4 / 6))
        deco_phys.rotation_euler = Vector((math.radians(90), 0, 0))
        context.scene.collection.objects.link(deco_phys)
        for o in context.view_layer.objects:
            o.select_set(o == deco_phys)
        context.view_layer.objects.active = deco_phys
        bpy.ops.object.convert(target="MESH")
        context.scene.yurerig.controllers_collection.objects.link(deco_phys)

        deco_fk_curve = bpy.data.curves.new(type="FONT", name="DECO_FK")
        deco_fk_curve.align_x = "CENTER"
        deco_fk_curve.align_y = "TOP"
        deco_fk_curve.size = slider_size / 6
        deco_fk = bpy.data.objects.new("DECO_FK", object_data=deco_fk_curve)
        deco_fk.data.body = "FK"
        deco_fk.location = Vector((0, 0, -slider_size / 6))
        deco_fk.rotation_euler = Vector((math.radians(90), 0, 0))
        context.scene.collection.objects.link(deco_fk)
        for o in context.view_layer.objects:
            o.select_set(o == deco_fk)
        context.view_layer.objects.active = deco_fk
        bpy.ops.object.convert(target="MESH")
        context.scene.yurerig.controllers_collection.objects.link(deco_fk)

        context.view_layer.objects.active = armature

        bpy.ops.object.mode_set(mode="EDIT")
        i = 0
        physics_influence_slider_root_name = (
            f"DECO_physics_influence_slider_root_{i}_BoneShape"
        )
        physics_influence_slider_name = f"CTRL_physics_influence_slider_{i}_BoneShape"
        while physics_influence_slider_root_name in armature.data.bones:
            i += 1
            physics_influence_slider_root_name = (
                f"DECO_physics_influence_slider_root_{i}_BoneShape"
            )
            physics_influence_slider_name = (
                f"CTRL_physics_influence_slider_{i}_BoneShape"
            )
        physics_influence_slider_root_bone = armature.data.edit_bones.new(
            physics_influence_slider_root_name
        )
        physics_influence_slider_bone = armature.data.edit_bones.new(
            physics_influence_slider_name
        )
        physics_influence_slider_root_bone.head = Vector(
            (1, 0, (slider_size + slider_gap) * i + slider_gap)
        )
        physics_influence_slider_root_bone.tail = Vector(
            (1, 1, (slider_size + slider_gap) * i + slider_gap)
        )
        physics_influence_slider_root_bone.show_wire = True
        physics_influence_slider_bone.head = Vector(
            (1, 0, (slider_size + slider_gap) * i + slider_gap)
        )
        physics_influence_slider_bone.tail = Vector(
            (1, 1, (slider_size + slider_gap) * i + slider_gap)
        )
        physics_influence_slider_bone.show_wire = True
        physics_influence_slider_bone.use_connect = False
        physics_influence_slider_bone.parent = physics_influence_slider_root_bone

        armature.update_from_editmode()
        bpy.ops.object.mode_set(mode="POSE")

        armature.pose.bones[
            physics_influence_slider_root_name
        ].custom_shape = self.make_slider_root(
            physics_influence_slider_root_name, deco_fk, deco_phys
        )
        deco_bones.append(armature.pose.bones[physics_influence_slider_root_name])
        physics_influence_slider_pose_bone = armature.pose.bones[
            physics_influence_slider_name
        ]
        max_slider_value = slider_size * 2 / 6
        physics_influence_slider_pose_bone["Max Slider Value"] = max_slider_value
        physics_influence_slider_pose_bone.custom_shape = self.make_slider_obj(
            physics_influence_slider_name
        )
        physics_influence_slider_limit_location = (
            physics_influence_slider_pose_bone.constraints.new("LIMIT_LOCATION")
        )
        physics_influence_slider_limit_location.use_max_x = True
        physics_influence_slider_limit_location.max_x = 0
        physics_influence_slider_limit_location.use_min_x = True
        physics_influence_slider_limit_location.min_x = 0
        physics_influence_slider_limit_location.use_max_y = True
        physics_influence_slider_limit_location.max_y = 0
        physics_influence_slider_limit_location.use_min_y = True
        physics_influence_slider_limit_location.min_y = 0
        physics_influence_slider_limit_location.use_max_z = True
        physics_influence_slider_limit_location.max_z = (
            physics_influence_slider_pose_bone["Max Slider Value"]
        )
        physics_influence_slider_limit_location.use_min_z = True
        physics_influence_slider_limit_location.min_z = 0
        physics_influence_slider_limit_location.use_transform_limit = True
        physics_influence_slider_limit_location.owner_space = "LOCAL_WITH_PARENT"

        context.view_layer.objects.active = armature

        bpy.ops.object.mode_set(mode="EDIT")

        # Setup rig bones
        is_def_bone_pattern = re.compile(r"^DEF_.+")
        is_ctrl_bone_pattern = re.compile(r"^CTRL_.+")
        for rel in bone_tree:
            for child_bone in rel.children:
                if is_ctrl_bone_pattern.match(child_bone.name):
                    # Already setup
                    continue

                child_bone.bone.hide_select = True
                child_bone.bone_group = def_bone_group

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

                # Create a `PHYS_` bone
                phys_name = f"PHYS_{name[4:]}"
                if phys_name in armature.data.edit_bones:
                    phys_bone = armature.data.edit_bones[phys_name]
                else:
                    phys_bone = armature.data.edit_bones.new(phys_name)
                phys_bone.head = child_bone.head
                phys_bone.tail = child_bone.tail
                if parent_is_active_bone:
                    phys_bone.parent = armature.data.edit_bones[active_bone.name]
                else:
                    parent_phys_name = f"PHYS_{parent_name[4:]}"
                    phys_bone.parent = armature.data.edit_bones[parent_phys_name]
                phys_bone.roll = armature.data.edit_bones[name].roll
                phys_bone.use_connect = child_bone.bone.use_connect
                phys_bone.show_wire = True
                armature.update_from_editmode()
                phys_pose_bone = armature.pose.bones[phys_name]
                phys_pose_bone.bone.hide_select = True
                phys_pose_bone.bone_group = phys_bone_group
                phys_bones.append(phys_pose_bone)
                phys_bone.layers = [layer == 16 for layer in range(32)]

                # Add a PHYS_ constraint
                phys_constraint = child_bone.constraints.new("COPY_TRANSFORMS")
                phys_constraint.target = armature
                phys_constraint.subtarget = phys_name
                phys_constraint.influence = 1

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
                ctrl_pose_bone.bone_group = ctrl_bone_group
                if ctrl_pose_bone.custom_shape is None:
                    ctrl_obj = self.make_controller_object(
                        f"{ctrl_name}_ControllerBoneShape",
                        ctrl_bone.head,
                        ctrl_bone.tail,
                    )
                    ctrl_pose_bone.custom_shape = ctrl_obj
                    ctrl_pose_bone.use_custom_shape_bone_size = False
                else:
                    self.update_controller_object_radius(
                        ctrl_pose_bone.custom_shape, ctrl_bone.head, ctrl_bone.tail
                    )
                ctrl_bones.append(ctrl_pose_bone)
                ctrl_bone.layers = [layer == 8 for layer in range(32)]

                # Add a CTRL_ constraint
                ctrl_constraint = child_bone.constraints.new("COPY_TRANSFORMS")
                ctrl_constraint.target = armature
                ctrl_constraint.subtarget = ctrl_name
                ctrl_influence_driver = ctrl_constraint.driver_add("influence")
                ctrl_influence_driver.driver.type = "SCRIPTED"
                var = ctrl_influence_driver.driver.variables.new()
                var.name = "locZ"
                var.type = "TRANSFORMS"
                var.targets[0].id = armature
                var.targets[0].bone_target = physics_influence_slider_name
                var.targets[0].transform_space = "LOCAL_SPACE"
                var.targets[0].transform_type = "LOC_Z"
                ctrl_influence_driver.driver.expression = "locZ == 0"
                ctrl_influence_driver.driver.expression = (
                    f"1 - locZ / {max_slider_value}"
                )

        # Setup rigid body world
        if (
            bpy.context.scene.rigidbody_world is None
            or bpy.context.scene.rigidbody_world.collection is None
        ):
            bpy.ops.rigidbody.world_add()
            bpy.context.scene.rigidbody_world.enabled = True
            bpy.context.scene.rigidbody_world.collection = bpy.data.collections.new(
                "RigidBody Collection"
            )
            bpy.context.scene.rigidbody_world.constraints = bpy.data.collections.new(
                "RigidBody Constraint Collection"
            )

        bpy.ops.object.mode_set(mode="POSE")

        # Create Rigid Body Objects
        for rel in bone_tree:
            for child_bone in rel.children:
                if is_ctrl_bone_pattern.match(child_bone.name):
                    # Already setup
                    continue

                phys_name = f"PHYS_{child_bone.name[4:]}"
                phys_pose_bone = armature.pose.bones[phys_name]

                if rel.parent == active_bone:
                    root_name = f"RIGIDBODY_{child_bone.name[4:]}_Root"
                    if bpy.data.objects.get(root_name) is None:
                        root_obj = self.make_rigidbody_root_object(
                            root_name, child_bone.head, child_bone.tail
                        )
                        root_obj_constraint = root_obj.constraints.new("CHILD_OF")
                        root_obj_constraint.target = armature
                        root_obj_constraint.subtarget = active_bone.name
                    else:
                        self.update_rigidbody_rotation(
                            bpy.data.objects[root_name],
                            child_bone.head,
                            child_bone.tail,
                        )

                name = f"RIGIDBODY_{child_bone.name[4:]}"
                if bpy.data.objects.get(name) is None:
                    obj = self.make_rigidbody_object(
                        name, child_bone.head, child_bone.tail
                    )
                else:
                    obj = bpy.data.objects[name]
                    self.update_rigidbody_rotation(
                        obj,
                        child_bone.head,
                        child_bone.tail,
                    )

                if phys_pose_bone.custom_shape is None:
                    phys_pose_bone.custom_shape = self.make_phys_bone_object(
                        f"{name}_BoneShape", child_bone.head, child_bone.tail
                    )
                    phys_pose_bone.use_custom_shape_bone_size = False

                phys_constraint = phys_pose_bone.constraints.new("COPY_ROTATION")
                phys_constraint.target = obj

        # Create Rigid Body Joints
        for rel in bone_tree:
            if rel.parent == active_bone:
                for child_bone in rel.children:
                    root_obj_name = f"RIGIDBODY_{child_bone.name[4:]}_Root"
                    name = f"RIGIDBODY_{child_bone.name[4:]}"
                    joint_name = f"RIGIDBODY_JOINT_{child_bone.name[4:]}"
                    joint_obj = bpy.data.objects.new(joint_name, None)
                    joint_obj.location = child_bone.head
                    bpy.context.scene.rigidbody_world.constraints.objects.link(
                        joint_obj
                    )
                    joint_obj.rigid_body_constraint.type = "GENERIC_SPRING"
                    joint_obj.rigid_body_constraint.object1 = bpy.data.objects[
                        root_obj_name
                    ]
                    joint_obj.rigid_body_constraint.object2 = bpy.data.objects[name]
                    self.set_joint_properties(joint_obj.rigid_body_constraint)
                    bpy.context.scene.yurerig.joints_collection.objects.link(joint_obj)
            else:
                for child_bone in rel.children:
                    parent_obj_name = f"RIGIDBODY_{rel.parent.name[4:]}"
                    child_obj_name = f"RIGIDBODY_{child_bone.name[4:]}"
                    joint_name = (
                        f"RIGIDBODY_JOINT_{rel.parent.name[4:]}_{child_bone.name[4:]}"
                    )
                    joint_obj = bpy.data.objects.new(joint_name, None)
                    joint_obj.location = (rel.parent.tail + child_bone.head) / 2
                    bpy.context.scene.rigidbody_world.constraints.objects.link(
                        joint_obj
                    )
                    joint_obj.rigid_body_constraint.type = "GENERIC_SPRING"
                    joint_obj.rigid_body_constraint.object1 = bpy.data.objects[
                        parent_obj_name
                    ]
                    joint_obj.rigid_body_constraint.object2 = bpy.data.objects[
                        child_obj_name
                    ]
                    self.set_joint_properties(joint_obj.rigid_body_constraint)
                    bpy.context.scene.yurerig.joints_collection.objects.link(joint_obj)
        # Create Rigid Body Reset Goal Objects
        for rel in bone_tree:
            for child_bone in rel.children:
                if is_ctrl_bone_pattern.match(child_bone.name):
                    # Already setup
                    continue

                phys_name = f"PHYS_{child_bone.name[4:]}"
                phys_pose_bone = armature.pose.bones[phys_name]

                name = f"RIGIDBODY_GOAL_{child_bone.name[4:]}"
                if bpy.data.objects.get(name) is None:
                    obj = self.make_rigidbody_reset_goal_object(
                        name,
                        child_bone.head,
                        child_bone.tail,
                        physics_influence_slider_name,
                        armature,
                        bpy.data.objects[f"RIGIDBODY_{child_bone.name[4:]}"],
                    )
                else:
                    obj = bpy.data.objects[name]
                    self.update_rigidbody_rotation(
                        obj,
                        child_bone.head,
                        child_bone.tail,
                    )

        # SET DECO_, CTRL_ and PHYS_ bone not use deform
        for b in deco_bones:
            b.bone.use_deform = False
        for b in ctrl_bones:
            b.bone.use_deform = False
        for b in phys_bones:
            b.bone.use_deform = False

        # Set DEF_, DECO_ and PHYS_ bone non selectable
        for b in def_bones:
            b.bone.hide_select = True
        for b in deco_bones:
            b.bone.hide_select = True
        for b in phys_bones:
            b.bone.hide_select = True

        # Select CTRL_ bones
        for b in armature.data.bones:
            b.select = False
        for b in ctrl_bones:
            b.bone.select = True
        armature.data.bones.active = active_bone.bone

        return {"FINISHED"}


class YURERIG_OT_RemoveOperator(bpy.types.Operator):
    """
    Setup DEF_ bones, CTRL_ bones and PHYS_ bones, add rigidbody objects and
    generic joints, add controller for turn on physics.
    """

    bl_idname = "orito_itsuki.yurerig_remove"
    bl_label = "Remove Yure Rig"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        obj: bpy.types.Object = context.active_object
        flag: bool = obj and obj.type == "ARMATURE" and obj.mode == "POSE"
        return flag

    def execute(self, context: bpy.types.Context) -> Set[str]:
        props = context.scene.yurerig
        armature: bpy.types.Object = context.active_object

        is_def_bone_pattern = re.compile(r"^DEF_.+")
        is_ctrl_bone_pattern = re.compile(r"^CTRL_.+")
        is_deco_bone_pattern = re.compile(r"^DECO_.+")
        is_phys_bone_pattern = re.compile(r"^PHYS_.+")

        is_rigidbody_joint_pattern = re.compile(r"^RIGIDBODY_JOINT_.+")
        is_rigidbody_pattern = re.compile(r"^RIGIDBODY_.+")
        is_rigidbody_goal_pattern = re.compile(r"^RIGIDBODY_GOAL_.+")
        is_controller_boneshape = re.compile(r".+BoneShape$")

        bpy.ops.object.mode_set(mode="EDIT")

        armature.pose.bone_groups.remove(armature.pose.bone_groups["DEFORM_BONES"])
        armature.pose.bone_groups.remove(armature.pose.bone_groups["CONTROLLER_BONES"])
        armature.pose.bone_groups.remove(armature.pose.bone_groups["PHYSICS_BONES"])

        for b in armature.pose.bones:
            if is_def_bone_pattern.match(b.name):
                b.bone_group = None
                b.constraints.remove(b.constraints[0])
                for d in armature.animation_data.drivers:
                    if b.name in d.data_path:
                        armature.animation_data.drivers.remove(d)
                b.constraints.remove(b.constraints[0])

        for b in armature.data.edit_bones:
            if (
                is_ctrl_bone_pattern.match(b.name)
                or is_phys_bone_pattern.match(b.name)
                or is_deco_bone_pattern.match(b.name)
            ):
                armature.data.edit_bones.remove(b)

        for obj in props.joints_collection.objects:
            if is_rigidbody_joint_pattern.match(obj.name):
                bpy.data.objects.remove(obj)

        for obj in props.rigidbodies_collection.objects:
            if is_rigidbody_pattern.match(obj.name):
                bpy.data.objects.remove(obj)

        for obj in props.rigidbodies_reset_goal_collection.objects:
            if is_rigidbody_goal_pattern.match(obj.name):
                bpy.data.objects.remove(obj)

        for obj in props.controllers_collection.objects:
            if is_controller_boneshape.match(obj.name):
                bpy.data.objects.remove(obj)

        bpy.ops.object.mode_set(mode="POSE")

        for b in armature.pose.bones:
            if is_def_bone_pattern.match(b.name):
                b.bone.hide_select = False

        if len(props.joints_collection.all_objects) == 0:
            bpy.data.collections.remove(props.joints_collection)

        if len(props.rigidbodies_collection.all_objects) == 0:
            bpy.data.collections.remove(props.rigidbodies_collection)

        if len(props.rigidbodies_reset_goal_collection.all_objects) == 0:
            bpy.data.collections.remove(props.rigidbodies_reset_goal_collection)

        if len(props.controllers_collection.all_objects) == 0:
            bpy.data.collections.remove(props.controllers_collection)

        if len(props.root_collection.all_objects) == 0:
            bpy.data.collections.remove(props.root_collection)

        return {"FINISHED"}
