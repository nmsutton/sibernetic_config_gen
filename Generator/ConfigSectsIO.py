# The MIT License (MIT)
#
# Copyright (c) 2011, 2013 OpenWorm.
# http://openworm.org
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the MIT License
# which accompanies this distribution, and is available at
# http://opensource.org/licenses/MIT
#
# Contributors:
#      OpenWorm - http://openworm.org/people.html
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
# USE OR OTHER DEALINGS IN THE SOFTWARE.

'''
Created on 18.04.2016

@author: nmsutton
'''

#from Generator import Generator
from Particle import Particle, Float4
from Const import Const
from ElasticConnection import ElasticConnection
import re

class ConfigSectsIO(object):
	def import_conf(self, in_file):
		boundbox_sect = True
		particle_sect = False
		bounding_box = []
		particles = []

		with open(in_file, "r") as ins:
			for line in ins:
				if line.rstrip() == "[velocity]":
					particle_sect = False
				elif line.rstrip() == "[position]":
					boundbox_sect = False
					particle_sect = True
				elif boundbox_sect == True and line.rstrip() != "":
					bounding_box.append(float(line.rstrip()))					
				elif particle_sect == True and line.rstrip() != "":
					p_x,p_y,p_z,p_t = line.rstrip().split("\t")
					p_type = "{0:.2g}".format(float(p_t))
					particle = Particle(float(p_x),float(p_y),float(p_z),float(p_type))
					particle.setVelocity(Float4(0.0,0.0,0.0,float(p_type)))
					particles.append(particle)

		return bounding_box, particles

	def import_part_phys(self, phy_file=''):
		part_phys_mod = []

		with open(phy_file, "r") as ins:
			for line in ins:			
				if line.rstrip() != "":
					p_i, p_v = line.rstrip().split("\t")
					part_phys_mod.append(float(p_v))

		return part_phys_mod	

	def import_collada(self, col_file):
		print("collada import")
		particle_sect = False
		bounding_box = [0, 100.2, 0, 66.8, 0, 668]
		#bounding_box = [0, 133.6, 0, 160.32, 0, 66.8]
		#remove_text = "          <float_array id="Sphere-mesh-positions-array" count="2598">"
#		start_pos_section = "        <source id=\"Sphere_001-mesh-positions\">"
		start_pos_section = re.compile(".*<float_array id=\".*positions-array\" count=\"\d+\">.*")
		#end_pos_section = "          <technique_common>"
		tris_section = re.compile("\s+<p>(.*)</p>")
		#tris_triplet = re.compile("(.*\>)?(\S+)\s(\S+)\s(\S+)\s(\S+)\s(\S+)\s(\S+)\s?[<]?(.*)?")
		tris_triplet = re.compile("(\S+)\s(\S+)\s(\S+)\s(\S+)\s(\S+)\s(\S+)\s?")
		xml_pattern = "(.*[>])+(.*)([<].*)+"
		vertex_pattern = "(\S+)\s(\S+)\s(\S+)(\s?)"
		p_type = 2.1
		particles = []
		unsorted_connections = []
		elastic_connections_collection = []
		nMuscles = 1

		with open(col_file, "r") as ins:
			for line in ins:
				if start_pos_section.match(line.rstrip()):#particle_sect == True and line.rstrip() != "":
					for xml in re.finditer(xml_pattern, line.rstrip()):
						#print(xml.group(2))
						for vertex in re.finditer(vertex_pattern, xml.group(2)):
							#print(vertex.group(0))
							p_x = vertex.group(1)
							p_y = vertex.group(2)
							p_z = vertex.group(3)
							#p_x,p_y,p_z,blank = vertex.group(0).split(" ")
							#print(p_x)							
							particle = Particle(float(p_x),float(p_y),float(p_z),float(p_type))
							particle.setVelocity(Float4(0.0,0.0,0.0,float(p_type)))
							particles.append(particle)				
				elif tris_section.match(line.rstrip()):
					print("particles:")
					print(len(particles))
					for tris in re.finditer(tris_triplet, tris_section.match(line.rstrip()).group(1)):
						#print(tris.group(0))
						particle_i_group = [ int(tris.group(1)), int(tris.group(1)), int(tris.group(3)) ]
						particle_j_group = [ int(tris.group(3)), int(tris.group(5)), int(tris.group(5)) ]
						val1 = 0.0
						for p_index in range(len(particle_j_group)):
							part_i = particles[particle_i_group[p_index]]
							part_j = particles[particle_j_group[p_index]]
							unsorted_connections.append([[int(tris.group(1)),int(tris.group(3))],[int(tris.group(1)),int(tris.group(5))],[int(tris.group(3)),int(tris.group(5))]])
							#unsorted_connections.append( ElasticConnection(particles.index(part_j),Particle.distBetween_particles(part_j,part_i), val1, 0) )
							#elastic_connections_collection.append( ElasticConnection(particles.index(part_j),Particle.distBetween_particles(part_j,part_i), val1, 0) )
						
						# add blanks
					for p_i in range(len(particles)):
						total_conn = 0
						#val1 = 1.0
						found_j = []
						for con_i in range(len(unsorted_connections)):
							#part_j_i = int(unsorted_connections[con_i].particle_j - 0.1)
							for connection in unsorted_connections[con_i]:
								if (p_i == connection[0] or p_i == connection[1]) and (total_conn < Const.MAX_NUM_OF_NEIGHBOUR):
									part_i = particles[p_i]
									j_index = (p_i == connection[0]) and connection[1] or connection[0]
									part_j = particles[j_index]
									#elastic_connections_collection.append(unsorted_connections[con_i])
									if not j_index in found_j:
										val1 = 0
										dx2 = part_i.position.x - part_j.position.x
										dy2 = part_i.position.y - part_j.position.y
										dz2 = part_i.position.z - part_j.position.z
										dx2 *= dx2
										dy2 *= dy2
										dz2 *= dz2 
										nMi = particles.index(part_i)*nMuscles/len(particles);
										val1 = (1.1+nMi)*float((dz2 > 100*dx2)and(dz2 > 100*dy2))  

										elastic_connections_collection.append( ElasticConnection(particles.index(part_j),Particle.distBetween_particles(part_j,part_i), val1, 0) )
										found_j.append(j_index)
										total_conn += 1
						elastic_connections_collection.extend([ElasticConnection(Const.NO_PARTICEL_ID,0,0,0)] * (Const.MAX_NUM_OF_NEIGHBOUR - total_conn))#len(particle_i_group)) )

		return bounding_box, particles, elastic_connections_collection

	def export_conf(self, out_file, bounding_box, conf_file_group):

		output_f = open(out_file,"w")

		for bb_point in bounding_box:
			output_f.write(str(bb_point))
			output_f.write("\n")
		output_f.write("[position]\n")

		for i in range(len(conf_file_group)):
			with open(conf_file_group[i], "r") as ins:
				for line in ins:
					output_f.write(line)

			if i == 0:
				output_f.write("[velocity]\n")
			elif i == 1:
				output_f.write("[connection]\n")
			elif i == 2:
				output_f.write("[end]\n")

		output_f.close()