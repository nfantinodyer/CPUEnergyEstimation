#CSEN283
sudo apt-get update
sudo apt-get install stress-ng
sudo apt-get install gcc g++ libacl1-dev libaio-dev libapparmor-dev libatomic1 libattr1-dev libbsd-dev libcap-dev libeigen3-dev libgbm-dev libcrypt-dev libglvnd-dev libipsec-mb-dev libjpeg-dev libjudy-dev libkeyutils-dev libkmod-dev libmd-dev libmpfr-dev libsctp-dev libxxhash-dev zlib1g-dev
### CPU stress tests
#### For all cores:
stress-ng --cpu 0 --timeout 60s
- `--cpu 0`: Uses all available CPU cores.
- `--timeout 60s`: Runs the stress test for 60 seconds.

#### For a specific amount of cores (threads)
stress-ng --cpu 4 --timeout 60s
- This will use 4 CPU cores.

#### Sets a static usage
stress-ng --cpu 4 --cpu-method matrixprod --cpu-load 80 --timeout 60s
- `--cpu-method matrixprod`: Uses matrix multiplication to stress CPU.
- `--cpu-load 80`: Keeps CPU usage at 80%.

#### Other components
##### Memory
stress-ng --vm 2 --vm-bytes 1G --timeout 60s
- `--vm 2`: Starts 2 virtual memory stressors.
- `--vm-bytes 1G`: Each stressor uses 1GB of memory.
##### I/O
stress-ng --hdd 2 --timeout 60s
- Stresses the hard disk drive with 2 workers.