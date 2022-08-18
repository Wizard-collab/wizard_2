# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os

# Guerilla modules
from guerilla import Document, Modifier, pynode, Node, Plug

# Wizard modules
from guerilla_render_wizard import wizard_tools
from guerilla_render_wizard import wizard_reference

def update_texturing(namespace, files_list, asset_name, referenced_string_asset):
    old_objects = wizard_tools.get_all_nodes()
    if namespace in wizard_tools.get_all_nodes():
        plug_texturing(namespace, files_list, asset_name, update=True)
        wizard_reference.trigger_after_reference_hook('texturing',
                                    files_list,
                                    namespace,
                                    wizard_tools.get_new_objects(old_objects),
                                    referenced_string_asset)

def import_texturing(namespace, files_list, asset_name, referenced_string_asset):
    old_objects = wizard_tools.get_all_nodes()
    if namespace not in wizard_tools.get_all_nodes():
        plug_texturing(namespace, files_list, asset_name, update=False)
        wizard_reference.trigger_after_reference_hook('texturing',
                                        files_list,
                                        namespace,
                                        wizard_tools.get_new_objects(old_objects),
                                        referenced_string_asset)

def plug_texturing(namespace, files_list, asset_name, update=False):
    render_graph, material_override_node, surface_node, displacement_node = get_shader(namespace, asset_name)
    textures_dic = get_textures_dic(files_list)

    # Plug diffuse
    if textures_dic['diffuse']:
        #plug = get_plug(surface_node, 'DiffuseColor', 'string')
        plug = get_plug(material_override_node, 'diffusecolor', dataType='string')
        plug.set(textures_dic['diffuse'])

        attribute = get_attribute(surface_node, 'DiffuseColor', 'Texture', [('Gamma', 'linear')])
        set_file(attribute, '<attr:diffusecolor>')

    # Plug metallic
    if textures_dic['diffuse'] and textures_dic['metalness'] and textures_dic['roughness']:

        plug = get_plug(material_override_node, 'metal', dataType='string')
        plug.set(textures_dic['metalness'])

        plug = get_plug(material_override_node, 'roughness', dataType='string')
        plug.set(textures_dic['roughness'])

        # Metal color
        attribute = get_attribute(surface_node, 'MetalColor', 'Texture', [('Gamma', 'linear')])
        set_file(attribute, '<attr:diffusecolor>')
        # Metal amount
        attribute = get_attribute(surface_node, 'Metal', 'MaskTexture', [('Gamma', 'data')])
        set_file(attribute, '<attr:metal>')
        # Metal rougness
        attribute = get_attribute(surface_node, 'MetalRoughness', 'MaskTexture', [('Gamma', 'data')])
        set_file(attribute, '<attr:roughness>')

    # Plug roughness
    if textures_dic['roughness']:
        if not update:
            surface_node.overrideinheritedattr('Spec1',1)
        attribute = get_attribute(surface_node, 'Spec1Roughness', 'MaskTexture', [('Gamma', 'data')])
        set_file(attribute, '<attr:roughness>')

    # Plug normal map
    if textures_dic['normal_map']:
        plug = get_plug(material_override_node, 'normal', dataType='string')
        plug.set(textures_dic['normal_map'])

        attribute = get_attribute(surface_node, 'Normal', 'NormalMap', [('Gamma', 'data')])
        set_file(attribute, '<attr:normal>')

    # Plug height
    if textures_dic['height_map']:
        if not update:
            displacement_node.overrideinheritedattr('Normalization',"Affine")
            displacement_node.overrideinheritedattr('Offset',0)
            displacement_node.overrideinheritedattr('Multiplier', 0.02)
            displacement_node.overrideinheritedattr("RaytraceDisplacement", 0.02)
            displacement_node.overrideinheritedattr("DisplaceAmount", 1)
            displacement_node.overrideinheritedattr('RaytraceDisplacement', 2)
            displacement_node.State.set("bypass")

        plug = get_plug(material_override_node, 'height', dataType='string')
        plug.set(textures_dic['height_map'])

        attribute = get_attribute(displacement_node, 'Amount', 'MaskTexture', [('Gamma', 'data')])
        set_file(attribute, '<attr:height>')

def set_file(attribute, file):
    with Modifier() as mod:
        # Force file reload by deleting the plug
        #plug = get_plug(attribute, 'File')
        #plug.delete()
        plug = get_plug(attribute, 'File')
        plug.set(file)

def create_shader(namespace, asset_name):
    shaders_GRP = wizard_tools.add_GRP('SHADERS')

    render_graph = Node.create(namespace, 'RenderGraph')
    render_graph.move(shaders_GRP)

    tag_node = render_graph.loadfile('$(LIBRARY)/rendergraph/tag.gnode')[0]
    asset_tag = "{0}_{1}".format(os.environ['wizard_category_name'], os.environ['wizard_asset_name'])
    tag_node.Tag.set(asset_tag)
    tag_node.rename(asset_tag)

    attribute_node = render_graph.loadfile('$(LIBRARY)/rendergraph/attributes.gnode')[0]
    attribute_node.overrideinheritedattr('RaytraceSubdivLevel',2)
    attribute_node.overrideinheritedattr('Subdiv', True)
    attribute_node.Input1.Plug.connect(tag_node.Output1.Plug)

    material_override_node = render_graph.loadfile('$(LIBRARY)/rendergraph/materialoverride.gnode')[0]
    material_override_node.rename('{0}_materialoverride'.format(asset_name))
    material_override_node.Input1.Plug.connect(attribute_node.Output1.Plug)

    displacement_node = render_graph.loadfile('$(LIBRARY)/rendergraph/shader.gnode')[0]
    displacement_node.Shader.set('Displacement')
    displacement_node.Mode.set('displacement')
    displacement_node.rename('{0}_displacement_shader'.format(asset_name))
    displacement_node.Input1.Plug.connect(material_override_node.Output1.Plug)

    surface_node = render_graph.loadfile('$(LIBRARY)/rendergraph/shader.gnode')[0]
    surface_node.Shader.set('Surface2')
    surface_node.Mode.set('surface')
    surface_node.rename('{0}_main_shader'.format(asset_name))
    surface_node.Input1.Plug.connect(displacement_node.Output1.Plug)

    out_node = render_graph.loadfile('$(LIBRARY)/rendergraph/output.gnode')[0]
    out_node.Input1.Plug.connect(surface_node.Output1.Plug)

    return render_graph, material_override_node, surface_node, displacement_node

def get_shader(namespace, asset_name):
    if namespace not in wizard_tools.get_all_nodes():
        render_graph, material_override_node, surface_node, displacement_node = create_shader(namespace, asset_name)
    else: 
        render_graph = wizard_tools.get_node_from_name(namespace)
        material_override_node = wizard_tools.get_node_from_name('{0}_materialoverride'.format(asset_name))
        surface_node = wizard_tools.get_node_from_name('{0}_main_shader'.format(asset_name))
        displacement_node = wizard_tools.get_node_from_name('{0}_displacement_shader'.format(asset_name))
    return render_graph, material_override_node, surface_node, displacement_node

def create_attribute(node, attribute_name, map_type, attrs=[], type='AttributeShader'):
    with Modifier() as mod:
        attribute = mod.createnode(attribute_name, type='AttributeShader', parent=node)
        attribute.Shader.set(map_type)
        for attr in attrs:
            attribute.overrideinheritedattr(attr[0],attr[1])
    return attribute

def create_plug(attribute, plug_name, dataType='texture'):
    plug = attribute.createplug(plug_name, 'user', dataType, Plug.Dynamic)
    return plug

def get_attribute(node, attribute_name, map_type, attrs=[], type='AttributeShader'):
    attribute = None
    for child in node.children():
        if child.name == attribute_name:
            attribute = child
            break
    if not attribute:
        attribute = create_attribute(node,
                                        attribute_name,
                                        map_type,
                                        attrs,
                                        type)
    return attribute

def get_plug(attribute, plug_name, dataType='texture'):
    plug = None
    if attribute.hasPlug(plug_name):
        plug = attribute.findchild(".{0}".format(plug_name))
    if plug is None:
        plug = create_plug(attribute, plug_name, dataType)
    return plug

def get_udim_path(path):
    items = path.split('.')
    extension = items.pop(-1)
    try:
        int(items[-1])
        items.pop(-1)
        path = ('.').join(items + ['%d', extension])
    except:
        path = ('.').join(items + [extension])
    return path

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
        texture = get_udim_path(diffuse_maps[0])
        textures_dic['diffuse'] = texture
    else:
        textures_dic['diffuse'] = None

    if len(roughness_maps) >=1:
        texture = get_udim_path(roughness_maps[0])
        textures_dic['roughness'] = texture
    else:
        textures_dic['roughness'] = None

    if len(metalness_maps) >=1:
        texture = get_udim_path(metalness_maps[0])
        textures_dic['metalness'] = texture
    else:
        textures_dic['metalness'] = None

    if len(normal_maps) >=1:
        texture = get_udim_path(normal_maps[0])
        textures_dic['normal_map'] = texture
    else:
        textures_dic['normal_map'] = None

    if len(height_maps) >=1:
        texture = get_udim_path(height_maps[0])
        textures_dic['height_map'] = texture
    else:
        textures_dic['height_map'] = None

    return textures_dic
