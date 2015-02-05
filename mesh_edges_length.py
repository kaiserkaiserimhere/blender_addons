bl_info = {
    'name': "set edges length",
    'description': "edges length",
    'author': "Giuseppe De Marco [BlenderLab] inspired by NirenYang",
    'version': (0, 0, 1),
    'blender': (2, 7, 0, 5),
    'location': '[Toolbar][Tools][Mesh Tools]: set Length(Shit+Alt+E)',
    'warning': "",
    'category': 'Mesh',
    "wiki_url": "",
    "tracker_url": "",
}


import bpy
import bmesh
import mathutils
from bpy.props import BoolProperty, FloatProperty, EnumProperty

edge_length_debug = True
edge_length_win_opened = False
_error_message = 'Edge selection is needed'


def get_selected(bmesh_obj, geometry_type):
    """
    geometry type should be edges, verts or faces 
    """
    selected = []
    for i in getattr(bmesh_obj, geometry_type):
        if i.select:
            selected.append(i)
    return selected


class LengthSet(bpy.types.Operator):
    bl_idname = "object.mesh_edge_length_set"
    bl_label = "Set edges length"
    bl_description = "change selected edges length (Shit+Alt+E)"
    bl_options = {'REGISTER', 'UNDO'}
    
    target_length = FloatProperty(name = 'length', default = 0.0)
    
    #~ incremental = BoolProperty(\
        #~ name="incremental",\
        #~ default=False,\
        #~ description="incremental")
        
    #~ proportional_resize = BoolProperty(\
        #~ name="proportional direction",\
        #~ default=False,\
        #~ description="increase the edge in a proportional direction")
        #~ 
    #~ invert = BoolProperty(\
        #~ name="invert vertices",\
        #~ default=False,\
        #~ description="invert vertices")


    behaviour = EnumProperty(
        items = [('normal', 'normal', 'One'), 
                 ('incremental', 'incremental', 'Two'),
                 ('proportional', 'proportional', 'Three'),
                 ('invert', 'invert', 'Three')],
        name = "Resize behaviour")
            
    
    me = vts_sequence = None
    edge_length_win_opened = False
    
    @classmethod
    def poll(cls, context):
        return (context.edit_object)
    
    def invoke(self, context, event):
        wm = context.window_manager

        obj = context.edit_object
        bm = bmesh.from_edit_mesh(obj.data)

        if bm.select_history and isinstance(bm.select_history[0], bmesh.types.BMEdge):
            vts_sequence = [i.index for i in bm.select_history[-1].verts]
            self.report({'INFO'}, str(type(bm.select_history[0])))            
        else:
            self.report({'ERROR'}, _error_message)
            return {'CANCELLED'}        
        
        
        vector = bm.verts[vts_sequence[-2]].co - bm.verts[vts_sequence[-1]].co
        self.target_length = vector.length
        
        return wm.invoke_props_dialog(self)

    def open_edge_length_window(self, bm_obj):
        
        if not self.selected_edges:
            self.report({'ERROR'}, _error_message)
            return {'CANCELLED'}
        
        if edge_length_debug: self.report({'INFO'}, str(self.target_length))

        self.edge_length_win_opened = True
        self.execute(self.context)
    
    def execute(self, context):
        if edge_length_debug: self.report({'INFO'}, 'execute')
        
        self.context = context
        
        obj = context.edit_object
        bm = bmesh.from_edit_mesh(obj.data)
        
        #self.switch_point = False
        self.selected_edges = get_selected(bm, 'edges')
        
        if not self.edge_length_win_opened: 
            self.open_edge_length_window( bm )
        
        else:
            self.edge_length_win_opened = False
            if edge_length_debug: self.report({'INFO'}, 'win_close')
            
            for edge in self.selected_edges:
                
                #~ if self.invert_vert_pos:
                    #~ verts = [edge.verts[1].co, edge.verts[0].co]
                #~ else:
                verts = [edge.verts[0].co, edge.verts[1].co]
                
                if edge_length_debug: self.report({'INFO'}, 'edge '+str(edge)) 
                if edge_length_debug: self.report({'INFO'}, self.behaviour )


                if self.behaviour == 'invert':
                    vector = verts[0] - verts[1]
                elif self.behaviour == 'proportional':
                    vector = verts[1] - verts[0]
                    if edge_length_debug: self.report({'WARNING'}, 'proportional not implemented yet !' )
                    
                else:
                    vector = verts[1] - verts[0]
                
                if edge_length_debug: self.report({'INFO'}, 'edge.verts[1].co, edge.verts[0].co '+str(verts[1])+' '+str(verts[0]) )
                if edge_length_debug: self.report({'INFO'}, 'vector '+str(vector)) 
                vector.length = abs(self.target_length)
                
                if edge_length_debug: self.report({'INFO'}, 'vector '+str(vector.length)) 
                if edge_length_debug: self.report({'INFO'}, 'target_length'+str(vector.length)) 

                if self.target_length > 0:

                    edge.verts[0].co = verts[1] - vector
                    if self.behaviour == 'incremental':
                        edge.verts[0].co = verts[0]  - vector 

                    if edge_length_debug: self.report({'INFO'}, 'self.target_length > 0') 
                    
                elif self.target_length < 0:                  
                    edge.verts[0].co = verts[1] + vector
                    if self.behaviour == 'incremental':
                        edge.verts[0].co = verts[0]  + vector 
                #if self.invert_vert_pos:
                    # this rotate it
                    #~ a = mathutils.Vector( edge.verts[0].co )
                    #~ b = mathutils.Vector( edge.verts[1].co )
                    #~ edge.verts[0].co = b
                    #~ edge.verts[1].co = a
                    #edge.verts[0].co = edge.verts[0].co - edge.verts[1].co
                
                # eventuale nuovo approccio:
                # 1. trova il centro dell' edge 
                # 2. sfrutta: bpy.ops.transform.resize(value=(2.53986, 2.53986, 2.53986), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)

                
            bmesh.update_edit_mesh(obj.data, True)
        return {'FINISHED'}

        
def menu_func(self, context):
    self.layout.operator_context = 'INVOKE_DEFAULT'
    #self.layout.label(text="edges length:")
    row = self.layout.row(align=True)
    row.operator(LengthSet.bl_idname, "Set edges length")
    self.layout.separator()
    
    
def register():
    bpy.utils.register_class(LengthSet)
    bpy.types.VIEW3D_PT_tools_meshedit.append(menu_func)

    # hotkey
    kc = bpy.context.window_manager.keyconfigs.default.keymaps['Mesh']
    if LengthSet.bl_idname not in kc.keymap_items:
        kc.keymap_items.new(LengthSet.bl_idname, 'E', 'PRESS', shift = True, alt = True)

def unregister():
    bpy.utils.unregister_class(LengthSet)
    bpy.types.VIEW3D_PT_tools_meshedit.remove(menu_func)
    
    # hotkey
    kc = bpy.context.window_manager.keyconfigs.default.keymaps['Mesh']
    if LengthSet.bl_idname in kc.keymap_items:
        kc.keymap_items.remove(kc.keymap_items[LengthSet.bl_idname])

if __name__ == "__main__":
    register()
