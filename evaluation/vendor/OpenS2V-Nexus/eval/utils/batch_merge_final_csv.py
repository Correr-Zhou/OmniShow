import os
import json
import pandas as pd

# Directory containing JSON files
eval_type = "Single-Domain"  # [Open-Domain, Human-Domain, Single-Object]
json_folder = "single_domain/0_merge"
output_path = f"{eval_type}.csv"

# Create an empty list to store each record
data = []

if eval_type == "Human-Domain":
    # Loop through each JSON file in the directory
    for filename in os.listdir(json_folder):
        if filename.endswith(".json"):
            with open(os.path.join(json_folder, filename), "r") as file:
                # Load the JSON data
                json_data = json.load(file)

                # Extract the necessary fields from the JSON
                model_name = filename.split(".")[0]
                total_score = json_data.get("total_score", None)
                aes_score = json_data.get("aes_score", None)
                motion_smoothness = json_data.get("motion_smoothness", None)
                motion_amplitude = json_data.get("motion_amplitude", None)
                facesim_score = json_data.get("facesim_cur", None)
                gme_score = json_data.get("gme_score", None)
                natural_score = json_data.get("natural_score", None)

                # Create a dictionary for this record
                record = {
                    "Model": model_name,
                    "Venue": "Closed-Source",  # Assuming "Closed-Source" for now, you can modify if needed
                    "Evaluated by": "OpenS2V Team",  # Assuming "OpenS2V Team", you can modify if needed
                    "TotalScore↑": f"{round(total_score * 100, 2)}%"
                    if total_score is not None
                    else None,
                    "Aesthetics↑": f"{round(aes_score * 100, 2)}%"
                    if aes_score is not None
                    else None,
                    "MotionSmoothness↑": f"{round(motion_smoothness * 100, 2)}%"
                    if motion_smoothness is not None
                    else None,
                    "MotionAmplitude↑": f"{round(motion_amplitude * 100, 2)}%"
                    if motion_amplitude is not None
                    else None,
                    "FaceSim↑": f"{round(facesim_score * 100, 2)}%"
                    if facesim_score is not None
                    else None,
                    "GmeScore↑": f"{round(gme_score * 100, 2)}%"
                    if gme_score is not None
                    else None,
                    "NaturalScore↑": f"{round(natural_score * 100, 2)}%"
                    if natural_score is not None
                    else None,
                }

                # Append the record to the data list
                data.append(record)
else:
    # Loop through each JSON file in the directory
    for filename in os.listdir(json_folder):
        if filename.endswith(".json"):
            with open(os.path.join(json_folder, filename), "r") as file:
                # Load the JSON data
                json_data = json.load(file)

                # Extract the necessary fields from the JSON
                model_name = filename.split(".")[0]
                total_score = json_data.get("total_score", None)
                aes_score = json_data.get("aes_score", None)
                motion_smoothness = json_data.get("motion_smoothness", None)
                motion_amplitude = json_data.get("motion_amplitude", None)
                facesim_score = json_data.get("facesim_cur", None)
                gme_score = json_data.get("gme_score", None)
                natural_score = json_data.get("natural_score", None)
                nexus_score = json_data.get("nexus_score", None)

                # Create a dictionary for this record
                record = {
                    "Model": model_name,
                    "Venue": "Closed-Source",  # Assuming "Closed-Source" for now, you can modify if needed
                    "Evaluated by": "OpenS2V Team",  # Assuming "OpenS2V Team", you can modify if needed
                    "TotalScore↑": f"{round(total_score * 100, 2)}%"
                    if total_score is not None
                    else None,
                    "Aesthetics↑": f"{round(aes_score * 100, 2)}%"
                    if aes_score is not None
                    else None,
                    "MotionSmoothness↑": f"{round(motion_smoothness * 100, 2)}%"
                    if motion_smoothness is not None
                    else None,
                    "MotionAmplitude↑": f"{round(motion_amplitude * 100, 2)}%"
                    if motion_amplitude is not None
                    else None,
                    "FaceSim↑": f"{round(facesim_score * 100, 2)}%"
                    if facesim_score is not None
                    else None,
                    "GmeScore↑": f"{round(gme_score * 100, 2)}%"
                    if gme_score is not None
                    else None,
                    "NexusScore↑": f"{round(nexus_score * 100, 2)}%"
                    if nexus_score is not None
                    else None,
                    "NaturalScore↑": f"{round(natural_score * 100, 2)}%"
                    if natural_score is not None
                    else None,
                }

                # Append the record to the data list
                data.append(record)

# Create a DataFrame from the data list
df = pd.DataFrame(data)

# Save the DataFrame to a CSV file
df.to_csv(output_path, index=False)
