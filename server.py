from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)


# Function to get ship info
def get_ship_info(ship_name, ship_info_path, fuel_data, pip_path):
    try:
        # Load the ship-info CSV file into a DataFrame
        ship_info_df = pd.read_csv(ship_info_path)

        # Search for the ship by name (case-insensitive)
        ship_row = ship_info_df[ship_info_df['Ship Name'].str.strip().str.lower() == ship_name.strip().lower()]

        if not ship_row.empty:
            # Extract the relevant information
            ship_type = ship_row.iloc[0]['Type']
            grt = ship_row.iloc[0]['Grt']

            banned = False

            # Calculate fuel burned per hour
            if ship_type in fuel_data:
                fuel_consumption = fuel_data[ship_type]
                fuel_burned_per_hour = float(grt) * fuel_consumption / 1000  # Convert kilos to tons
                if fuel_burned_per_hour > 100:
                    banned = True
            else:
                fuel_burned_per_hour = "Fuel consumption data not available for this ship type."

            # Load the PIP CSV file to count ship appearances
            pip_df = pd.read_csv(pip_path)

            # Count the number of times the ship appears in the PIP file
            ship_visits = 1 + pip_df[pip_df['Ship Name'].str.strip().str.lower() == ship_name.strip().lower()].shape[0]



            # Calculate total fuel burned based on visits
            if isinstance(fuel_burned_per_hour, (int, float)):
                total_fuel_burned = fuel_burned_per_hour * ship_visits
                if total_fuel_burned > 1000:
                    banned = True
            else:
                total_fuel_burned = "Cannot calculate total fuel burned due to missing fuel consumption data."

            ship_info = {
                'Ship Name': ship_row.iloc[0]['Ship Name'],
                'Type': ship_type,
                'GRT': grt,
                'Fuel Burned Per Hour (tons)': fuel_burned_per_hour,
                'Number of Visits': ship_visits,
                'Total Fuel Burned (tons)': total_fuel_burned,
                'Banned': banned
            }
            return ship_info
        else:
            return {'error': f"Ship '{ship_name}' not found in the ship-info file."}
    except FileNotFoundError as e:
        return {'error': f"File not found: {e.filename}"}
    except KeyError as e:
        return {'error': f"Missing column in CSV: {e}"}
    except Exception as e:
        return {'error': f"An error occurred: {e}"}


# Flask route to handle requests
@app.route('/get_ship_info', methods=['GET'])
def get_ship_info_endpoint():
    ship_name = request.args.get('ship_name')
    if not ship_name:
        return jsonify({'error': 'Please provide a ship name using the "ship_name" query parameter.'}), 400

    # File paths
    ship_info_path = r'ship-info.csv'
    pip_path = r'PIP.csv'

    # Fuel consumption data
    fuel_data = {
        'FREIGHTER': 10,
        'CRUISE': 15,
        'MISCELLANEOUS': 12,
        'TUG': 35,
        'FERRY': 12,
        'DREDGER': 25,
        'FUEL BARGE': 5,
        'MISC BARGE': 5,
        'WAVE PIERCING CRAFT': 20,
        'STEAMBOAT': 20
    }

    # Get ship info
    result = get_ship_info(ship_name, ship_info_path, fuel_data, pip_path)
    return jsonify(result)


# Function to calculate fuel burned for all ships in the PIP file
def calculate_fuel_burned_over_year(ship_info_path, fuel_data, pip_path):
    try:
        # Load the ship-info CSV file into a DataFrame
        ship_info_df = pd.read_csv(ship_info_path)

        # Load the PIP CSV file into a DataFrame
        pip_df = pd.read_csv(pip_path)

        # Normalize ship names in both DataFrames for case-insensitive matching
        ship_info_df['Ship Name'] = ship_info_df['Ship Name'].str.strip().str.lower()
        pip_df['Ship Name'] = pip_df['Ship Name'].str.strip().str.lower()

        # Count the number of visits for each ship in the PIP file
        ship_visits = pip_df['Ship Name'].value_counts()

        # Prepare a list to store results
        results = []

        # Iterate over each ship in the ship-info DataFrame
        for _, row in ship_info_df.iterrows():
            ship_name = row['Ship Name']
            ship_type = row['Type']
            grt = row['Grt']

            # Check if the ship appears in the PIP file
            if ship_name in ship_visits.index:
                visits = ship_visits[ship_name]

                # Calculate fuel burned per hour
                if ship_type in fuel_data:
                    fuel_consumption = fuel_data[ship_type]
                    fuel_burned_per_hour = float(grt) * fuel_consumption / 1000  # Convert kilos to tons
                    total_fuel_burned = fuel_burned_per_hour * visits
                else:
                    fuel_burned_per_hour = None
                    total_fuel_burned = None

                # Append the result
                results.append({
                    'Ship Name': row['Ship Name'],
                    'Type': ship_type,
                    'GRT': grt,
                    'Number of Visits': visits,
                    'Fuel Burned Per Hour (tons)': fuel_burned_per_hour,
                    'Total Fuel Burned (tons)': total_fuel_burned
                })

        # Convert results to a DataFrame
        results_df = pd.DataFrame(results)
        return results_df
    except FileNotFoundError as e:
        return {'error': f"File not found: {e.filename}"}
    except KeyError as e:
        return {'error': f"Missing column in CSV: {e}"}
    except Exception as e:
        return {'error': f"An error occurred: {e}"}


# Flask route to handle requests for all ships
@app.route('/get_all_ships_fuel', methods=['GET'])
def get_all_ships_fuel_endpoint():
    # File paths
    ship_info_path = r'c:\Users\klsha\Programming\Hack Pompey 25 sea change\ship-info.csv'
    pip_path = r'c:\Users\klsha\Programming\Hack Pompey 25 sea change\PIP.csv'

    # Fuel consumption data
    fuel_data = {
        'FREIGHTER': 10,
        'CRUISE': 15,
        'MISCELLANEOUS': 12,
        'TUG': 35,
        'FERRY': 12,
        'DREDGER': 25,
        'FUEL BARGE': 5,
        'MISC BARGE': 5,
        'WAVE PIERCING CRAFT': 20,
        'STEAMBOAT': 20
    }

    # Calculate fuel burned for all ships
    results_df = calculate_fuel_burned_over_year(ship_info_path, fuel_data, pip_path)

    # Convert the DataFrame to JSON and return it
    results_df.to_csv('Brendan.csv')
    return results_df.to_json(orient='records')


# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
