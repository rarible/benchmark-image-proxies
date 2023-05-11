# Image proxy resizers benchmark

```
for i in /sys/devices/system/cpu/cpu?; do echo performance > $i/cpufreq/scaling_governor; done
git clone https://github.com/rarible/benchmark-image-proxies
cd benchmark-image-proxies
docker-compose up -d
./benchmark.sh
```
