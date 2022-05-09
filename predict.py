from mrcnn.config import Config
import mrcnn.model as modellib
import slidingwindow as sw
import pandas as pd



def generate_sw(np_image, patch_size, patch_overlap):
    if patch_overlap > 1:
        raise ValueError("Patch overlap {} must be between 0 - 1".format(patch_overlap))
    windows = sw.generate(np_image,
                          sw.DimOrder.HeightWidthChannel,
                          patch_size,
                          patch_overlap)
    return windows


def predict_image(img, model, patch=True, patch_size=500):
    if patch:
        windows = generate_sw(img, patch_size=patch_size, patch_overlap=0)
        coord_df = pd.DataFrame(columns=[
            "window",
            "xmin",
            "ymin",
            "xmax",
            "ymax",
            "score"])

        for index, window in enumerate(windows):
            crop = img[windows[index].indices()]
            result = model.detect([crop])
            if result is None:
                continue
            else:
                xmin, ymin, xmax, ymax = windows[index].getRect()
            for i in range(len(result[0]['rois'])):
                coord = result[0]['rois'][i]
                score = result[0]['scores'][i]
                new_row = [
                        index,
                        coord[1] + xmin,
                        coord[0] + ymin,
                        coord[3] + xmin,
                        coord[2] + ymin,
                        score
                ]
                coord_df = coord_df.append(pd.Series(
                    new_row, index=coord_df.columns), ignore_index=True)
    else:
        coord_df = pd.DataFrame(columns=[
            "xmin",
            "ymin",
            "xmax",
            "ymax",
            "score"
        ])
        result = model.detect([img])

        for i in range(len(result[0]['rois'])):
            coord = result[0]['rois'][i]
            score = result[0]['scores'][i]
            new_row = [
                coord[1],
                coord[0],
                coord[3],
                coord[2],
                score
            ]
            coord_df = coord_df.append(pd.Series(
                    new_row, index=coord_df.columns), ignore_index=True)

    coord_df["xcenter"] = get_x_center(coord_df["xmin"], coord_df["xmax"])
    coord_df["ycenter"] = get_y_center(coord_df["ymin"], coord_df["ymax"])

    return coord_df


def get_x_center(xmin, xmax):
    return (xmin + xmax) * 0.5

def get_y_center(ymin, ymax):
    return (ymin + ymax) * 0.5