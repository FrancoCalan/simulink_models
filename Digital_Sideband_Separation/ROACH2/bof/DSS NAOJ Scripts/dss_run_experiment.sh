#!/bin/bash
#./initialize_raoch.sh
#./calibrate_adc5g.sh
#./synchronize_adc5g.py
#./dss_hotcold_multilo.py
#./send_telegram.py "DSS test started."
./dss_calibrate_multilo.py
#./send_telegram.py "Finished with calibration."
./dss_compute_srr_multilo.py
#./send_telegram.py "Test finished!"
