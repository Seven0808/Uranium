# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Logger import Logger
from UM.PluginRegistry import PluginRegistry
from UM.Mesh.MeshWriter import MeshWriter
from UM.Math.Matrix import Matrix
from UM.Math.Vector import Vector

from UM.FileHandler.FileHandler import FileHandler


##  Central class for reading and writing meshes.
#   This class is created by Application and handles reading and writing mesh files.
class MeshFileHandler(FileHandler):
    def __init__(self):
        super().__init__("mesh_writer", "mesh_reader")

    # Try to read the mesh_data from a file using a specified MeshReader.
    # \param reader the MeshReader to read the file with.
    # \param file_name The name of the mesh to load.
    # \param kwargs Keyword arguments.
    #               Possible values are:
    #               - Center: True if the model should be centered around (0,0,0), False if it should be loaded as-is. Defaults to True.
    # \returns MeshData if it was able to read the file, None otherwise.
    def readerRead(self, reader, file_name, **kwargs):
        try:
            results = reader.read(file_name)
            if results is not None:
                if type(results) is not list:
                    results = [results]

                for result in results:
                    if kwargs.get("center", True):
                        # If the result has a mesh and no children it needs to be centered
                        if result.getMeshData() and len(result.getChildren()) == 0:
                            extents = result.getMeshData().getExtents()
                            move_vector = Vector(extents.center.x, extents.center.y, extents.center.z)
                            result.setCenterPosition(move_vector)

                            if result.getMeshData().getExtents(result.getWorldTransformation()).bottom != 0:
                                result.translate(Vector(0, -result.getMeshData().getExtents(result.getWorldTransformation()).bottom, 0))

                        # Move all the meshes of children so that toolhandles are shown in the correct place.
                        for node in result.getChildren():
                            if node.getMeshData():
                                extents = node.getMeshData().getExtents()
                                m = Matrix()
                                m.translate(-extents.center)
                                node.setMeshData(node.getMeshData().getTransformed(m))
                                node.translate(extents.center)
                return results

        except OSError as e:
            Logger.log("e", str(e))

        Logger.log("w", "Unable to read file %s", file_name)
        return None  # unable to read

    ##  Get list of all supported filetypes for writing.
    #   \return List of dicts containing id, extension, description and mime_type for all supported file types.
    def getSupportedFileTypesWrite(self):
        supported_types = []
        meta_data = PluginRegistry.getInstance().getAllMetaData(filter={self._writer_type: {}}, active_only=True)
        for entry in meta_data:
            for output in entry[self._writer_type].get("output", []):
                ext = output.get("extension", "")
                description = output.get("description", ext)
                mime_type = output.get("mime_type", "text/plain")
                mode = output.get("mode", MeshWriter.OutputMode.TextMode)
                supported_types.append({
                    "id": entry["id"],
                    "extension": ext,
                    "description": description,
                    "mime_type": mime_type,
                    "mode": mode
                    })
            return supported_types
