# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os

# Blender modules
import bpy

# Create a Material:
def get_redshift_material(mat_name, update):
    if(mat_name not in bpy.data.materials) and (not update):
        material = bpy.data.materials.new(mat_name)
        material.use_nodes = True
        nt = material.node_tree
        #nt.nodes['Principled BSDF'].inputs['Base Color'].default_value = (mat_color)
        nt.nodes.remove(nt.nodes['Principled BSDF'])
        nt.nodes.remove(nt.nodes['Material Output'])
        # Create material node
        material_node = nt.nodes.new('rsMaterialShaderNode')
        material_node.name = "Wizard Redshift Material"
        # Setting Fresnel type to Metalness
        material_node.inputs[17].default_value = '2'
        material_node.inputs[0].default_value = False
        material_node.inputs[82].default_value = False
        # Create material output node
        output_node = nt.nodes.new('RedshiftMaterialOutputNode')
        output_node.name = "Wizard Redshift Material Output"
        output_node.location = [900.0000, 0.0000]
        # Link material to output
        nt.links.new(material_node.outputs['outColor'], output_node.inputs['Surface'])
        # Create Diffuse texture node
        diffuse_texture_node = nt.nodes.new('rsTextureSamplerShaderNode')
        diffuse_texture_node.inputs[0].default_value = False
        diffuse_texture_node.inputs[1].default_value = False
        diffuse_texture_node.location = [-340.0, 0.0]
        diffuse_texture_node.name = "Wizard Redshift Diffuse Texture"
        nt.links.new(diffuse_texture_node.outputs['outColor'], get_input(material_node, "diffuse_color"))
        # Create Rougness texture node
        roughness_texture_node = nt.nodes.new('rsTextureSamplerShaderNode')
        roughness_texture_node.inputs[0].default_value = False
        roughness_texture_node.inputs[1].default_value = False
        roughness_texture_node.location = [-340.0, -220.0]
        roughness_texture_node.name = "Wizard Redshift Roughness Texture"
        nt.links.new(roughness_texture_node.outputs['outColor'], get_input(material_node, "refl_roughness"))
        # Create Metallic texture node
        metallic_texture_node = nt.nodes.new('rsTextureSamplerShaderNode')
        metallic_texture_node.inputs[0].default_value = False
        metallic_texture_node.inputs[1].default_value = False
        metallic_texture_node.location = [-340.0, -440.0]
        metallic_texture_node.name = "Wizard Redshift Metallic Texture"
        nt.links.new(metallic_texture_node.outputs['outColor'], get_input(material_node, "refl_metalness"))
        # Create Normal map node
        normal_map_node = nt.nodes.new('rsNormalMapShaderNode')
        normal_map_node.inputs[0].default_value = False
        normal_map_node.inputs[1].default_value = False
        normal_map_node.location = [-340.0, -660.0]
        normal_map_node.name = "Wizard Redshift Normal Map"
        nt.links.new(normal_map_node.outputs['outDisplacementVector'], get_input(material_node, "bump_input"))
        # Create Displacement shader
        displacement_material_node = nt.nodes.new('rsDisplacementShaderNode')
        displacement_material_node.name = "Wizard Redshift Displacement Material"
        displacement_material_node.inputs[3].default_value = '2'
        displacement_material_node.inputs[11].default_value = 0.5
        displacement_material_node.location = [600.0000, -60.0000]
        nt.links.new(get_output(displacement_material_node, 'outDisplacementVector'), output_node.inputs['Displacement'])
        # Create Height texture node
        height_texture_node = nt.nodes.new('rsTextureSamplerShaderNode')
        height_texture_node.inputs[0].default_value = False
        height_texture_node.inputs[1].default_value = False
        height_texture_node.location = [280.0000, -60.0000]
        height_texture_node.name = "Wizard Redshift Height Texture"
        nt.links.new(height_texture_node.outputs['outColor'], get_input(displacement_material_node, "texMap"))

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
        if 'METALNESS' in file.upper():
            metalness_maps.append(file)
        if 'NORMAL' in file.upper():
            normal_maps.append(file)
        if 'HEIGHT' in file.upper():
            height_maps.append(file)

    if len(diffuse_maps) >=1:
        textures_dic['diffuse'] = bpy.data.images.load(diffuse_maps[0])
        if len(diffuse_maps) >1:
            textures_dic['diffuse'].source = 'TILED'
    else:
        textures_dic['diffuse'] = None

    if len(roughness_maps) >=1:
        textures_dic['roughness'] = bpy.data.images.load(roughness_maps[0])
        if len(diffuse_maps) >1:
            textures_dic['roughness'].source = 'TILED'
    else:
        textures_dic['roughness'] = None

    if len(metalness_maps) >=1:
        textures_dic['metalness'] = bpy.data.images.load(metalness_maps[0])
        if len(diffuse_maps) >1:
            textures_dic['metalness'].source = 'TILED'
    else:
        textures_dic['metalness'] = None

    if len(normal_maps) >=1:
        textures_dic['normal_map'] = bpy.data.images.load(normal_maps[0])
        if len(normal_maps) >1:
            textures_dic['normal_map'].source = 'TILED'
    else:
        textures_dic['normal_map'] = None

    if len(height_maps) >=1:
        textures_dic['height_map'] = bpy.data.images.load(height_maps[0])
        if len(height_maps) >1:
            textures_dic['height_map'].source = 'TILED'
    else:
        textures_dic['height_map'] = None

    return textures_dic

def plug_textures(namespace, files_list, update=None):
    material = get_redshift_material(namespace, update)
    if material:
        textures_dic = get_textures_dic(files_list)
        # Plug diffuse
        if textures_dic['diffuse']:
            diffuse_texture_node = material.node_tree.nodes['Wizard Redshift Diffuse Texture']
            diffuse_texture_node.inputs[2].default_value = textures_dic['diffuse']
        # Plug roughness
        if textures_dic['roughness']:
            roughness_texture_node = material.node_tree.nodes['Wizard Redshift Roughness Texture']
            roughness_texture_node.inputs[2].default_value = textures_dic['roughness']
        # Plug metalness
        if textures_dic['metalness']:
            metallic_texture_node = material.node_tree.nodes['Wizard Redshift Metallic Texture']
            metallic_texture_node.inputs[2].default_value = textures_dic['metalness']
        # Plug normal
        if textures_dic['normal_map']:
            normal_map_node = material.node_tree.nodes['Wizard Redshift Normal Map']
            normal_map_node.inputs[2].default_value = textures_dic['normal_map']
        # PLug height
        if textures_dic['height_map']:
            height_texture_node = material.node_tree.nodes['Wizard Redshift Height Texture']
            height_texture_node.inputs[2].default_value = textures_dic['height_map']