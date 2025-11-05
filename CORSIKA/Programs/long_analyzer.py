# This program processes CORSIKA's raw longitudinal output files (DAT######.long) and generates two formatted data files:
#   - OUT######.txt : contains longitudinal particle and energy deposit information
#   - PAR######.txt : contains fitted Gaisser–Hillas parameters

import re
import os

input_path = "DAT402141.long"
output_out_path = "OUT40214.txt"
output_par_path = "PAR40214.txt"

generate_out = not os.path.exists(output_out_path)
generate_par = not os.path.exists(output_par_path)

if not (generate_out or generate_par):
    print("Os arquivos de saída já existem. Nenhuma ação necessária.")
else:
    with open(input_path, "r") as file_in:
        out_data = []
        par_data = []
        shower_data = []
        current_shower = 1

        in_particle_section = False
        in_energy_section = False
        in_hillas_section = False

        start_line = "LONGITUDINAL DISTRIBUTION IN   205 VERTICAL STEPS OF    5. G/CM**2 FOR SHOWER"
        depth_line = "DEPTH     GAMMAS  POSITRONS  ELECTRONS       MU+           MU-     HADRONS     CHARGED     NUCLEI  CHERENKOV"
        end_line_1 = "LONGITUDINAL ENERGY DEPOSIT IN   205 VERTICAL STEPS OF    5. G/CM**2 FOR SHOWER"
        hillas_start = "FIT OF THE HILLAS CURVE"
        shower_end_line = "# End of shower"

        for line in file_in:
            line = line.strip()

            if line.startswith(start_line):
                if shower_data and generate_out:
                    out_data.extend(shower_data)
                    out_data.append(f"{shower_end_line} {current_shower}.")
                    current_shower += 1

                shower_data = [
                    f"# SHOWER {current_shower}",
                    "# Longitudinal particle distribution for 205 levels:"
                ]
                in_particle_section = True
                in_energy_section = False
                in_hillas_section = False
                continue

            if line.startswith(end_line_1):
                in_particle_section = False
                in_energy_section = True
                shower_data.append("# Energy deposit distribution for 205 levels:")
                continue

            if line.startswith(hillas_start):
                in_particle_section = False
                in_energy_section = False
                in_hillas_section = True
                hillas_params = []
                continue

            if in_particle_section:
                if line.startswith(depth_line):
                    continue
                if line:
                    shower_data.append(line)

            elif in_energy_section:
                if "DEPTH" in line and "GAMMA" in line:
                    continue
                if line:
                    shower_data.append(line)

            elif in_hillas_section:
                if "PARAMETERS" in line:
                    hillas_params = re.findall(r"[-+]?\d*\.\d+E[+-]\d+", line)

                if hillas_params and len(hillas_params) >= 6:
                    if generate_out:
                        shower_data.append(f"# Hillas parameters: {' '.join(hillas_params)}")
                    if generate_par:
                        par_data.append(" ".join(hillas_params[:6]))
                    in_hillas_section = False

        if shower_data and generate_out:
            out_data.extend(shower_data)
            out_data.append(f"{shower_end_line} {current_shower}.")

    if generate_out:
        with open(output_out_path, "w") as file_out:
            file_out.write("\n".join(out_data))
        print(f"Arquivo gerado: {output_out_path} ({current_shower} chuveiros processados).")

    if generate_par:
        with open(output_par_path, "w") as file_par:
            file_par.write("\n".join(par_data))
        print(f"Arquivo gerado: {output_par_path} ({len(par_data)} chuveiros processados).")
