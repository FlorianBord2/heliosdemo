from influxdb import InfluxDBClient
import json

class Influx:

	def __init__(self, path):
		fd = open(path)
		f = fd.read()
		conf = json.loads(f)
		print(conf)
		self.cl = InfluxDBClient(conf['db_adresse'], conf['port'], conf['user'], conf['password'], conf['db'])
		self.tol = conf['tolerence_min']
		self.db = conf['db']

	def _getCenter(self, tab):
		x = (tab[0] + tab[2]) / 2
		y = (tab[1] + tab[3]) / 2
		return x,y


	def _save2(self, data):
		#[[836, 644, 1062, 763, 2, 0.599301], [902, 380, 1136, 482, 2, 0.63929075], [837, 27, 962, 250, 2, 0.87451226]]
		street = {}
		street['rue1'] = 0
		street['rue2'] = 0
		for frame in data:
			if frame[5] >= self.tol:
				x = (frame[0] + frame[2]) / 2
				y = (frame[1] + frame[3]) / 2
				print ('x:', x, ' y:', y)
				#rue = maptopix(x, y)
				if y <= 300:
					rue = 'rue 1'
					street['rue1'] = street['rue1'] + 1
				else:
					rue = 'rue 2'
					street['rue2'] = street['rue2'] + 1
				self._save_entity(x, y, rue, frame[4], frame[5])
		for each in street:
			self._save_total(each, street[each])

	def _save_total(self, street, total):
		json_body = [
			{
				"measurement": 'total',
				"tags": {
					"type": 'car',
					"street": street
					},
					"fields": {
						"value": total
						}
			}
		]
		try:
			self.cl.write_points(json_body)
		except:
			self.cl.create_database(self.db)
			self.cl.write_points(json_body)

	def _save_entity(self, x, y, street, e_type, tol):
		json_body = [
			{
				"measurement": 'entity',
				"tags": {
					"x": x,
					"y": y,
					"street": street,
					"type": e_type
					},
					"fields": {
						"value": tol
						}
			}
		]
		try:
			self.cl.write_points(json_body)
		except:
			self.cl.create_database(self.db)
			self.cl.write_points(json_body)


	def _saveN(self, data):
		i = 0
		for each in data['detection_scores']:
			if each > self.tol:
				i = i + 1
		print('Sur la frame on a =', i)
		json_body = [
			{
				"measurement": "teste3",
				"tags": {
					"type":2
			},
				"fields": {
					"value": i
					}
				}
			]
		self.cl.write_points(json_body)

