import os
from mrcnn.config import Config
import mrcnn.model as modellib


class InferenceConfig(Config):
    BACKBONE = 'resnet50' #backbone used in training
    GPU_COUNT = 1 #number of gpu used
    IMAGES_PER_GPU = 1 #number of images processed per gpu
    NUM_CLASSES = 1+1 #number of class (building and background/non-building)
    IMAGE_MIN_DIM = 640 #minimum image dimension
    IMAGE_MAX_DIM = 640 #maximum image dimension
    USE_MINI_MASK = True #enable/disable mini mask
    MAX_GT_INSTANCES = 300
    DETECTION_MAX_INSTANCES = 10
    DETECTION_MIN_CONFIDENCE = 0.9
    NAME='SpaceNet'

def load_model(model_path):
    trained_model = modellib.MaskRCNN(
        mode="inference",
        config=InferenceConfig(),
        model_dir=os.path.dirname(model_path)
    )
    trained_model.load_weights(model_path, by_name=True)
    return trained_model
