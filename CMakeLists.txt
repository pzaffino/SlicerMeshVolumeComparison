cmake_minimum_required(VERSION 3.16.3...3.19.7 FATAL_ERROR)

project(SlicerMeshVolumeComparison)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://www.slicer.org/wiki/Documentation/Nightly/Extensions/SlicerMeshVolumeComparison")
set(EXTENSION_CATEGORY "Quantification")
set(EXTENSION_CONTRIBUTORS "Paolo Zaffino (Magna Graecia University of Catanzaro (Italy)), Michela Desito (Magna Graecia University of Catanzaro (Italy)), Maria Francesca Spadea (Karlsruher Intitute of Technology (Germany))")
set(EXTENSION_DESCRIPTION "This extension compute volume difference between meshes")
set(EXTENSION_ICONURL "https://www.example.com/Slicer/Extensions/SlicerMeshVolumeComparison.png")
set(EXTENSION_SCREENSHOTURLS "https://www.example.com/Slicer/Extensions/SlicerMeshVolumeComparison/Screenshots/1.png")
set(EXTENSION_DEPENDS "Sandbox") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(MeshVolumeComparison)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
