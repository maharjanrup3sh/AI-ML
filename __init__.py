bl_info = {
    "name": "AI Pipeline Assistant v4 (Optimizer)",
    "blender": (3, 0, 0),
    "category": "Object",
}

import bpy

# ---------------------------------------------------
# MEMORY SYSTEM
# ---------------------------------------------------

def get_memory():
    if "pipeline_memory" not in bpy.context.scene:
        bpy.context.scene["pipeline_memory"] = {}
    return bpy.context.scene["pipeline_memory"]

def learn(name, label):
    mem = get_memory()
    mem[name.lower()] = label

def recall(name):
    mem = get_memory()
    return mem.get(name.lower(), None)

# ---------------------------------------------------
# COLLECTION SYSTEM (SAFE)
# ---------------------------------------------------

def assign_to_collection(obj, label):
    col = bpy.data.collections.get(label)

    if not col:
        col = bpy.data.collections.new(label)
        bpy.context.scene.collection.children.link(col)

    if obj.name not in col.objects:
        col.objects.link(obj)

# ---------------------------------------------------
# SMART CLASSIFIER
# ---------------------------------------------------

def classify(obj):

    learned = recall(obj.name)
    if learned:
        return learned, 100

    if obj.type != 'MESH':
        return "PROP", 40

    x, y, z = obj.dimensions
    verts = len(obj.data.vertices)
    name = obj.name.lower()

    env = prop = char = 0

    # NAME
    if any(k in name for k in ["wall","floor","terrain","road"]):
        env += 4
    if any(k in name for k in ["chair","table","lamp","prop"]):
        prop += 3
    if any(k in name for k in ["char","player","npc","rig","armature"]):
        char += 5

    # SIZE
    size = max(x, y, z)
    if size > 5:
        env += 3
    elif size < 0.5:
        prop += 2

    # SHAPE
    flatness = min(x, y, z) / max(x, y, z)
    if flatness < 0.2:
        env += 2

    # COMPLEXITY
    if verts > 15000:
        char += 4
    elif verts < 500:
        prop += 2

    # RIG
    if obj.find_armature():
        char += 6

    scores = {"ENV": env, "PROP": prop, "CHAR": char}
    best = max(scores, key=scores.get)
    total = sum(scores.values()) or 1
    confidence = int((scores[best] / total) * 100)

    return best, confidence

# ---------------------------------------------------
# APPLY NAMING
# ---------------------------------------------------

def apply(obj, label, index, mode):

    original_name = obj.name

    if mode == "GAME":
        obj.name = f"SM_{label}_{index:02d}"
    elif mode == "FILM":
        obj.name = f"{label}_Main_{index:02d}"
    else:
        obj.name = f"{label}_{index:02d}"

    learn(original_name, label)

# ---------------------------------------------------
# REPORT SYSTEM
# ---------------------------------------------------

def generate_report(context):

    report = {
        "ENV": 0,
        "PROP": 0,
        "CHAR": 0,
        "low_conf": []
    }

    for obj in context.selected_objects:

        label, confidence = classify(obj)

        obj["ai_label"] = label
        obj["ai_confidence"] = confidence

        report[label] += 1

        if confidence < 60:
            report["low_conf"].append(obj.name)

    context.scene["pipeline_report"] = report

# ---------------------------------------------------
# OPTIMIZER
# ---------------------------------------------------

def optimize_scene(context):

    report = {"decimated":0,"textures":0,"duplicates":0}

    for obj in context.selected_objects:

        if obj.type != 'MESH':
            continue

        mesh = obj.data

        # DECIMATE
        if len(mesh.vertices) > 5000:
            dec = obj.modifiers.new(name="AI_Decimate", type='DECIMATE')
            dec.ratio = 0.5
            report["decimated"] += 1

        # DUPLICATES
        for other in context.selected_objects:
            if other != obj and other.type == 'MESH':
                if other.data == obj.data:
                    other.data = obj.data
                    report["duplicates"] += 1

        # TEXTURES
        for mat in mesh.materials:
            if mat and mat.use_nodes:
                for node in mat.node_tree.nodes:
                    if node.type == 'TEX_IMAGE' and node.image:
                        img = node.image
                        if img.size[0] > 2048:
                            img.scale(2048,2048)
                            report["textures"] += 1

    return report

# ---------------------------------------------------
# OPERATORS
# ---------------------------------------------------

class PIPELINE_OT_preview(bpy.types.Operator):
    bl_idname = "pipeline.preview"
    bl_label = "Scan Scene"

    def execute(self, context):
        generate_report(context)
        self.report({'INFO'}, "Scan complete")
        return {'FINISHED'}

class PIPELINE_OT_apply(bpy.types.Operator):
    bl_idname = "pipeline.apply"
    bl_label = "Apply Naming & Grouping"

    def execute(self, context):

        mode = context.scene.pipeline_mode

        for i, obj in enumerate(context.selected_objects, 1):
            label, conf = classify(obj)
            apply(obj, label, i, mode)
            assign_to_collection(obj, label)

        return {'FINISHED'}

class PIPELINE_OT_optimize(bpy.types.Operator):
    bl_idname = "pipeline.optimize"
    bl_label = "Optimize Scene"

    def execute(self, context):

        bpy.ops.ed.undo_push(message="Optimize Scene")

        report = optimize_scene(context)
        self.report({'INFO'}, str(report))

        return {'FINISHED'}

# ---------------------------------------------------
# UI PANEL
# ---------------------------------------------------

class PIPELINE_PT_panel(bpy.types.Panel):
    bl_label = "AI Pipeline Assistant v4"
    bl_idname = "PIPELINE_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Pipeline'

    def draw(self, context):

        layout = self.layout

        # MODE
        box = layout.box()
        box.label(text="⚙ Mode")
        box.prop(context.scene, "pipeline_mode")

        # SCAN
        box = layout.box()
        box.label(text="🔍 Scan")
        box.operator("pipeline.preview", icon='VIEWZOOM')

        # REPORT
        report = context.scene.get("pipeline_report")
        if report:
            box = layout.box()
            box.label(text="📊 Report")
            box.label(text=f"ENV: {report['ENV']}")
            box.label(text=f"PROP: {report['PROP']}")
            box.label(text=f"CHAR: {report['CHAR']}")

            if report["low_conf"]:
                box.label(text="⚠ Low Confidence:")
                for name in report["low_conf"][:5]:
                    box.label(text=f"- {name}")

        # APPLY
        box = layout.box()
        box.label(text="✅ Apply")
        box.operator("pipeline.apply", icon='CHECKMARK')

        # OPTIMIZE
        box = layout.box()
        box.label(text="🧹 Optimize")
        box.operator("pipeline.optimize", icon='MOD_DECIM')

# ---------------------------------------------------
# REGISTER
# ---------------------------------------------------

def register():

    bpy.utils.register_class(PIPELINE_OT_preview)
    bpy.utils.register_class(PIPELINE_OT_apply)
    bpy.utils.register_class(PIPELINE_OT_optimize)
    bpy.utils.register_class(PIPELINE_PT_panel)

    bpy.types.Scene.pipeline_mode = bpy.props.EnumProperty(
        name="Mode",
        items=[
            ('GAME',"Game",""),
            ('FILM',"Film",""),
            ('SIMPLE',"Simple",""),
        ],
        default='GAME'
    )

def unregister():

    bpy.utils.unregister_class(PIPELINE_OT_preview)
    bpy.utils.unregister_class(PIPELINE_OT_apply)
    bpy.utils.unregister_class(PIPELINE_OT_optimize)
    bpy.utils.unregister_class(PIPELINE_PT_panel)

    del bpy.types.Scene.pipeline_mode

if __name__ == "__main__":
    register()