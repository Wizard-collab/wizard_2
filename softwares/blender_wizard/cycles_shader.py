# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os

# Blender modules
import bpy

# Create a Material:
def get_blender_material(mat_name, update):
    if(mat_name not in bpy.data.materials) and (not update):
        material = bpy.data.materials.new(mat_name)
        material.use_nodes = True
        nt = material.node_tree

        BSDF_node = nt.nodes['Principled BSDF']
        output_node = nt.nodes['Material Output']
        output_node.location = [720.0, 300.0]

        diffuse_texture_node = nt.nodes.new('ShaderNodeTexImage')
        nt.links.new(get_output(diffuse_texture_node, 'Color'), get_input(BSDF_node, "Base Color"))
        diffuse_texture_node.location = [-340.0, 300.0]
        diffuse_texture_node.name = "Wizard Diffuse Texture"

        roughness_texture_node = nt.nodes.new('ShaderNodeTexImage')
        nt.links.new(get_output(roughness_texture_node, 'Color'), get_input(BSDF_node, "Roughness"))
        roughness_texture_node.location = [-340.0, 0.0]
        roughness_texture_node.name = "Wizard Roughness Texture"

        metallic_texture_node = nt.nodes.new('ShaderNodeTexImage')
        nt.links.new(get_output(metallic_texture_node, 'Color'), get_input(BSDF_node, "Metallic"))
        metallic_texture_node.location = [-340.0, -300.0]
        metallic_texture_node.name = "Wizard Metallic Texture"

        normal_map_node = nt.nodes.new('ShaderNodeNormalMap')
        nt.links.new(get_output(normal_map_node, 'Normal'), get_input(BSDF_node, "Normal"))
        normal_map_node.location = [-340.0, -600.0]
        normal_map_node.name = "Wizard Normal Map"

        normal_texture_node = nt.nodes.new('ShaderNodeTexImage')
        nt.links.new(get_output(normal_texture_node, 'Color'), get_input(normal_map_node, "Color"))
        normal_texture_node.location = [-650.0, -600.0]
        normal_texture_node.name = "Wizard Normal Texture"

        displacement_node = nt.nodes.new('ShaderNodeDisplacement')
        nt.links.new(get_output(displacement_node, 'Displacement'), get_input(output_node, "Displacement"))
        displacement_node.location = [540.0, 200.0]
        displacement_node.name = "Wizard Displacement"

        displacement_texture_node = nt.nodes.new('ShaderNodeTexImage')
        nt.links.new(get_output(displacement_texture_node, 'Color'), get_input(displacement_node, "Height"))
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

def get_textures_dic(files_list):
    textures_dic = dict()

    diffuse_maps = []
    roughness_maps = []
    metalness_maps = []
    normal_maps = []
    height_maps = []

    for file in files_list:
        file = file.replace('\\', '/')
        if 'COLOR' in file.upper():
            diffuse_maps.append(file)
        if 'ROUGHNESS' in file.upper():
            roughness_maps.append(file)
        if 'METAL' in file.upper():
            metalness_maps.append(file)
        if 'NORMAL' in file.upper():
            normal_maps.append(file)
        if 'HEIGHT' in file.upper():
            height_maps.append(file)

    if len(diffuse_maps) >=1:
        if 'diffuse_maps' in bpy.data.images:
            bpy.data.images.remove(bpy.data.images['diffuse_maps'])
        bpy.ops.image.open(filepath=diffuse_maps[0], directory=os.path.dirname(diffuse_maps[0]), use_udim_detecting=True)
        image = find_image(os.path.basename(diffuse_maps[0]))
        if image:
            image.name = 'diffuse_maps'
            textures_dic['diffuse'] = image
        else:
            textures_dic['diffuse'] = None
    else:
        textures_dic['diffuse'] = None

    if len(roughness_maps) >=1:
        if 'roughness_maps' in bpy.data.images:
            bpy.data.images.remove(bpy.data.images['roughness_maps'])
        bpy.ops.image.open(filepath=roughness_maps[0], directory=os.path.dirname(roughness_maps[0]), use_udim_detecting=True)
        image = find_image(os.path.basename(roughness_maps[0]))
        if image:
            image.name = 'roughness_maps'
            textures_dic['roughness'] = image
        else:
            textures_dic['roughness'] = None
    else:
        textures_dic['roughness'] = None

    if len(metalness_maps) >=1:
        if 'metalness_maps' in bpy.data.images:
            bpy.data.images.remove(bpy.data.images['metalness_maps'])
        bpy.ops.image.open(filepath=metalness_maps[0], directory=os.path.dirname(metalness_maps[0]), use_udim_detecting=True)
        image = find_image(os.path.basename(metalness_maps[0]))
        if image:
            image.name = 'metalness_maps'
            textures_dic['metalness'] = image
        else:
            textures_dic['metalness'] = None
    else:
        textures_dic['metalness'] = None

    if len(normal_maps) >=1:
        if 'normal_maps' in bpy.data.images:
            bpy.data.images.remove(bpy.data.images['normal_maps'])
        bpy.ops.image.open(filepath=normal_maps[0], directory=os.path.dirname(normal_maps[0]), use_udim_detecting=True)
        image = find_image(os.path.basename(normal_maps[0]))
        if image:
            image.name = 'normal_maps'
            textures_dic['normal_map'] = image
        else:
            textures_dic['normal_map'] = None
    else:
        textures_dic['normal_map'] = None

    if len(height_maps) >=1:
        if 'height_maps' in bpy.data.images:
            bpy.data.images.remove(bpy.data.images['height_maps'])
        bpy.ops.image.open(filepath=height_maps[0], directory=os.path.dirname(height_maps[0]), use_udim_detecting=True)
        image = find_image(os.path.basename(height_maps[0]))
        if image:
            image.name = 'height_maps'
            textures_dic['height_map'] = image
        else:
            textures_dic['height_map'] = None
    else:
        textures_dic['height_map'] = None

    return textures_dic

def plug_textures(namespace, files_list, update=None):
    material = get_blender_material(namespace, update)

    if material:
        textures_dic = get_textures_dic(files_list)
        # Plug diffuse
        if textures_dic['diffuse']:
            diffuse_texture_node = material.node_tree.nodes['Wizard Diffuse Texture']
            diffuse_texture_node.image = textures_dic['diffuse']
        # Plug roughness
        if textures_dic['roughness']:
            roughness_texture_node = material.node_tree.nodes['Wizard Roughness Texture']
            roughness_texture_node.image = textures_dic['roughness']
        # Plug metalness
        if textures_dic['metalness']:
            metallic_texture_node = material.node_tree.nodes['Wizard Metallic Texture']
            metallic_texture_node.image = textures_dic['metalness']
        # Plug normal
        if textures_dic['normal_map']:
            normal_map_node = material.node_tree.nodes['Wizard Normal Texture']
            normal_map_node.image = textures_dic['normal_map']
        # Plug displacement
        if textures_dic['height_map']:
            displacement_texture_node = material.node_tree.nodes['Wizard Displacement Texture']
            displacement_texture_node.image = textures_dic['height_map']
