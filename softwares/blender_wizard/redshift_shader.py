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
        output_node.location = [280.0, 0.0]
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

def get_textures_dic(files_list):
    textures_dic = dict()
    for file in files_list:
        file = file.replace('\\', '/')
        if 'COLOR' in file.upper():
            textures_dic['diffuse'] = bpy.data.images.load(file)
            textures_dic['diffuse'].source = 'TILED'
        if 'ROUGHNESS' in file.upper():
            textures_dic['roughness'] = bpy.data.images.load(file)
            textures_dic['roughness'].source = 'TILED'
        if 'METALNESS' in file.upper():
            textures_dic['metalness'] = bpy.data.images.load(file)
            textures_dic['metalness'].source = 'TILED'
        if 'NORMAL' in file.upper():
            textures_dic['normal_map'] = bpy.data.images.load(file)
            textures_dic['normal_map'].source = 'TILED'
    return textures_dic

def plug_textures(namespace, files_list, update=None):
    material = get_redshift_material(namespace, update)
    if material:
        textures_dic = get_textures_dic(files_list)
        # Plug diffuse
        diffuse_texture_node = material.node_tree.nodes['Wizard Redshift Diffuse Texture']
        diffuse_texture_node.inputs[2].default_value = textures_dic['diffuse']
        # Plug roughness
        roughness_texture_node = material.node_tree.nodes['Wizard Redshift Roughness Texture']
        roughness_texture_node.inputs[2].default_value = textures_dic['roughness']
        # Plug metalness
        metallic_texture_node = material.node_tree.nodes['Wizard Redshift Metallic Texture']
        metallic_texture_node.inputs[2].default_value = textures_dic['metalness']
        # Plug normal
        normal_map_node = material.node_tree.nodes['Wizard Redshift Normal Map']
        normal_map_node.inputs[2].default_value = textures_dic['normal_map']
