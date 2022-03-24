# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Guerilla modules
from guerilla import Document, Modifier, pynode, Node, Plug

# Wizard modules
from guerilla_render_wizard import wizard_tools
from guerilla_render_wizard import wizard_reference

def update_texturing(namespace, files_list, asset_name):
    old_objects = wizard_tools.get_all_nodes()
    if namespace in wizard_tools.get_all_nodes():
        plug_texturing(namespace, files_list, asset_name, update=True)
        wizard_reference.trigger_after_reference_hook('texturing',
                                    files_list,
                                    namespace,
                                    wizard_tools.get_new_objects(old_objects))

def import_texturing(namespace, files_list, asset_name):
    old_objects = wizard_tools.get_all_nodes()
    if namespace not in wizard_tools.get_all_nodes():
        plug_texturing(namespace, files_list, asset_name, update=False)
        wizard_reference.trigger_after_reference_hook('texturing',
                                        files_list,
                                        namespace,
                                        wizard_tools.get_new_objects(old_objects))

def plug_texturing(namespace, files_list, asset_name, update=False):
    render_graph, surface_node, displacement_node = get_shader(namespace, asset_name)
    textures_dic = get_textures_dic(files_list)

    # Plug diffuse
    if textures_dic['diffuse']:
        attribute = get_attribute(surface_node, 'DiffuseColor', 'Texture', [('Gamma', 'linear')])
        set_file(attribute, textures_dic['diffuse'])

    # Plug metallic
    if textures_dic['diffuse'] and textures_dic['metalness'] and textures_dic['roughness']:
        # Metal color
        attribute = get_attribute(surface_node, 'MetalColor', 'Texture', [('Gamma', 'linear')])
        set_file(attribute, textures_dic['diffuse'])
        # Metal amount
        attribute = get_attribute(surface_node, 'Metal', 'MaskTexture', [('Gamma', 'data')])
        set_file(attribute, textures_dic['metalness'])
        # Metal rougness
        attribute = get_attribute(surface_node, 'MetalRoughness', 'MaskTexture', [('Gamma', 'data')])
        set_file(attribute, textures_dic['roughness'])

    # Plug roughness
    if textures_dic['roughness']:
        if not update:
            surface_node.overrideinheritedattr('Spec1',1)
        attribute = get_attribute(surface_node, 'Spec1Roughness', 'MaskTexture', [('Gamma', 'data')])
        set_file(attribute, textures_dic['roughness'])

    # Plug normal map
    if textures_dic['normal_map']:
        attribute = get_attribute(surface_node, 'Normal', 'NormalMap', [('Gamma', 'data')])
        set_file(attribute, textures_dic['normal_map'])

    # Plug height
    if textures_dic['height_map']:
        if not update:
            displacement_node.overrideinheritedattr('Normalization',"Affine")
            displacement_node.overrideinheritedattr('Offset',0)
            displacement_node.overrideinheritedattr("RaytraceDisplacement", 0.02)
            displacement_node.overrideinheritedattr("DisplaceAmount", 1)
            displacement_node.State.set("bypass")
        attribute = get_attribute(displacement_node, 'Amount', 'MaskTexture', [('Gamma', 'data')])
        set_file(attribute, textures_dic['height_map'])

def set_file(attribute, file):
    with Modifier() as mod:
        # Force file reload by deleting the plug
        plug = get_plug(attribute, 'File')
        plug.delete()
        plug = get_plug(attribute, 'File')
        plug.set(file)

def create_shader(namespace, asset_name):
    shaders_GRP = wizard_tools.add_GRP('SHADERS')

    render_graph = Node.create(namespace, 'RenderGraph')
    render_graph.move(shaders_GRP)

    tag_node = render_graph.loadfile('$(LIBRARY)/rendergraph/tag.gnode')[0]
    tag_node.Tag.set(asset_name)
    tag_node.rename(asset_name)

    attribute_node = render_graph.loadfile('$(LIBRARY)/rendergraph/attributes.gnode')[0]
    attribute_node.overrideinheritedattr('RaytraceSubdivLevel',2)
    attribute_node.overrideinheritedattr('Subdiv', True)
    attribute_node.Input1.Plug.connect(tag_node.Output1.Plug)

    displacement_node = render_graph.loadfile('$(LIBRARY)/rendergraph/shader.gnode')[0] # Displacement Shader
    displacement_node.Shader.set('Displacement')
    displacement_node.Mode.set('displacement')
    displacement_node.rename('{0}_displacement_shader'.format(asset_name))
    displacement_node.Input1.Plug.connect(attribute_node.Output1.Plug)

    surface_node = render_graph.loadfile('$(LIBRARY)/rendergraph/shader.gnode')[0]
    surface_node.Shader.set('Surface2')
    surface_node.Mode.set('surface')
    surface_node.rename('{0}_main_shader'.format(asset_name))
    surface_node.Input1.Plug.connect(displacement_node.Output1.Plug)

    out_node = render_graph.loadfile('$(LIBRARY)/rendergraph/output.gnode')[0]
    out_node.Input1.Plug.connect(surface_node.Output1.Plug)

    return render_graph, surface_node, displacement_node

def get_shader(namespace, asset_name):
    if namespace not in wizard_tools.get_all_nodes():
        render_graph, surface_node, displacement_node = create_shader(namespace, asset_name)
    else: 
        render_graph = wizard_tools.get_node_from_name(namespace)
        surface_node = wizard_tools.get_node_from_name('{0}_main_shader'.format(asset_name))
        displacement_node = wizard_tools.get_node_from_name('{0}_displacement_shader'.format(asset_name))
    return render_graph, surface_node, displacement_node

def create_attribute(node, attribute_name, map_type, attrs=[]):
    with Modifier() as mod:
        attribute = mod.createnode(attribute_name, type='AttributeShader', parent=node)
        attribute.Shader.set(map_type)
        for attr in attrs:
            attribute.overrideinheritedattr(attr[0],attr[1])
    return attribute

def create_plug(attribute, plug_name):
    plug = attribute.createplug(plug_name, 'user', 'texture', Plug.Dynamic)
    return plug

def get_attribute(node, attribute_name, map_type, attrs=[]):
    attribute = None
    for child in node.children():
        if child.name == attribute_name:
            attribute = child
            break
    if not attribute:
        attribute = create_attribute(node,
                                        attribute_name,
                                        map_type,
                                        attrs)
    return attribute

def get_plug(attribute, plug_name):
    plug = None
    for child_plug in attribute.plugs():
        if child_plug.name == plug_name:
            plug = child_plug
            break
    if plug is None:
        plug = create_plug(attribute, plug_name)
    return plug

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
        textures_dic['diffuse'] = diffuse_maps[0]
    else:
        textures_dic['diffuse'] = None

    if len(roughness_maps) >=1:
        textures_dic['roughness'] = roughness_maps[0]
    else:
        textures_dic['roughness'] = None

    if len(metalness_maps) >=1:
        textures_dic['metalness'] = metalness_maps[0]
    else:
        textures_dic['metalness'] = None

    if len(normal_maps) >=1:
        textures_dic['normal_map'] = normal_maps[0]
    else:
        textures_dic['normal_map'] = None

    if len(height_maps) >=1:
        textures_dic['height_map'] = height_maps[0]
    else:
        textures_dic['height_map'] = None

    return textures_dic
