import os
import json


def merge_scores_files(folder_path):
    merged_data = {}

    json_files = [f for f in os.listdir(folder_path) if f.endswith(".json")]

    for json_file in json_files:
        file_path = os.path.join(folder_path, json_file)
        score_name = json_file.replace(".json", "")

        with open(file_path, "r") as f:
            data = json.load(f)

            for video_id, video_data in data.items():
                if video_id not in merged_data:
                    merged_data[video_id] = {}

                merged_data[video_id][score_name] = video_data

    for video_id, scores in merged_data.items():
        if "aesthetic_score" in scores:
            aes_dict = scores["aesthetic_score"]
            if isinstance(aes_dict, dict) and "aes_score" in aes_dict:
                scores["aes_score"] = aes_dict["aes_score"]
            del scores["aesthetic_score"]

        if "motion_amplitude" in scores:
            motion_dict = scores["motion_amplitude"]
            if isinstance(motion_dict, dict) and "motion_fb" in motion_dict:
                scores["motion_amplitude"] = motion_dict["motion_fb"]

        if "motion_smoothness" in scores:
            motion_dict = scores["motion_smoothness"]
            if isinstance(motion_dict, dict) and "motion_smoothness" in motion_dict:
                scores["motion_smoothness"] = motion_dict["motion_smoothness"]

        if "facesim" in scores:
            face_dict = scores["facesim"]
            if isinstance(face_dict, dict) and "cur_score" in face_dict:
                scores["facesim_cur"] = face_dict["cur_score"]
            del scores["facesim"]

        if "gmescore" in scores:
            gme_dict = scores["gmescore"]
            if isinstance(gme_dict, dict) and "gme_score" in gme_dict:
                scores["gme_score"] = gme_dict["gme_score"]
            del scores["gmescore"]

        if "nexusscore" in scores:
            nexus_dict = scores["nexusscore"]
            if isinstance(nexus_dict, dict) and "nexus_score" in nexus_dict:
                scores["nexus_score"] = nexus_dict["nexus_score"]
            del scores["nexusscore"]

        natural_scores = []
        for key in ["naturalscore_1", "naturalscore_2", "naturalscore_3"]:
            val = scores.get(key)
            if val is not None:
                natural_scores.append(float(val))
            if key in scores:
                del scores[key]
        if natural_scores:
            scores["natural_score"] = sum(natural_scores) / len(natural_scores)

    return merged_data


def process_scores(data, eval_type):
    total_aes_score = total_facesim_cur = total_gme_score = total_motion_amplitude = (
        total_motion_smoothness
    ) = total_nexus_score = total_natural_score = 0
    count_aes_score = count_facesim_cur = count_gme_score = count_motion_amplitude = (
        count_motion_smoothness
    ) = count_nexus_score = count_natural_score = 0

    min_aes_score = 4
    max_aes_score = 7
    min_motion_amplitude = 0
    max_motion_amplitude = 1
    min_motion_smoothness = 0
    max_motion_smoothness = 1
    min_facesim_cur = 0
    max_facesim_cur = 1
    min_gme_score = 0
    max_gme_score = 1
    min_nexus_score = 0
    max_nexus_score = 0.05
    min_natural_score = 1
    max_natural_score = 5

    for key, value in data.items():
        if "aes_score" in value:
            aes_score = max(min(value["aes_score"], max_aes_score), min_aes_score)
            total_aes_score += aes_score
            count_aes_score += 1

        if "motion_amplitude" in value:
            motion_amplitude = min(abs(value["motion_amplitude"]), max_motion_amplitude)
            total_motion_amplitude += motion_amplitude
            count_motion_amplitude += 1

        if "motion_smoothness" in value:
            motion_smoothness = min(
                abs(value["motion_smoothness"]), max_motion_smoothness
            )
            total_motion_smoothness += motion_smoothness
            count_motion_smoothness += 1

        if "facesim_cur" in value:
            facesim_cur = min(value["facesim_cur"], max_facesim_cur)
            total_facesim_cur += facesim_cur
            count_facesim_cur += 1

        if "gme_score" in value:
            gme_score = min(value["gme_score"], max_gme_score)
            total_gme_score += gme_score
            count_gme_score += 1

        if "nexus_score" in value and value["nexus_score"] != 0:
            nexus_score = min(value["nexus_score"], max_nexus_score)
            total_nexus_score += nexus_score
            count_nexus_score += 1

        if "natural_score" in value:
            natural_score = max(
                min(value["natural_score"], max_natural_score), min_natural_score
            )
            total_natural_score += natural_score
            count_natural_score += 1

    avg_aes_score = total_aes_score / count_aes_score if count_aes_score else 0
    avg_motion_amplitude = (
        total_motion_amplitude / count_motion_amplitude if count_motion_amplitude else 0
    )
    avg_motion_smoothness = (
        total_motion_smoothness / count_motion_smoothness
        if count_motion_smoothness
        else 0
    )
    avg_facesim_cur = total_facesim_cur / count_facesim_cur if count_facesim_cur else 0
    avg_gme_score = total_gme_score / count_gme_score if count_gme_score else 0
    avg_nexus_score = total_nexus_score / count_nexus_score if count_nexus_score else 0
    avg_natural_score = (
        total_natural_score / count_natural_score if count_natural_score else 0
    )

    aes_score = (avg_aes_score - min_aes_score) / (max_aes_score - min_aes_score)
    motion_amplitude = (avg_motion_amplitude - min_motion_amplitude) / (
        max_motion_amplitude - min_motion_amplitude
    )
    motion_smoothness = (avg_motion_smoothness - min_motion_smoothness) / (
        max_motion_smoothness - min_motion_smoothness
    )
    facesim_cur = (avg_facesim_cur - min_facesim_cur) / (
        max_facesim_cur - min_facesim_cur
    )
    gme_score = (avg_gme_score - min_gme_score) / (max_gme_score - min_gme_score)
    nexus_score = (avg_nexus_score - min_nexus_score) / (
        max_nexus_score - min_nexus_score
    )
    natural_score = (avg_natural_score - min_natural_score) / (
        max_natural_score - min_natural_score
    )

    if eval_type != "Human-Domain":
        total_score = (
            0.16 * aes_score
            + 0.06 * motion_smoothness
            + 0.02 * motion_amplitude
            + 0.20 * facesim_cur
            + 0.12 * gme_score
            + 0.20 * nexus_score
            + 0.24 * natural_score
        )
        return {
            "total_score": total_score,
            "aes_score": aes_score,
            "motion_smoothness": motion_smoothness,
            "motion_amplitude": motion_amplitude,
            "facesim_cur": facesim_cur,
            "gme_score": gme_score,
            "nexus_score": nexus_score,
            "natural_score": natural_score,
        }
    else:
        total_score = (
            0.18 * aes_score
            + 0.09 * motion_smoothness
            + 0.03 * motion_amplitude
            + 0.25 * facesim_cur
            + 0.15 * gme_score
            + 0.30 * natural_score
        )
        return {
            "total_score": total_score,
            "aes_score": aes_score,
            "motion_smoothness": motion_smoothness,
            "motion_amplitude": motion_amplitude,
            "facesim_cur": facesim_cur,
            "gme_score": gme_score,
            "natural_score": natural_score,
        }


# eval_type = "Open-Domain"  # [Open-Domain, Human-Domain, Single-Object]
# input_json_folder = "/mnt/workspace/ysh/Code/ConsisID-X/0_util_codes/OpenS2V-Nexus/eval/smoothness_results/open_domain/keling_1.6"
# output_json_path = f"/mnt/workspace/ysh/Code/ConsisID-X/0_util_codes/OpenS2V-Nexus/eval/smoothness_results/open_domain/0_merge/keling_1.6_{eval_type}.json"

# merged_score = merge_scores_files(input_json_folder)
# process_score = process_scores(merged_score, eval_type)

# with open(output_json_path, "w") as output_file:
#     json.dump(process_score, output_file, indent=4)

# print(f"Processed and saved: {output_json_path}")

eval_type = "Single-Domain"  # [Open-Domain, Human-Domain, Single-Object]
base_input_json_folder = "single_domain"
output_base_json_path = "single_domain/0_merge"


def process_multiple_folders(base_input_folder, output_base_folder, eval_type):
    for folder_name in os.listdir(base_input_folder):
        folder_path = os.path.join(base_input_folder, folder_name)

        if os.path.isdir(folder_path):
            input_json_folder = folder_path
            output_json_path = os.path.join(
                output_base_folder, f"{folder_name}_{eval_type}.json"
            )

            print(f"Processing folder: {folder_name}")
            merged_score = merge_scores_files(input_json_folder)
            process_score = process_scores(merged_score, eval_type)

            with open(output_json_path, "w") as output_file:
                json.dump(process_score, output_file, indent=4)

            print(f"Processed and saved: {output_json_path}")


process_multiple_folders(base_input_json_folder, output_base_json_path, eval_type)
