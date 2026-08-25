import os
import sys
import cv2
import numpy as np

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ml_dir = os.path.join(base_dir, "Project Code (forensic face sketch)", "Project Code (forensic face sketch)", "ThirdEye v2", "ml_service")
sys.path.insert(0, ml_dir)

from app import crop_face

p = r"C:\Users\Mallikarjun Gala\Downloads\40800910494_1f2f50da79_q.jpg"
img = cv2.imread(p)
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
cropped = crop_face(img_rgb, target_size=160)

h, w = cropped.shape[:2]
grey = cv2.cvtColor(cropped, cv2.COLOR_RGB2GRAY)

# Lower face (mustache & beard)
lower_face = grey[int(h * 0.55):int(h * 0.90), int(w * 0.20):int(w * 0.80)]
forehead = grey[int(h * 0.05):int(h * 0.35), int(w * 0.25):int(w * 0.75)]
eyebrows = grey[int(h * 0.25):int(h * 0.45), int(w * 0.20):int(w * 0.80)]

lf_mean = float(np.mean(lower_face))
lf_std = float(np.std(lower_face))
fh_mean = float(np.mean(forehead))
eb_mean = float(np.mean(eyebrows))

print(f"Lower Face (Beard/Mustache) Mean: {lf_mean:.2f}, Std: {lf_std:.2f}")
print(f"Forehead Mean: {fh_mean:.2f}")
print(f"Eyebrows Mean: {eb_mean:.2f}")
print(f"Lower Face vs Forehead darkness diff: {fh_mean - lf_mean:.2f}")
