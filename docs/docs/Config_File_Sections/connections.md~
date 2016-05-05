# Elastic Connections Section

[connection] - contains information about elastic connection of all elastic particles
<br>a b c d
<br>
<br>where:
<br>a = particle_j
<br>b = r_ij
<br>c = val1
<br>d = val2

particle_j = ID of particle .  ID is an index for the particles

r_ij = distance * Const.simulationScale
where distance is the distance between particle i and j .

val1 and val2 are values that effect the amount of elastic connection
created.cin

starting sequantially from the first particle index the [connection] section
contains groups of particle_j entries up to the MAX_NUM_OF_NEIGHBOUR variable
which is the max neighbor particles to be included.  

Example for MAX_NUM_OF_NEIGHBOUR = 4
[connection]
1.1	2.24331	0	0
2.1	1.58626	0	0
-1	0	0	0
-1	0	0	0
0.1	2.24331	0	0
2.1	1.58626	0	0
-1	0	0	0
-1	0	0	0

This represent groups for particle 0 and 1.  For particle 0 entries for 1 and 2 are seen.  For particle 1, 0 and 2 respectively.

Note: details here derived from [main.py](https://github.com/openworm/sibernetic_config_gen/blob/master/main.py).
