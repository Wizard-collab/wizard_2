# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os

# Blender modules
import bpy


def get_blender_material(mat_name, update):
    if (mat_name not in bpy.data.materials) and (not update):
        material = bpy.data.materials.new(mat_name)
        material.use_nodes = True
        nt = material.node_tree

        BSDF_node = nt.nodes['Principled BSDF']
        output_node = nt.nodes['Material Output']
        output_node.location = [720.0, 300.0]

        diffuse_texture_node = nt.nodes.new('ShaderNodeTexImage')
        nt.links.new(get_output(diffuse_texture_node, 'Color'),
                     get_input(BSDF_node, "Base Color"))
        diffuse_texture_node.location = [-340.0, 300.0]
        diffuse_texture_node.name = "Wizard Diffuse Texture"

        roughness_texture_node = nt.nodes.new('ShaderNodeTexImage')
        nt.links.new(get_output(roughness_texture_node, 'Color'),
                     get_input(BSDF_node, "Roughness"))
        roughness_texture_node.location = [-340.0, 0.0]
        roughness_texture_node.name = "Wizard Roughness Texture"

        metallic_texture_node = nt.nodes.new('ShaderNodeTexImage')
        nt.links.new(get_output(metallic_texture_node, 'Color'),
                     get_input(BSDF_node, "Metallic"))
        metallic_texture_node.location = [-340.0, -300.0]
        metallic_texture_node.name = "Wizard Metallic Texture"

        normal_map_node = nt.nodes.new('ShaderNodeNormalMap')
        nt.links.new(get_output(normal_map_node, 'Normal'),
                     get_input(BSDF_node, "Normal"))
        normal_map_node.location = [-340.0, -600.0]
        normal_map_node.name = "Wizard Normal Map"

        normal_texture_node = nt.nodes.new('ShaderNodeTexImage')
        nt.links.new(get_output(normal_texture_node, 'Color'),
                     get_input(normal_map_node, "Color"))
        normal_texture_node.location = [-650.0, -600.0]
        normal_texture_node.name = "Wizard Normal Texture"

        displacement_node = nt.nodes.new('ShaderNodeDisplacement')
        nt.links.new(get_output(displacement_node, 'Displacement'),
                     get_input(output_node, "Displacement"))
        displacement_node.location = [540.0, 200.0]
        displacement_node.inputs[1].default_value = 0.0
        displacement_node.inputs[2].default_value = 0.01
        displacement_node.name = "Wizard Displacement"
        material.displacement_method = 'BOTH'

        displacement_texture_node = nt.nodes.new('ShaderNodeTexImage')
        nt.links.new(get_output(displacement_texture_node, 'Color'),
                     get_input(displacement_node, "Height"))
        displacement_texture_node.location = [280.0, 200.0]
        displacement_texture_node.name = "Wizard Displacement Texture"

    elif (mat_name in bpy.data.materials) and update:
        material = bpy.data.materials[mat_name]
    else:
        material = None
    return material


def get_input(node, socket_identifier):
    for input in node.inputs:
        if input.identifier == socket_identifier:
            break
    return input


def get_output(node, socket_identifier):
    for output in node.outputs:
        if output.identifier == socket_identifier:
            break
    return output


def find_image(full_name):
    for image_name in bpy.data.images.keys():
        if full_name.split('.')[0] in image_name:
            return bpy.data.images[image_name]


def get_textures_dic(files_list, namespace):
    textures_dic = {}

    for file in files_list:
        file = file.replace('\\', '/')
        type = os.path.basename(file).split('.')[0]
        if type not in textures_dic.keys():
            textures_dic[type] = []
        textures_dic[type].append(file)

    for type, maps in textures_dic.items():
        if len(maps) >= 1:

            image_name = f'{namespace}:{type}_maps'

            nodes_with_image = []
            if image_name in bpy.data.images:
                nodes_with_image = get_nodes_with_image(image_name)
                bpy.data.images.remove(
                    bpy.data.images[image_name])

            bpy.ops.image.open(filepath=maps[0], directory=os.path.dirname(
                maps[0]), use_udim_detecting=True, relative_path=False)

            image = find_image(os.path.basename(maps[0]))

            if image:
                image.name = image_name
                textures_dic[type] = image
                reassign_image_to_nodes(nodes_with_image, image)
            else:
                textures_dic[type] = None

        else:
            textures_dic[type] = None

    return textures_dic


def get_nodes_with_image(image_name):
    nodes_using_image = []
    for material in bpy.data.materials:
        if material.use_nodes:
            for node in material.node_tree.nodes:
                if node.type == 'TEX_IMAGE' and node.image and node.image.name == image_name:
                    nodes_using_image.append(node)
    return nodes_using_image


def reassign_image_to_nodes(nodes, image):
    for node in nodes:
        node.image = image


def reload_textures(namespace, files_list, update=None):
    textures_dic = get_textures_dic(files_list, namespace)


def plug_textures(namespace, files_list, update=None):
    material = get_blender_material(namespace, update)

    if material:
        textures_dic = get_textures_dic(files_list, namespace)
        for type, maps in textures_dic.items():
            image_node = None
            if "BASECOLOR" in type.upper():
                image_node = material.node_tree.nodes['Wizard Diffuse Texture']
            if "ROUGHNESS" in type.upper() and "SHEEN" not in type.upper():
                image_node = material.node_tree.nodes['Wizard Roughness Texture']
            if "METAL" in type.upper():
                image_node = material.node_tree.nodes['Wizard Metallic Texture']
            if "NORMAL" in type.upper():
                image_node = material.node_tree.nodes['Wizard Normal Texture']
            if "HEIGHT" in type.upper():
                image_node = material.node_tree.nodes['Wizard Displacement Texture']
            if not image_node:
                continue
            image_node.image = maps
