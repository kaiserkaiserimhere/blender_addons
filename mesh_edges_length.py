bl_info = {
    'name': "set edges length",
    'description': "edges length",
    'author': "Giuseppe De Marco [BlenderLab] inspired by NirenYang",
    'version': (0, 0, 3),
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

edge_length_debug = False
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

def get_center_vector( verts ):
    """
    verts = [mathutils.Vector((x,y,z)), mathutils.Vector((x,y,z))]
    """
    center_vector = mathutils.Vector( ((( verts[1][0] + verts[0][0] )/2.)
                                    , (( verts[1][1] + verts[0][1] )/2.)
                                    , (( verts[1][2] + verts[0][2] )/2.) ) )
    return center_vector
    

class LengthSet(bpy.types.Operator):
    bl_idname = "object.mesh_edge_length_set"
    bl_label = "Set edges length"
    bl_description = "change selected edges length (Shit+Alt+E)"
    bl_options = {'REGISTER', 'UNDO'}
    
    target_length = FloatProperty(name = 'length', default = 0.0)
    
    incremental = BoolProperty(\
        name="incremental",\
        default=False,\
        description="incremental")

    behaviour = EnumProperty(
        items = [
                 ('proportional', 'proportional', 'Three'),        
                 ('invert', 'invert', 'Three'),
                 ('clockwise', 'clockwise', 'One'), 
                 ('unclockwise', 'unclockwise', 'One'),                  
                 ],
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
        
        self.edge_length_win_opened = True
        self.execute(self.context)
    
    def execute(self, context):
        if edge_length_debug: self.report({'INFO'}, 'execute')
        
        self.context = context
        
        obj = context.edit_object
        bm = bmesh.from_edit_mesh(obj.data)
        
        self.selected_edges = get_selected(bm, 'edges')
        
        if not self.edge_length_win_opened: 
            self.open_edge_length_window( bm )
        
        else:
            self.edge_length_win_opened = False            
            for edge in self.selected_edges:
                

                verts = [edge.verts[0].co, edge.verts[1].co]

                if self.behaviour == 'invert':
                    vector = verts[0] - verts[1]
                elif self.behaviour == 'unclockwise':
                    vector = verts[1] - verts[0]
                elif self.behaviour == 'proportional':
                    center_vector = get_center_vector( verts )
                    vector = (verts[1] - center_vector) - (verts[0] - center_vector )
                    if edge_length_debug: self.report({'INFO'}, '\n center vector '+str(center_vector)) 
                else:
                    vector = verts[1] - verts[0]
                                
                if edge_length_debug: self.report({'INFO'}, '\n vector '+str(vector)) 
                
                vector.length = abs(self.target_length)
                
                if edge_length_debug: self.report({'INFO'}, \
                '\n edge.verts[0].co '+str(verts[0])+\
                '\n edge.verts[1].co '+str(verts[1])+\
                '\n vector'+str(vector)+ '\n vector.length'+ str(vector.length))
                              
                if self.target_length > 0:
                    if self.behaviour == 'proportional':
                        edge.verts[1].co = center_vector  + vector / 2
                        edge.verts[0].co = center_vector  - vector / 2
                        if self.incremental:
                            edge.verts[1].co = center_vector  + vector
                            edge.verts[0].co = center_vector  - vector                                
                    elif self.behaviour == 'unclockwise':
                        edge.verts[1].co = verts[0] + vector
                        if self.incremental: edge.verts[1].co = verts[1]  + vector                         
                    else:
                        edge.verts[0].co = verts[1] - vector
                        if self.incremental: edge.verts[0].co = verts[0]  - vector 

                elif self.target_length < 0:                  
                    if self.behaviour == 'proportional':
                        edge.verts[1].co = center_vector  - vector / 2
                        edge.verts[0].co = center_vector  + vector / 2
                        if self.incremental:
                            edge.verts[1].co = center_vector  - vector
                            edge.verts[0].co = center_vector  + vector                           
                    elif self.behaviour == 'unclockwise':
                        edge.verts[1].co = verts[0] - vector     
                        if self.incremental: edge.verts[1].co = verts[1]  - vector
                    else:
                        edge.verts[0].co = verts[1] + vector
                        if self.incremental: edge.verts[0].co = verts[1]  + vector 

                if edge_length_debug: self.report({'INFO'}, \
                '\n edge.verts[0].co'+str(verts[0])+\
                '\n edge.verts[1].co'+str(verts[1])+\
                '\n vector'+str(vector) )

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
