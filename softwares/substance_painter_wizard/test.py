import substance_painter.resource

# Display the URL of a resource:
envmap_resources = substance_painter.resource.search("")
print(envmap_resources)
for envmap in envmap_resources:
    envmap_id = envmap.identifier()
    print("The URL of the resource `{0}` is {1}"
        .format(envmap_id.name, envmap_id.url()))
    print("The location of the resource `{0}` is {1}"
        .format(envmap_id.name, envmap_id.location()))
    #print(envmap_id.name, envmap_id.usage)
    print(substance_painter.resource.Usage(envmap_id))

# It is possible to create a ResourceID from a URL. If there is no
# resource corresponding to the URL, the ResourceID is still valid
# but refers to a resource that doesn't exist.
envmap2_id = substance_painter.resource.ResourceID.from_url(
    "resource://starter_assets/Bonifacio Street");

# It is possible to create a ResourceID from a context, a name and
# a version (optional). This is equivalent to the above, with the
# same caveat.
envmap3_id = substance_painter.resource.ResourceID(
    context="starter_assets", name="Bonifacio Street")
envmap4_id = substance_painter.resource.ResourceID(
    context="starter_assets", name="Bonifacio Street",
    version="d30facd8d860fc212f864065641cdca4e8006510.image");

# It is possible to get the ResourceID of a resource embedded in the
# current project. This time it refers to an actual resource.
envmap5_id = substance_painter.resource.ResourceID.from_project(
    name="Bonifacio Street");

# Finally, it is possible to get the ResourceID of a resource that
# was imported in the current session:
envmap6_id = substance_painter.resource.ResourceID.from_session(
    name="Bonifacio Street");