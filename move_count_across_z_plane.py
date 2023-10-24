import os
from pathlib import Path
from multiprocessing import Pool, cpu_count
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#
TRAJECTORY_DIR = Path.cwd()/"trajectory"

#@@@@@@@@@@@@@@@ INPUT FILE @@@@@@@@@@@@@@@#

def read_config(file_name):
    config = {}
    run_flag = False

    with open(file_name, 'r') as f:
        for line in f:
            line = line.strip()  # remove whitespace

            if not line or line.startswith('#'):
                continue

            if line.startswith('#'):  # skip empty lines and comments
                    continue
            if not line:
                    run_flag_second = False
            parts = line.split(None, 1)
            if len(parts) < 2:
                continue
            if len(parts) > 3:
                continue
            key, value = parts
            if "MOVE_COUNT_ACROSS_Z .true." in line:
                run_flag = True
            config[key.strip()] = value.strip()
    return config, run_flag

# def read_config_times(file_name):
#     config_times = {}
#     with open(file_name, 'r') as f:
#         for line in f:
#             line = line.strip()
#             if "nstana" not in line:
#                 run_flag_times = False
#             if "nedana" not in line:
#                 run_flag_times = False
#             if "intana" not in line:
#                 run_flag_times = False
#             if line.startswith('#'):  # skip empty lines and comments
#                 continue
#             if not line:
#                 break
#             key, value = line.split()
#             config_times[key.strip()] = value.strip()

#     return config_times, run_flag_times
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#
def extract_atom_positions(file_name):
    atom_positions = {}
    with open(file_name, 'r') as file:
        for line in file:
            tokens = line.split()
            if len(tokens) == 9:  # Assuming all the lines with atom info have 9 tokens
                atom_id, mol, atom_type = map(int, [tokens[0], tokens[1], tokens[2]])
                x, y, z = map(float, [tokens[3], tokens[4], tokens[5]])
                ix, iy, iz = map(int, [tokens[6], tokens[7], tokens[8]])

                if atom_type == ATOM_TYPE_number:
                    atom_positions[atom_id] = float(z)
    return atom_positions
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#
def count_crossings(old_positions, new_positions):
    upward_move = 0
    downward_move = 0
    for atom_id, old_z in old_positions.items():
        new_z = new_positions.get(atom_id)
        if old_z < float(z_point_of_intersection) and new_z >= float(z_point_of_intersection):
            upward_move += 1
        elif old_z >= float(z_point_of_intersection) and new_z < float(z_point_of_intersection):
            downward_move += 1
    return upward_move, downward_move
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#
def process_pair(trajectory_pair):
    old_positions = extract_atom_positions(trajectory_pair[0])
    new_positions = extract_atom_positions(trajectory_pair[1])

    return count_crossings(old_positions, new_positions)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#
def extract_time_from_filename(filename):
    """Extract time value from the filename."""
    return int(filename.split('_')[1].split('.')[0])
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#
def extract_time_from_filename(filename):
    return int(filename.split('_')[1].split('.')[0])

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#
def main():
    all_files = sorted([os.path.join(TRAJECTORY_DIR, f) for f in os.listdir(TRAJECTORY_DIR) if f.endswith('.lammpstrj')])
    all_files = [
        f for f in all_files 
        if nstana <= extract_time_from_filename(os.path.basename(f)) <= nedana
        and (extract_time_from_filename(os.path.basename(f)) - nstana) % intana == 0
    ]
    num_cores = cpu_count()

    with Pool(num_cores) as pool:
        results = pool.map(process_pair, zip(all_files[:-1], all_files[1:]))

    with open(Path.cwd()/"output_analysis"/f"move_count_across_z={z_point_of_intersection}.csv", 'w') as f:
        f.write("time(ns),atoms_upward,atoms_downward\n")
        for (file1, file2), (upward_moves, downward_moves) in zip(zip(all_files[:-1], all_files[1:]), results):
            time_value = extract_time_from_filename(os.path.basename(file2))  # Extracting time from the second file in the pair
            f.write(f"{time_value/(10**6):.7f},{upward_moves},{downward_moves}\n")
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#
if __name__ == '__main__':

    config, should_run = read_config(f"{Path.cwd()}/analysis.inp")
    if not should_run:
        print("MOVE_COUNT_ACROSS_Z directive is not active in analysis.inp. Exiting program.")
        exit()

    # config_times, run_flag_times = read_config_times(f"{Path.cwd()}/analysis.inp")
    # if not run_flag_times:
    #     print("Error in Time Settings. Exiting program.")
    #     exit()

    ATOM_TYPE_number = int(config['ATOM_TYPE_number'])
    z_point_of_intersection = config['z_point_of_intersection']
    nstana = int(config['nstana'])
    nedana = int(config['nedana'])
    intana = int(config['intana'])
    
    main()