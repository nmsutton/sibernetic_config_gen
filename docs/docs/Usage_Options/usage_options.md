#Example Usage of sibernetic_config_gen

<br>$ python main.py
<br>runs in demo mode where a basic scene is made
<br>see <a href='http://sibernetic-config-gen-docs.readthedocs.io/en/latest/Minimal_Object_Reqs/minimal_object_reqs/'>Minimal_Object_Reqs</a> for more details.
<br><br>Arguments that can be used:
<br>-i = input collada file to import
<br>-o = output config file for sibernetic
<br>--dsca = number to multiply to distance formula for
<br>generating elastic connections
<br>--dexp = exponent to apply to distance formula
<br>
<br>Example run with args:
<br>python main.py -i ./3d_modelling/proto_down_wrm.dae -o ./3d_modelling/proto_down_wrm --dsca 100.0 --dexp 1.5
<br>
<br>sibernetic_config_gen uses the euclidean distance formula to calculate elastic strengths,  dsca is a scalar multiple of that and dexp is an exponent applied to that.  Because the vertices and edges have custom lengths modifications of the calculations in that way is needed to have sibernetic produce stable meshes.
