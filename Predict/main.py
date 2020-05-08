import sys,os
import cv2
from influx import Influx
from PIL import Image
import numpy as np
#YoloPath
sys.path.append('.')

from keras_yolo3.yolo import YOLO, detect_video

def model(data):
	return YOLO(**data)

class Predictor:
	def __init__(self,model,path):
		self.model = model
		self.path = path
		self._load()
		self.inf = Influx('./influx_conf.json')

	def __del__(self,):
		self.model.close_session()

	def _load(self,):
		self.vid = cv2.VideoCapture(self.path)
		if not self.vid.isOpened():
			raise IOError("Couldn't open webcam or video")

	def run(self,):
		while self.vid.isOpened():
			fdata, frame = self.vid.read()
			if not fdata:
				break
			frame = frame[:, :, ::-1]
			image = Image.fromarray(frame)
			out_pred, image = self.model.detect_image(image,
				show_stats=False)
			#Enregistrement des infos
			print(out_pred)
			self.inf._save2(out_pred)
			#fin de l'enregistrement
			result = np.asarray(image)
			cv2.namedWindow("VIDEO", cv2.WINDOW_NORMAL)
			cv2.imshow("VIDEO", result)
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break
		self.vid.release()


def main():
	if len(sys.argv)!=3:
		print('Error: Number of arguments')
		return
	m_model = model({
		"model_path": sys.argv[1],
		"anchors_path": './FilesToPred/yolo_anchors.txt',
		"classes_path": './FilesToPred/data_classes.txt',
		"score": 0.2,
		"gpu_num": 1,
		"model_image_size": (416, 416),
	})
	Predictor(m_model,sys.argv[2]).run()

if __name__ == "__main__":
	main()