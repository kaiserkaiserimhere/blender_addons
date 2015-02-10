bl_info = {
    'name': "set edges length",
    'description': "edges length",
    'author': "Giuseppe De Marco [BlenderLab] inspired by NirenYang",
    'version': (0, 2, 1),
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
import numpy as np
from bpy.props import BoolProperty, FloatProperty, EnumProperty, StringProperty

edge_length_debug = True
_error_message = 'Please select one or more edge to fill select_history'


def get_edge_vector( edge ):
    verts = ( edge.verts[0].co, edge.verts[1].co)
    
    # I can say that vector 1 is always greater then vector 0 if the edge
    #   is vertical in positive x y
    #   is vertical in negative x and negative y
    #   is orizontal with negative x and positive y

    # then is lesser if the edge
    #   is vertical with positive x and negative y
    #   is vertical with negative x and positive y    
    #   is orizontal with positive x and positive y
    
    # so the vertex disposition, on creation, is unclockwise
    
    vector = verts[1] - verts[0]
    return vector

def get_selected(bmesh_obj, geometry_type):
    """
    geometry type should be edges, verts or faces 
    """
    selected = []
    for i in getattr(bmesh_obj, geometry_type):
        if i.select:
            selected.append(i)
    return tuple(selected)

def get_center_vector( verts ):
    """
    verts = [mathutils.Vector((x,y,z)), mathutils.Vector((x,y,z))]
    """
    center_vector = mathutils.Vector( ((( verts[1][0] + verts[0][0] )/2.)
                                    , (( verts[1][1] + verts[0][1] )/2.)
                                    , (( verts[1][2] + verts[0][2] )/2.) ) )
    return center_vector

def compare_edge_vertices( edge ):
    """
    return 0  if edge.verts[0].co > edge.verts[1].co
    return 1  if edge.verts[1].co > edge.verts[0].co
    return -1 if edge.verts[0].co == edge.verts[1].co
    """
    if np.absolute(edge.verts[0].co) > np.absolute(edge.verts[1].co):
        return 0
    elif np.absolute(edge.verts[1].co) > np.absolute(edge.verts[0].co):
        return 1
    else:
        return -1

def sub_ad_abs_verts( v0, v1, operation='add', first_element=0 ):
    """
    operations = add sub
    """
    v0_sings = { 'x': -1 if v[0] < 0 else 1, 
                 'y': -1 if v[0] < 0 else 1, 
                 'z': -1 if v[0] < 0 else 1, 
                }
    v1_sings = { 'x': -1 if v[1] < 0 else 1, 
                 'y': -1 if v[1] < 0 else 1, 
                 'z': -1 if v[1] < 0 else 1, 
                }
    
    v0_abs = np.absolute( v0 )
    v1_abs = np.absolute( v1 )
    
    res = None
    
    if operation == 'add': 
        res = v0_abs + v1_abs
    elif operation == 'sub':
        if first_element == 0: v0_abs - v1_abs
        else:                  v1_abs - v0_abs
    
    res = mathutils.Vector( res[0]*v0_signs['x'],\
                            res[1]*v0_signs['y'],\
                            res[2]*v0_signs['z'],\
                          )
    return res

class LengthSet(bpy.types.Operator):
    bl_idname = "object.mesh_edge_length_set"
    bl_label = "Set edges length"
    bl_description = "change selected edges length (Shit+Alt+E)"
    bl_options = {'REGISTER', 'UNDO'}

    old_length = StringProperty(name = 'originary length') #, default = 0.00, unit = 'LENGTH', precision = 5, set = print(''))
    target_length = FloatProperty(name = 'length', default = 0.00, unit = 'LENGTH', precision = 5)
    
    #incremental = BoolProperty(\
    #    name="incremental",\
    #    default=False,\
    #    description="incremental")

    mode = EnumProperty(
        items = [
                 ('fixed', 'fixed', 'fixed'),        
                 ('increment', 'increment', 'increment'), 
                 ('decrement', 'decrement', 'decrement'),                  
                 ],
        name = "mode")

    behaviour = EnumProperty(
        items = [
                 ('A > B', 'A > B', '1'),        
                 ('B > A', 'B > A', '2'),                
                 ('proportional', 'proportional', '3'),        
                 #('invert', 'invert', 'Three'),
                 ('clockwise', 'clockwise', 'One'), 
                 ('unclockwise', 'unclockwise', 'One'),                  
                 ],
        name = "Resize behaviour")
            
    originary_edge_length_dict = {}
    
    @classmethod
    def poll(cls, context):
        return (context.edit_object)
    
    def invoke(self, context, event):
        wm = context.window_manager

        obj = context.edit_object
        bm = bmesh.from_edit_mesh(obj.data)
        
        bpy.ops.mesh.select_mode(type="EDGE")
        
        self.selected_edges = get_selected(bm, 'edges')
        
        if self.selected_edges:
            
            vertex_set = []
            
            for edge in self.selected_edges:
                vector = get_edge_vector( edge )
                
                if edge.verts[0].index not in vertex_set:
                    vertex_set.append( edge.verts[0].index )
                else: 
                    self.report( {'ERROR_INVALID_INPUT'}, 'edges with shared vertices not permitted. Use scale instead.' )
                    return {'CANCELLED'} 
                if edge.verts[1].index not in vertex_set:
                    vertex_set.append( edge.verts[1].index )
                else: 
                    self.report( {'ERROR_INVALID_INPUT'}, 'edges with shared vertices not permitted. Use scale instead.' )
                    return {'CANCELLED'} 
                
                # warning, it's a constant !
                verts_index = ''.join((str(edge.verts[1].index), str(edge.verts[0].index)))
                self.originary_edge_length_dict[ verts_index ] = vector
                self.old_length = str(vector.length)
        else:
            self.report({'ERROR'}, _error_message)
            return {'CANCELLED'}        

        if edge_length_debug: self.report({'INFO'}, str(self.originary_edge_length_dict)) 
        
        if bpy.context.scene.unit_settings.system == 'IMPERIAL':
            # imperial conversion 2 metre conversion
            vector.length = ( 0.9144 * vector.length ) / 3

        self.target_length = vector.length

        return wm.invoke_props_dialog(self)
    

    def execute(self, context):
        if edge_length_debug: self.report({'INFO'}, 'execute')
        
        bpy.ops.mesh.select_mode(type="EDGE")

        self.context = context
        
        obj = context.edit_object
        bm = bmesh.from_edit_mesh(obj.data)
        
        self.selected_edges = get_selected(bm, 'edges')
        
        if not self.selected_edges:
            self.report({'ERROR'}, _error_message)
            return {'CANCELLED'}

        for edge in self.selected_edges:
            
            vector = get_edge_vector( edge )
            # what we shold see in originary length dialog field
            self.old_length = str(vector.length)
                        
            vector.length = abs(self.target_length)
            center_vector = get_center_vector( ( edge.verts[0].co, edge.verts[1].co) )
            
            verts_index = ''.join((str(edge.verts[1].index), str(edge.verts[0].index)))
            
            if edge_length_debug: self.report({'INFO'}, \
                                  ' - '.join( ('vector '+str(vector), \
                                  'originary_vector '+str(self.originary_edge_length_dict[verts_index])\
                                  ))) 

            verts = ( edge.verts[0].co, edge.verts[1].co)
            
            
            
            if edge_length_debug: self.report({'INFO'}, \
            '\n edge.verts[0].co '+str(verts[0])+\
            '\n edge.verts[1].co '+str(verts[1])+\
            '\n vector.length'+ str(vector.length))
            
            # the clockwise direction have v1 -> v0, unclockwise v0 -> v1
            
            if self.target_length >= 0:
                if self.behaviour == 'proportional':
                    edge.verts[1].co = center_vector  + vector / 2
                    edge.verts[0].co = center_vector  - vector / 2
                    
                    if self.mode == 'decrement':
                        edge.verts[0].co = (center_vector  + vector / 2)  - (self.originary_edge_length_dict[verts_index] / 2 )
                        edge.verts[1].co = (center_vector  - vector / 2)  + (self.originary_edge_length_dict[verts_index] / 2 )
                    
                    elif self.mode == 'increment':
                        edge.verts[1].co = (center_vector  + vector / 2) +  self.originary_edge_length_dict[verts_index] / 2
                        edge.verts[0].co = (center_vector  - vector / 2) -  self.originary_edge_length_dict[verts_index] / 2

                elif self.behaviour == 'A > B':
                    if edge_length_debug: self.report({'INFO'}, \
                                          str((\
                                          abs(edge.verts[0].co[0]),\
                                          abs(edge.verts[0].co[1]),\
                                          abs(edge.verts[0].co[2]),\
                                          )))
                                          
                    if compare_edge_vertices(edge) == 0:
                        edge.verts[1].co = sub_ad_abs_verts( edge.verts[1].co, vector, operation='add', first_element=0 )
                    elif compare_edge_vertices(edge) == 1:
                        edge.verts[0].co = sub_ad_abs_verts( edge.verts[0].co, vector, operation='add', first_element=1 )
                    
                    if self.mode == 'decrement':
                        edge.verts[0].co = (center_vector  + vector / 2)  - (self.originary_edge_length_dict[verts_index] / 2 )
                        edge.verts[1].co = (center_vector  - vector / 2)  + (self.originary_edge_length_dict[verts_index] / 2 )
                    
                    elif self.mode == 'increment':
                        edge.verts[1].co = (center_vector  + vector / 2) +  self.originary_edge_length_dict[verts_index] / 2
                        edge.verts[0].co = (center_vector  - vector / 2) -  self.originary_edge_length_dict[verts_index] / 2

                elif self.behaviour == 'B > A':
                    edge.verts[1].co = center_vector  + vector / 2
                    edge.verts[0].co = center_vector  - vector / 2
                    
                    if self.mode == 'decrement':
                        edge.verts[0].co = (center_vector  + vector / 2)  - (self.originary_edge_length_dict[verts_index] / 2 )
                        edge.verts[1].co = (center_vector  - vector / 2)  + (self.originary_edge_length_dict[verts_index] / 2 )
                    
                    elif self.mode == 'increment':
                        edge.verts[1].co = (center_vector  + vector / 2) +  self.originary_edge_length_dict[verts_index] / 2
                        edge.verts[0].co = (center_vector  - vector / 2) -  self.originary_edge_length_dict[verts_index] / 2



                elif self.behaviour == 'unclockwise':
                    if self.mode == 'increment':   
                        edge.verts[1].co = verts[0]  + ( self.originary_edge_length_dict[verts_index] + vector )
                    elif self.mode == 'decrement':
                        edge.verts[0].co = verts[1]  - ( self.originary_edge_length_dict[verts_index] - vector )
                    else:
                        edge.verts[1].co = verts[0]   + vector
                    
                else:
                    if self.mode == 'increment': 
                        edge.verts[0].co = verts[1]  - ( self.originary_edge_length_dict[verts_index]  + vector )                        
                    elif self.mode == 'decrement':   
                        edge.verts[1].co = verts[0]  + ( self.originary_edge_length_dict[verts_index] - vector )
                    else:
                        edge.verts[0].co = verts[1]  - vector

            
            if bpy.context.scene.unit_settings.system == 'IMPERIAL':
                # imperial conversion 2 metre conversion
                #vector.length = ( 3. * vector.length ) / 0.9144
                # metre 2 imperial conversion
                #vector.length = ( 0.9144 * vector.length ) / 3.                
                for mvert in edge.verts:
                    # school time: 0.9144 : 3 = X : mvert
                    mvert.co = ( 0.9144 * mvert.co ) / 3
            
            
            if edge_length_debug: self.report({'INFO'}, \
            '\n edge.verts[0].co'+str(verts[0])+\
            '\n edge.verts[1].co'+str(verts[1])+\
            '\n vector'+str(vector)+'\n v1 > v0:'+str( (verts[1]>=verts[0]  ) ) )
            
            bmesh.update_edit_mesh(obj.data, True)
        
        
        return {'FINISHED'}

        
def menu_func(self, context):
    self.layout.operator_context = 'INVOKE_DEFAULT'
    self.layout.separator()    
    self.layout.label(text="Edges length:")
    row = self.layout.row(align=True)
    row.operator(LengthSet.bl_idname, "Set edges length")
    
    
def register():
    bpy.utils.register_class(LengthSet)
    bpy.types.VIEW3D_PT_tools_meshedit.append(menu_func)
    
    # edge contextual edit menu ( CTRL + E )
    bpy.types.VIEW3D_MT_edit_mesh_edges.append(menu_func)
    
    # hotkey
    kc = bpy.context.window_manager.keyconfigs.default.keymaps['Mesh']
    if LengthSet.bl_idname not in kc.keymap_items:
        kc.keymap_items.new(LengthSet.bl_idname, 'E', 'PRESS', shift = True, alt = True)

def unregister():
    bpy.utils.unregister_class(LengthSet)
    bpy.types.VIEW3D_PT_tools_meshedit.remove(menu_func)
    bpy.types.VIEW3D_MT_edit_mesh_edges.remove(menu_func)

    # hotkey
    kc = bpy.context.window_manager.keyconfigs.default.keymaps['Mesh']
    if LengthSet.bl_idname in kc.keymap_items:
        kc.keymap_items.remove(kc.keymap_items[LengthSet.bl_idname])

if __name__ == "__main__":
    register()
