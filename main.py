from flask import Flask, request, render_template, jsonify, send_from_directory
import matplotlib.pyplot as plt

app = Flask(__name__, static_folder='static')


@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/process", methods=["POST"])
def process():
    town = request.form["locationInput"].upper()

    # List of valid towns
    valid_towns = [
        'ANG MO KIO', 'BEDOK', 'BISHAN', 'BUKIT BATOK', 'BUKIT MERAH',
        'BUKIT PANJANG', 'BUKIT TIMAH', 'CENTRAL AREA', 'CHOA CHU KANG',
        'CLEMENTI', 'GEYLANG', 'HOUGANG', 'JURONG EAST', 'JURONG WEST',
        'KALLANG/WHAMPOA', 'MARINE PARADE', 'PASIR RIS', 'PUNGGOL',
        'QUEENSTOWN', 'SEMBAWANG', 'SENGKANG', 'SERANGOON', 'TAMPINES',
        'TOA PAYOH', 'WOODLANDS', 'YISHUN'
    ]

    if town in valid_towns:
        # Import the appropriate town module dynamically
        module_name = f"templates.resale_hdb_{town.lower().replace('/', '_').replace(' ', '_')}"
        town_module = __import__(module_name, fromlist=['analyze_town_data'])

        from templates.resale_hdb_var import HDBDataLoader, filter_by_date, DATASET_ID

        loader = HDBDataLoader(DATASET_ID)
        df = loader.download_file()
        filtered_df = filter_by_date(df)
        filtered_df['price_per_sqm'] = filtered_df[
            'resale_price'] / filtered_df['floor_area_sqm']
        fourfive_filtered_df = filtered_df[filtered_df['flat_type'].isin(
            ['4 ROOM', '5 ROOM'])]

        # Create the plot using the modified analyze_town_data function
        fig = town_module.analyze_town_data(fourfive_filtered_df)
        # Save the plot to a file
        image_filename = f"{town.lower().replace('/', '_').replace(' ', '_')}_analysis.png"
        fig.savefig(f"static/{image_filename}")
        plt.close(fig)  # Close the figure to free memory

        # Get latest median price
        latest_data = fourfive_filtered_df[
            fourfive_filtered_df['town'] == town].sort_values(
                'month', ascending=False).iloc[0]
        latest_median_price = round(latest_data['price_per_sqm'], 2)

        return jsonify({
            "status": "success",
            "image": image_filename,
            "median_price": latest_median_price
        })

    return jsonify({"error": "Town not found", "status": "error"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
