# ParticleMemIndex Section

[particleMemIndex] - contains information about in which membranes elastic particles are included
<br>a
<br>b
<br>c
<br>d
<br>e
<br>f
<br>g
<br>
<br>where:
<br>a ... g = particles that are included in a given membrane.  The same particles
<br>can be included in multiple different membranes.  The max particles per membrane <br>are given by MAX_MEMBRANES_INCLUDING_SAME_PARTICLE in Const.py and in this
<br>example the constant is 7.  Membrane entried are included in the positions
<br>membrane_index * max_mem_const, i.e. 8th line is the start of the 2cnd membrane
<br>entry.
