from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process():
    town = request.form["locationInput"].upper()

    # List of valid towns
    valid_towns = ['ANG MO KIO', 'BEDOK', 'BISHAN', 'BUKIT BATOK', 'BUKIT MERAH', 
                   'BUKIT PANJANG', 'BUKIT TIMAH', 'CENTRAL AREA', 'CHOA CHU KANG', 
                   'CLEMENTI', 'GEYLANG', 'HOUGANG', 'JURONG EAST', 'JURONG WEST', 
                   'KALLANG/WHAMPOA', 'MARINE PARADE', 'PASIR RIS', 'PUNGGOL', 
                   'QUEENSTOWN', 'SEMBAWANG', 'SENGKANG', 'SERANGOON', 'TAMPINES', 
                   'TOA PAYOH', 'WOODLANDS', 'YISHUN']

    if town in valid_towns:
        # Import the appropriate town module dynamically
        module_name = f"templates.resale_hdb_{town.lower().replace('/', '_').replace(' ', '_')}"
        town_module = __import__(module_name, fromlist=['analyze_town_data'])

        from templates.resale_hdb_var import HDBDataLoader, filter_by_date, DATASET_ID

        loader = HDBDataLoader(DATASET_ID)
        df = loader.download_file()
        filtered_df = filter_by_date(df)
        filtered_df['price_per_sqm'] = filtered_df['resale_price'] / filtered_df['floor_area_sqm']
        fourfive_filtered_df = filtered_df[filtered_df['flat_type'].isin(['4 ROOM', '5 ROOM'])]

        import io
        import base64
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_svg import FigureCanvasSVG

        # Create the plot
        fig = Figure(figsize=(12, 8))
        result = town_module.analyze_town_data(fourfive_filtered_df, fig=fig)
        
        # Convert plot to SVG
        output = io.StringIO()
        FigureCanvasSVG(fig).print_svg(output)
        result['svg'] = output.getvalue()
        
        return jsonify(result)
    return jsonify({"error": "Town not found"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)