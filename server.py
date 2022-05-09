from flask import request, render_template, flash, redirect
from image_processing import *
import pandas as pd
from predict import predict_image
from dir_utils import list_dir
from location_utils import add_location_to_df
from app import app
import model
import tensorflow as tf

building_detection_model = model.load_model("./model/maskrcnn_model_complete.h5")
graph = tf.get_default_graph()

@app.route("/", methods=['GET'])
@app.route("/home", methods=['GET'])
def home():
    if request.method == "GET":
        return render_template("home.html")


@app.route("/faq", methods=['GET'])
def faq():
    if request.method == "GET":
        return render_template("faq.html")


@app.route("/predict", methods=['GET','POST'])
def predict():
    global graph
    with graph.as_default():
        if request.method == "POST":
            if 'files' not in request.files:
                flash(u'No file part')
                return redirect(request.url)

            file = request.files['files']
            patch_size = int(request.form['patch_size'])

            if file and allowed_file(file.filename):
                img_path = save_req_image(file)

                np_img = load_image(img_path)

                coordinates_result = predict_image(
                    np_img,
                    building_detection_model,
                    patch=True,
                    patch_size=patch_size
                )

                raster, source_raster, target_raster = load_raster(img_path)

                lonlat_df = get_lonlat_df(
                    coordinates_result[["xcenter", "ycenter", "score"]],
                    raster,
                    source_raster,
                    target_raster
                )

                plot_bbox(np_img, coordinates_result[["xmin", "ymin", "xmax", "ymax"]])

                lonlat_df = add_location_to_df(lonlat_df)
                save_image(np_img, os.path.join(
                    app.config['RESULTS_FOLDER'], 
                    'result-'+ os.path.splitext(file.filename)[0]+'.png'))
                lonlat_df.to_csv(os.path.join(app.config['RESULTS_FOLDER'], 'result-'+ os.path.splitext(file.filename)[0]+'.csv'))

                return render_template(
                    "predict.html",
                    img_path=os.path.join('results/', 'result-'+ os.path.splitext(file.filename)[0]+'.png'),
                    filename='result-'+ os.path.splitext(file.filename)[0]+'.png',
                    tables=[lonlat_df.to_html(classes='data', header="true")]
                )
            else:
                flash(u'Allowed image type is tif')
                return redirect(request.url)

        elif request.method == "GET":
            return render_template("predict.html")


@app.route("/results", methods=['GET'])
def results():
    if request.method == "GET":
        path = app.config['RESULTS_FOLDER']
        is_load_image = request.args.get("is_load_image", default="False", type=bool)
        if is_load_image == True:
            img_name = request.args.get("img_name")
            lonlat_df = pd.read_csv(
                os.path.join(app.config['RESULTS_FOLDER'], os.path.splitext(img_name)[0]+'.csv'),
                index_col=[0]
            )
            print('results/'+img_name)
            return render_template(
                'results.html',
                tree=list_dir(path),
                load_image=True,
                img_path='results/'+img_name,
                tables=[lonlat_df.to_html(classes='data', header="true")])
        else:
            return render_template('results.html', tree=list_dir(path), load_image=False)

if __name__ == "__main__":
    app.run(debug=True, host='localhost', port='8080')