# blender_addons
Blender custom addons

To install an addon please read Blender's Documentation
http://wiki.blender.org/index.php/Doc:2.6/Manual/Extensions/Python/Add-Ons


* mesh_edges_length.py 

    Working with Cosenza Blender Training [1] I discovered some user habits, specially in engineers profiles, geoscientists and everyone of them who came from CAD experience, that needs the opportunity to set an edge lenght to a fixed, absolute, value.
    
    This awareness pushed me to search and then develop the addon that do this.
    I also found and started developing on a fork of NirenYang's mesh_edges_length_angle_yi.py [2], it was the code that ispired me to believe that other guys, in this world, have already thought that it could be useful.
    
    mesh_edges_length.py simply permits us to set the lenght of an edge even if the Scene is in None, Metrical of Imperial units, converting these automatically to the user. It comes with 4 behaviour:
    
    Proportional: it sets the edge length increasing it on both sides, preserving the vertices's middle point position, preventing that the center of the edge could be dislocated.
    Clockwise: It sets the length increasing it from the last vertice in the clockwise direction.
    Unclockwise: ...opposite direction of the previous.
    Invert: it inverts the vertices. Probably it's really useless but I'm let it there for some user experiences that actually I don't cognise. Probably sooner or later this feature will be dropped.
    Together with the behaviour settings, mesh_edges_length.py comes with a option called "incremental". It let the behaviour function to work as usual but, instead of setting the edge length to the fixed value, it increase the current edge length with the value that we choose.
    
    mesh_edges_length.py could also works on multiple selected edges but just the last in selection history gets his length displayed in the dialog window, to the user eye.
    
    Accessing methods
    It could be called in these ways:
    
    Shift+Alt+E, I mantained the Yang approach, it was smart
    
    in Toolshelf, It was appended in Tools tab
    
    CTRL+E, in Edge Special menu, also appended on the bottom
    
    I hope that this toy is to your liking as it was for me during its development, I'm also curious of your feedbacks.
    
     https://www.blendernetwork.org/events/view/7
     
     https://developer.blender.org/T39999
    
