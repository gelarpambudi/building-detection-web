import pandas as pd
import cv2
import os
from osgeo import osr, gdal
from matplotlib import pyplot as plt
from matplotlib import patches
from werkzeug.utils import secure_filename
from app import app


def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def load_image(img_path):
  img = cv2.imread(img_path)
  return img

def save_image(np_img, save_path):
  cv2.imwrite(save_path, np_img)

def save_req_image(img_file):
    filename = secure_filename(img_file.filename)
    img_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return os.path.join(app.config['UPLOAD_FOLDER'], filename)

def load_raster(img_path):
    raster = gdal.Open(img_path)
    src_srs=osr.SpatialReference()
    src_srs.ImportFromWkt(raster.GetProjection())
    tgt_srs = src_srs.CloneGeogCS()
    return raster, src_srs, tgt_srs


def get_corner_coord(raster):
    xmin, xpixel, _, ymin, _, ypixel = raster.GetGeoTransform()
    width, height = raster.RasterXSize, raster.RasterYSize
    xmax = xmin + (width * xpixel)
    ymax = ymin + (height * ypixel)
    return (xmin, ymax), (xmax, ymax), (xmax, ymin), (xmin, ymin)

def get_space_coord(xoffset, px_w, rot1, yoffset, px_h, rot2, x, y):
    posX = px_w * x + rot1 * y + xoffset
    posY = rot2 * x + px_h * y + yoffset
    posX += px_w / 2.0
    posY += px_h / 2.0
    return posX, posY

def get_lonlat_df(coords, raster, src_references, target_references):
    lonlat_df = pd.DataFrame(columns=["lat", "lon", "score"])

    transform =  osr.CoordinateTransformation(src_references, target_references)
    xoffset, px_w, rot1, yoffset, rot2, px_h = raster.GetGeoTransform()

    for index, row in coords.iterrows():
        posX, posY = get_space_coord(
            xoffset,
            px_w,
            rot1,
            yoffset,
            px_h,
            rot2, 
            row['xcenter'], row['ycenter']
        )
        lon,lat,z = transform.TransformPoint(posX, posY)
        new_row = [lat, lon, row['score']]
        lonlat_df = lonlat_df.append(pd.Series(
                    new_row, index=lonlat_df.columns), ignore_index=True)

    return lonlat_df

def plot_bbox(img, bbox_df, color=[0,0,255], thickness=4):
    for index,row in bbox_df.iterrows():
        y1, x1 = int(row['ymin']), int(row['xmin'])
        y2, x2 = int(row['ymax']), int(row['xmax'])
        cv2.rectangle(img, (x1,y1), (x2,y2), color, thickness, cv2.LINE_AA)