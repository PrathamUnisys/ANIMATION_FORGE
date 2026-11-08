import bpy

def configure_forgotten_kingdom_scene():
    scene = bpy.context.scene
    scene.render.fps = 24
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.frame_start = 1
    scene.frame_end = 1080
    return {"scene": scene.name, "frames": 1080, "fps": 24}
