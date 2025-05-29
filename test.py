import os
import requests
import subprocess

def decompress_z_file(z_path):
    try:
        subprocess.run(['gzip', '-d', z_path], check=True)
        print(f"Decompressed: {z_path}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to decompress {z_path}: {e}")



def downloader(gps_week, gps_day, days):
    os.makedirs("uploads", exist_ok=True)

    for i in range(days):
        day = gps_day + i
        sp3_filename = f"igr{gps_week}{day}.sp3.Z"
        clk_filename = f"igr{gps_week}{day}.clk.Z"

        sp3_url = f"https://cddis.nasa.gov/archive/gnss/products/{gps_week}/{sp3_filename}"
        clk_url = f"https://cddis.nasa.gov/archive/gnss/products/{gps_week}/{clk_filename}"

        sp3_path = os.path.join("uploads", sp3_filename)
        clk_path = os.path.join("uploads", clk_filename)

        try:
            sp3_response = requests.get(sp3_url)
            sp3_response.raise_for_status()
            with open(sp3_path, "wb") as f:
                f.write(sp3_response.content)
            print(f"SP3 file for day {day} of GPS week {gps_week} downloaded successfully.")
        except requests.HTTPError as e:
            print(f"Failed to download SP3 file for day {day}: {e}")

        try:
            clk_response = requests.get(clk_url)
            clk_response.raise_for_status()
            with open(clk_path, "wb") as f:
                f.write(clk_response.content)
            print(f"CLK file for day {day} of GPS week {gps_week} downloaded successfully.")
        except requests.HTTPError as e:
            print(f"Failed to download CLK file for day {day}: {e}")

        
        decompress_z_file(sp3_path)
        decompress_z_file(clk_path)
    

# Example usage
downloader(1610, 3, 2)
