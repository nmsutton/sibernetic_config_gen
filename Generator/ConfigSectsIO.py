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
		boundry_box = []
		particles = []

		with open(in_file, "r") as ins:
			for line in ins:
				if line.rstrip() == "[velocity]":
					particle_sect = False
				elif line.rstrip() == "[position]":
					boundbox_sect = False
					particle_sect = True
				elif boundbox_sect == True and line.rstrip() != "":
					boundry_box.append(float(line.rstrip()))					
				elif particle_sect == True and line.rstrip() != "":
					p_x,p_y,p_z,p_t = line.rstrip().split("\t")
					p_type = "{0:.2g}".format(float(p_t))
					particle = Particle(float(p_x),float(p_y),float(p_z),float(p_type))
					particle.setVelocity(Float4(0.0,0.0,0.0,float(p_type)))
					particles.append(particle)

		return boundry_box, particles

	def import_part_phys(self, phy_file=''):
		part_phys_mod = []

		with open(phy_file, "r") as ins:
			for line in ins:			
				if line.rstrip() != "":
					p_i, p_v = line.rstrip().split("\t")
					part_phys_mod.append(float(p_v))

		return part_phys_mod	

	def extract_particles(self, p_type, line, xml_pattern, vertex_pattern):
		particles = []
		for xml in re.finditer(xml_pattern, line.rstrip()):
			for vertex in re.finditer(vertex_pattern, xml.group(2)):
				p_x = vertex.group(1)
				p_y = vertex.group(2)
				p_z = vertex.group(3)						
				particle = Particle(float(p_x),float(p_y),float(p_z),float(p_type))
				particle.setVelocity(Float4(0.0,0.0,0.0,float(p_type)))
				particles.append(particle)		

		return particles

	def translate_mesh(self, trans_type, trans, sect, boundry_pattern, boundry_box, particles):
		trans_3d_object = trans[0]
		sect_3d_object = sect[0]
		x_trans = float(trans[1])
		y_trans = float(trans[2])
		z_trans	= float(trans[3])
		print (trans_3d_object, " ", sect_3d_object)
		if trans_3d_object == sect_3d_object and boundry_pattern.match(trans_3d_object):
			if trans_type == "position":
				boundry_box[0] += x_trans
				boundry_box[1] += x_trans
				boundry_box[2] += y_trans
				boundry_box[3] += y_trans
				boundry_box[4] += z_trans
				boundry_box[5] += z_trans
			elif trans_type == "scale":
				boundry_box[0] *= x_trans
				boundry_box[1] *= x_trans
				boundry_box[2] *= y_trans
				boundry_box[3] *= y_trans
				boundry_box[4] *= z_trans
				boundry_box[5] *= z_trans			
		elif trans_3d_object == sect_3d_object:
			sect_start = sect[1]
			sect_end = sect[2]
			print(sect_start, "\t", sect_end)
			for i in range(sect_end - sect_start):
				offset_i = i+sect_start
				if trans_type == "position":				
					particles[offset_i].position.x += x_trans
					particles[offset_i].position.y += y_trans
					particles[offset_i].position.z += z_trans
				if trans_type == "scale":					
					particles[offset_i].position.x *= x_trans
					particles[offset_i].position.y *= y_trans
					particles[offset_i].position.z *= z_trans								

		return boundry_box, particles		

	def import_collada(self, col_file):
		'''
		Importing boundry box assumes box verticies are in collada file in format vertice 1-8 =
		(0 0 0) (0 0 1) (0 1 0) (0 1 1) (1 0 0) (1 0 1) (1 1 0) (1 1 1)

		<x, z, y> it appears works

		Collada transforms work as follows:
		<matrix>
		 1.0 0.0 0.0 2.0 # x moves 1*2 further
		 0.0 1.0 0.0 3.0 # y moves 1*3 further
		 0.0 0.0 1.0 4.0 # z moves 1*4 further
		 0.0 0.0 0.0 1.0 # x,y,z moves 0*1 further
		</matrix> 
		NOTE: unclear if row 4 applies translation uniformly or along individual axes.
		Assuming individual axes for now, such as <x,y,z,s> and x moves x*s further.

		TODO: rotation not implemented in transformations yet
		'''
		print("collada import")
		boundry_box = [0, 100.2, 0, 66.8, 0, 668] #default
		boundry_parts = []
		elast_pos_section = re.compile(".*<float_array id=\"(elastic.*)-mesh-positions-array\" count=\"\d+\">.*")
		liquid_pos_section = re.compile(".*<float_array id=\"(liquid.*)-mesh-positions-array\" count=\"\d+\">.*")
		bound_pos_section = re.compile(".*<float_array id=\"(boundry.*)-mesh-positions-array\" count=\"\d+\">.*")
		boundry_pattern = re.compile("boundry.*")
		section_coords = []		
		transf_section = re.compile(".*<node id=\".*\" name=\"(.*)\" type=\"NODE\">.*")
		tran_loc_sect = re.compile(".*<translate sid=\"location\">(.*)</translate>.*")
		tran_scale_sect = re.compile(".*<scale sid=\"scale\">(.*)</scale>.*")
		trans_loc = []
		trans_scale = []
		trans_axis_values = 4
		elastic_found = False
		tris_section = re.compile("\s+<p>(.*)</p>")
		tris_triplet = re.compile("(\S+)\s(\S+)\s(\S+)\s(\S+)\s(\S+)\s(\S+)\s?")
		xml_pattern = "(.*[>])+(.*)([<].*)+"
		vertex_pattern = "(\S+)\s(\S+)\s(\S+)(\s?)"
		current_transf_name = ""
		particles = []
		unsorted_connections = []
		membranes = []
		parm_memb_index = []
		elastic_connections_collection = []
		nMuscles = 1

		with open(col_file, "r") as ins:
			for line in ins:
				if elast_pos_section.match(line.rstrip()):
					p_type = 2.1
					new_particles = self.extract_particles(p_type, line, xml_pattern, vertex_pattern)
					particles.extend(new_particles)
					elastic_found = True	

					object_3d_name = elast_pos_section.match(line.rstrip()).group(1)
					section_coords.append([object_3d_name, (len(particles) - len(new_particles)), (len(particles))])
				elif liquid_pos_section.match(line.rstrip()):
					p_type = 1.1
					new_particles = self.extract_particles(p_type, line, xml_pattern, vertex_pattern)
					particles.extend(new_particles)

					object_3d_name = liquid_pos_section.match(line.rstrip()).group(1)
					section_coords.append([object_3d_name, (len(particles) - len(new_particles)), (len(particles))])
				elif bound_pos_section.match(line.rstrip()):
					p_type = 3.1
					new_particles = self.extract_particles(p_type, line, xml_pattern, vertex_pattern)
					boundry_parts.extend(new_particles)
					x1 = boundry_parts[0].position.x
					x2 = boundry_parts[4].position.x
					y1 = boundry_parts[0].position.y
					y2 = boundry_parts[2].position.y
					z1 = boundry_parts[0].position.z
					z2 = boundry_parts[1].position.z		
					boundry_box = [x1, x2, y1, y2, z1, z2]			

					object_3d_name = bound_pos_section.match(line.rstrip()).group(1)
					section_coords.append([object_3d_name, (len(particles) - len(new_particles)), (len(particles))])
				elif transf_section.match(line.rstrip()):
					current_transf_name = transf_section.match(line.rstrip()).group(1)
				elif tran_loc_sect.match(line.rstrip()):
					trans_entry = [current_transf_name]
					trans_coords = tran_loc_sect.match(line.rstrip()).group(1)
					trans_entry.extend(trans_coords.split(' '))
					trans_loc.append(trans_entry)
				elif tran_scale_sect.match(line.rstrip()):
					trans_entry = [current_transf_name]
					trans_coords = tran_scale_sect.match(line.rstrip()).group(1)
					trans_entry.extend(trans_coords.split(' '))
					trans_scale.append(trans_entry)
				elif tris_section.match(line.rstrip()) and elastic_found == True:
					for tris in re.finditer(tris_triplet, tris_section.match(line.rstrip()).group(1)):
						# create elastic connections
						particle_i_group = [ int(tris.group(1)), int(tris.group(1)), int(tris.group(3)) ]
						particle_j_group = [ int(tris.group(3)), int(tris.group(5)), int(tris.group(5)) ]
						val1 = 0.0
						for p_index in range(len(particle_j_group)):
							part_i = particles[particle_i_group[p_index]]
							part_j = particles[particle_j_group[p_index]]
							unsorted_connections.append([[int(tris.group(1)),int(tris.group(3))],[int(tris.group(1)),int(tris.group(5))],[int(tris.group(3)),int(tris.group(5))]])

						# create membranes
						membrane_triple = [int(tris.group(1)), int(tris.group(3)), int(tris.group(5))]
						if not membrane_triple in membranes:
							membranes.append(membrane_triple)
						# add blanks
					for p_i in range(len(particles)):
						total_conn = 0
						#val1 = 1.0
						found_j = []
						for con_i in range(len(unsorted_connections)):
							for connection in unsorted_connections[con_i]:
								if (p_i == connection[0] or p_i == connection[1]) and (total_conn < Const.MAX_NUM_OF_NEIGHBOUR):
									part_i = particles[p_i]
									j_index = (p_i == connection[0]) and connection[1] or connection[0]
									part_j = particles[j_index]
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
					elastic_found = False

			# create pmis
			print("particles:")
			print(float(len(particles)))
			for p_i in range(len(particles)):
				pmi_group = []
				for m_i in range(len(membranes)):
					for memb_vert in membranes[m_i]:
						if p_i == memb_vert and len(pmi_group) < Const.MAX_MEMBRANES_INCLUDING_SAME_PARTICLE:
							pmi_group.append(m_i)

				for pmi_i in pmi_group:
					parm_memb_index.append(pmi_i)

				for blank_i in range(Const.MAX_MEMBRANES_INCLUDING_SAME_PARTICLE - len(pmi_group)):
					parm_memb_index.append(-1)

			print("parm_memb_index:")
			print(len(parm_memb_index)/float(Const.MAX_MEMBRANES_INCLUDING_SAME_PARTICLE))

			# transforms	
			'''print("trans_loc")
			print(trans_loc)
			print("section_coords")
			print(section_coords)'''
			print("trans_loc")
			print(trans_loc)
			print("trans_scale")
			print(trans_scale)

			for trans in trans_scale:
				for sect in section_coords:					
					boundry_box, particles = self.translate_mesh("scale", trans, sect, boundry_pattern, boundry_box, particles)

			for trans in trans_loc:
				for sect in section_coords:
					boundry_box, particles = self.translate_mesh("position", trans, sect, boundry_pattern, boundry_box, particles)

					'''trans_3d_object = trans[0]
					sect_3d_object = sect[0]
					x_trans = float(trans[1])
					y_trans = float(trans[2])
					z_trans	= float(trans[3])
					if trans_3d_object == sect_3d_object and boundry_pattern.match(trans_3d_object):
						print("boundry_box")
						print(boundry_box)
						print('x_trans')
						print(float(trans[2]))
						print(float(trans[4]))
						print(x_trans)
						print('y_trans')	
						print(y_trans)
						boundry_box[0] += x_trans
						boundry_box[1] += x_trans
						boundry_box[2] += y_trans
						boundry_box[3] += y_trans
						boundry_box[4] += z_trans
						boundry_box[5] += z_trans
						print("boundry_box")
						print(boundry_box)						
					elif trans_3d_object == sect_3d_object:
						sect_start = sect[1]
						sect_end = sect[2]
						for i in range(sect_end - sect_start):
							offset_i = i+sect_start
							particles[offset_i].position.x += x_trans
							particles[offset_i].position.y += y_trans
							particles[offset_i].position.z += z_trans'''

		return boundry_box, particles, elastic_connections_collection, membranes, parm_memb_index

	def export_conf(self, out_file, boundry_box, conf_file_group):

		output_f = open(out_file,"w")

		for bb_point in boundry_box:
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
				output_f.write("[membranes]\n")
			elif i == 3:
				output_f.write("[particleMemIndex]\n")								
			elif i == 4:
				output_f.write("[end]\n")

		output_f.close()