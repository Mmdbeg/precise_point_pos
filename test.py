import os
import requests

def downloader(gps_week, gps_day, days):
    os.makedirs("uploads", exist_ok=True)  

    for i in range(days):
        day = gps_day + i
        url = f"https://cddis.nasa.gov/archive/gnss/products/{gps_week}/igr{gps_week}{(gps_day)+i}.sp3.Z"

        
        file_path = f"uploads/igr{gps_week}{(gps_day)+i}.sp3.Z"

        response = requests.get(url, auth=(None, None))
        response.raise_for_status()

        with open(file_path, "wb") as f:
            f.write(response.content)

        print(f"sp3 file for day {day} of GPS week {gps_week} download completed")

downloader(1610, 3, 2)
