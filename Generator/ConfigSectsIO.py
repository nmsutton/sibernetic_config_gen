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

from Particle import Particle, Float4
from Const import Const
from ElasticConnection import ElasticConnection
import re
import math as math

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
		'''
		Reserved for future use of importing physics values
		for each individual particle
		'''
		part_phys_mod = []

		if phy_file != '': 
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

	def translate_mesh(self, trans_scale, trans_loc, section_coords, sect_patterns, boundry_box, particles):
		elastic_pattern = sect_patterns[0]
		liquid_pattern = sect_patterns[1]
		boundry_pattern = sect_patterns[2]
		offset_counter = 0
		elastic_offset = 0
		for sect in section_coords:
			sect_3d_object = sect[0]
			if elastic_pattern.match(sect_3d_object): elastic_offset = sect[2]

		for t_i in range(len(trans_scale)):
			trans_3d_object = trans_loc[t_i][0]
			x_p_trans = float(trans_loc[t_i][1])
			y_p_trans = float(trans_loc[t_i][2])
			z_p_trans	= float(trans_loc[t_i][3])
			x_s_trans = float(trans_scale[t_i][1])
			y_s_trans = float(trans_scale[t_i][2])
			z_s_trans	= float(trans_scale[t_i][3])			

			if boundry_pattern.match(trans_3d_object):
				#scale
				boundry_box[0] *= x_s_trans
				boundry_box[1] *= x_s_trans
				boundry_box[2] *= y_s_trans
				boundry_box[3] *= y_s_trans
				boundry_box[4] *= z_s_trans
				boundry_box[5] *= z_s_trans						
				#position
				boundry_box[0] += x_p_trans
				boundry_box[1] += x_p_trans
				boundry_box[2] += y_p_trans
				boundry_box[3] += y_p_trans
				boundry_box[4] += z_p_trans
				boundry_box[5] += z_p_trans

			for sect in section_coords:
				sect_3d_object = sect[0]					
				if trans_3d_object == sect_3d_object:
					if liquid_pattern.match(trans_3d_object):
						sect_start = sect[1] + elastic_offset + offset_counter
						sect_end = sect[2] + elastic_offset + offset_counter
						offset_counter += sect[2]
					else:
						sect_start = sect[1]
						sect_end = sect[2]

					for i in range(sect_end - sect_start):
						offset_i = i+sect_start
						#scale
						particles[offset_i].position.x *= x_s_trans
						particles[offset_i].position.y *= y_s_trans
						particles[offset_i].position.z *= z_s_trans
						#position
						particles[offset_i].position.x += x_p_trans
						particles[offset_i].position.y += y_p_trans
						particles[offset_i].position.z += z_p_trans						

		''' 
		Code below for potential rotation interpreting from
		collada files

		# precalculate Sin - Cos
		angx = 0; angy = 0; angz = 0
		cx = math.cos(angx); sx = math.sin(angx) 
		cy = math.cos(angy); sy = math.sin(angy) 
		cz = math.cos(angz); sz = math.sin(angz) 

		# rotate x-axis
		x1=x
		y1=(cx*y)+(sx*z)
		z1=(sx*z)-(cx*y)

		# rotate y-axis
		x2=(cy*x1)+(sy*z1)
		y2=y1
		z2=(sy*z1)-(cy*x1)

		# rotate z-axis
		x1=(cz*x2)+(sz*y2)
		y1=(cz*y2)+(sz*x2)
		z1=z2					
		'''

		return boundry_box, particles		

	def calc_part_val1(self, particles, part_i, part_j, nMuscles):
		val1 = 0
		dx2 = part_i.position.x - part_j.position.x
		dy2 = part_i.position.y - part_j.position.y
		dz2 = part_i.position.z - part_j.position.z
		dx2 *= dx2
		dy2 *= dy2
		dz2 *= dz2 
		nMi = particles.index(part_i)*nMuscles/len(particles);
		val1 = (1.1+nMi)*float((dz2 > 100*dx2)and(dz2 > 100*dy2)) 

		return val1

	def calc_ptype(self, muscle_particles, p_i, p_j):
		val1 = 0.0
		if ([p_i, p_j] in muscle_particles) or ([p_j, p_i] in muscle_particles):
			val1 = 1.1#0.0#96.5#1.1

		return val1		

	def sort_conns(self, new_conns):
		for i in range(len(new_conns)):
			for i2 in range(len(new_conns)):
				if (new_conns[i].r_ij<new_conns[i2].r_ij):
					temp_conn = new_conns[i]					
					new_conns[i] = new_conns[i2]
					new_conns[i2] = temp_conn

		return new_conns

	def export_faces(self, out_file, membranes):
		output_f = open(out_file,"w")

		for face_i in range(len(membranes)):
			p1 = (float(membranes[face_i][0]))
			p2 = (float(face_i))
			p3 = (float(membranes[face_i][1]))
			p4 = (float(face_i))
			p5 = (float(membranes[face_i][2]))
			p6 = (float(face_i))
			output_f.write(str(p1)+" "+str(p2)+" "+str(p3)+" "+str(p4)+" "+str(p5)+" "+str(p6)+" ")

		output_f.close()

	def import_collada(self, col_file, dist_scalar, dist_exp):
		'''
		Importing boundry box assumes box verticies are in collada file in format vertice 1-8 =
		(0 0 0) (0 0 1) (0 1 0) (0 1 1) (1 0 0) (1 0 1) (1 1 0) (1 1 1)

		Importing collada transforms need 'TransRotLoc' and not 'Matrix' style 
		transforms currently

		TODO: rotation not implemented in transformations yet

		Currently only importing one elastic mesh and boundry box is supported.  Multiple 
		liquid meshes can be imported.

		The size of elastic_connections_collection = [None]*Const.MAX_NUM_OF_NEIGHBOUR*len(particles)*3
		is a heuristic which provides enough size in the list to random access indices before the real
		list values are created, in order to add the real values.  It is the max connections that could exist.
		'''
		print("collada import")
		boundry_box = [0, 100.2, 0, 66.8, 0, 668] #default
		boundry_parts = []
		elast_pos_section = re.compile(".*<float_array id=\"(elastic.*)-mesh-positions-array\" count=\"\d+\">.*")
		liquid_pos_section = re.compile(".*<float_array id=\"(liquid.*)-mesh-positions-array\" count=\"\d+\">.*")
		bound_pos_section = re.compile(".*<float_array id=\"(boundry.*)-mesh-positions-array\" count=\"\d+\">.*")
		material_section = re.compile(".*<polylist material=\"(.*)-material\" count=\"\d+\">.*")
		geo_section_end = re.compile(".*</geometry>.*")
		elastic_pattern = re.compile("elastic.*") 
		liquid_pattern = re.compile("liquid.*")
		boundry_pattern = re.compile("boundry.*")
		sect_patterns = [elastic_pattern, liquid_pattern, boundry_pattern]
		section_coords = []		
		transf_section = re.compile(".*<node id=\".*\" name=\"(.*)\" type=\"NODE\">.*")
		tran_loc_sect = re.compile(".*<translate sid=\"location\">(.*)</translate>.*")
		tran_scale_sect = re.compile(".*<scale sid=\"scale\">(.*)</scale>.*")
		trans_loc = []
		trans_scale = []
		trans_axis_values = 4
		elastic_found = False
		ptype_found = False
		tris_section = re.compile("\s+<p>(.*)</p>")
		tris_triplet = re.compile("(\S+)\s(\S+)\s(\S+)\s(\S+)\s(\S+)\s(\S+)\s?")
		xml_pattern = "(.*[>])+(.*)([<].*)+"
		vertex_pattern = "(\S+)\s(\S+)\s(\S+)(\s?)"
		current_transf_name = ""
		current_ptype_name = ""
		elastic_particles = []
		liquid_particles = []
		particles = []
		unsorted_connections = []
		membranes = []
		parm_memb_index = []
		elastic_connections_collection = []
		nMuscles = 1
		muscle_particles = []

		with open(col_file, "r") as ins:
			for line in ins:
				if elast_pos_section.match(line.rstrip()):
					p_type = 2.1
					new_particles = self.extract_particles(p_type, line, xml_pattern, vertex_pattern)
					elastic_particles.extend(new_particles)
					elastic_found = True	

					object_3d_name = elast_pos_section.match(line.rstrip()).group(1)
					section_coords.append([object_3d_name, 0, len(new_particles)])
					particles.extend(elastic_particles)					
				elif liquid_pos_section.match(line.rstrip()):
					p_type = 1.1
					new_particles = self.extract_particles(p_type, line, xml_pattern, vertex_pattern)
					liquid_particles.extend(new_particles)

					object_3d_name = liquid_pos_section.match(line.rstrip()).group(1)
					section_coords.append([object_3d_name, 0, len(new_particles)])
				elif bound_pos_section.match(line.rstrip()):
					p_type = 3.1
					new_particles = self.extract_particles(p_type, line, xml_pattern, vertex_pattern)
					boundry_parts.extend(new_particles)

					x_b, y_b, z_b = [], [], []
					for i in range(len(boundry_parts)):
						x_b.append(boundry_parts[i].position.x)
						y_b.append(boundry_parts[i].position.y)
						z_b.append(boundry_parts[i].position.z)
					x_b.sort(); y_b.sort(); z_b.sort()

					x1, x2, y1, y2, z1, z2 = x_b[0], x_b[-1], y_b[0], y_b[-1], z_b[0], z_b[-1]
					boundry_box = [x1, x2, y1, y2, z1, z2]			

					object_3d_name = bound_pos_section.match(line.rstrip()).group(1)
				elif material_section.match(line.rstrip()):
					current_ptype_name = material_section.match(line.rstrip()).group(1)
					ptype_found = True
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
						# read in elastic connections
						p1 = int(tris.group(1))
						p3 = int(tris.group(3))
						p5 = int(tris.group(5))
								
						unsorted_connections.append([[p1,p3],[p1,p5],[p3,p5]])

						# create membranes
						membrane_triple = [p1, p3, p5]
						if not membrane_triple in membranes:
							membranes.append(membrane_triple)

						# find muscles
						if ptype_found == True and current_ptype_name == "muscle":
							muscle_particles.append([p1,p3])
							muscle_particles.append([p1,p5])
							muscle_particles.append([p3,p5])
					ptype_found = False

				if geo_section_end.match(line.rstrip()) and elastic_found == True:
					# after unsorted_connections is filled up now elastic connections are created
					for p_i in range(len(particles)):
						total_conn = 0
						found_j = []
						new_conns = []
						conn_1 = 0
						conn_2 = 0
						for con_i in range(len(unsorted_connections)):
							for connection in unsorted_connections[con_i]:
								conn_1 = connection[0]
								conn_2 = connection[1]
								if (p_i == conn_1 or p_i == conn_2) and (total_conn < Const.MAX_NUM_OF_NEIGHBOUR):
									part_i = particles[p_i]
									j_index = (p_i == conn_1) and conn_2 or conn_1
									part_j = particles[j_index]
									if not j_index in found_j:
										#val1 = self.calc_part_val1(particles, part_i, part_j, nMuscles)
										val1 = self.calc_ptype(muscle_particles, p_i, j_index)
										dist = ((Particle.distBetween_particles(part_j,part_i)**float(dist_exp)) * float(dist_scalar))
										new_conns.append( ElasticConnection(particles.index(part_j)+0.2, dist, val1, 0) )
										found_j.append(j_index)
										total_conn += 1

						sorted_conns = self.sort_conns(new_conns)
						elastic_connections_collection.extend(sorted_conns)
						elastic_connections_collection.extend([ElasticConnection(Const.NO_PARTICEL_ID,0,0,0)] * (Const.MAX_NUM_OF_NEIGHBOUR - total_conn))

					elastic_found = False

			particles.extend(liquid_particles)

			# create pmis
			print("particles:")
			print(float(len(particles)))
			for p_i in range(len(particles)):
				if particles[p_i].type == 2.1:
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
			boundry_box, particles = self.translate_mesh(trans_scale, trans_loc, section_coords, sect_patterns, boundry_box, particles)

			# test removing sections
			#membranes = []
			#parm_memb_index = []
			#elastic_connections_collection = []

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