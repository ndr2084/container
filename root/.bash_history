python3
ll /nvme/
ls /nvme/
ls /nvme/wqz/kubernetes-scheduler-simulator/
cd /nvme/wqz/kubernetes-scheduler-simulator/
git status
ll
ls -l
cd 
ll
ls -l
vim .bashrc
vi .bashrc .
vi .bashrc 
apt
wget https://go.dev/dl/go1.20.4.linux-amd64.tar.gz # https://go.dev/dl/
apt install wget
apt update
apt install wget
apt install vim
ll
vim .bashrc
source .bashrc
ll
go version
wget https://go.dev/dl/go1.20.4.linux-amd64.tar.gz # https://go.dev/dl/
wget https://go.dev/dl/go1.20.4.linux-amd64.tar.gz # https://go.dev/dl/
 rm -rf /usr/local/go && tar -C /usr/local -xzf go1.20.4.linux-amd64.tar.gz
vim .bashrc
vim /etc/pro
vim /etc/profile
go version
go version
ll /usr/local/bin/
ll /usr/local/go/
ll /usr/local/go/bin/
ll /usr/local/go/bin/go
/usr/local/go/bin/go
vim .bashrc
cd 
ll
vim .bashrc
source .bashrc
go 
go version
ll
du -hd 1 .
ls
ll
cd 
ll
cp -r /nvme/wqz/kubernetes-scheduler-simulator .
ll
cd kubernetes-scheduler-simulator/
ll
go mod vendor
ll
./bin/simon
$ bin/simon apply --extended-resources "gpu"                   -f example/test-cluster-config.yaml                   -s example/test-scheduler-config.yaml
bin/simon apply --extended-resources "gpu"                   -f example/test-cluster-config.yaml                   -s example/test-scheduler-config.yaml
cat requirements.txt 
pip
pip version
pip --version
python
pip install -r requirements.txt 
ll
htop
top
top
ll
tail -f experiments/2023_0511/openb_pod_list_default/01-Random/1.3/42/log-cc_owdefault_dr0.0_tn1.3_ts42_if1.0_md0ac0.yaml-sc_Random1000_deshare_gsrandom_md3c66.yaml.log 
ll
ll
rm -rf experiments/2023_0511
ll
cd experiments/
ll
ll
cd plot/
ll
ll expected_results/
rm paib_frag_*.pdf
ll
ll expected_results/
cp ../analysis/expected_results/* .
ll
ll ../
ll ../analysis/
ll ../analysis/expected_results/
ll ../analysis/analysis_
ll ../analysis/analysis_results/
#cp ../analysis/expected_results/* .
ll
vim ../analysis/expected_results/analysis_allo_discrete.csv 
#cp ../analysis/expected_results/* .
cp ../analysis/expected_results/* .
ll
rm analysis_*
ll
ls -l
ls -la
cp ../analysis/expected_results/* .
ll
python3 plot_openb_alloc.py 
ll
cp openb_alloc.pdf /nvme/wqz/kubernetes-scheduler-simulator
ll
rm openb_alloc.pdf 
rm analysis_*
ll
cd ..
ll
cd analysis/
ls -la
ll analysis_results/
ll -a analysis_results/
cd ..
ll
ll -la run_scripts/
ll 
..
cd ..
ll
cd ..
ll
ll
cd 
ll
cd go
ll
ll
ll pkg/
cd ..
rm -rf go
ll
ll
#rm go1.20.4.linux-amd64.tar.gz 
ll
rm go1.20.4.linux-amd64.tar.gz 
ll
cd kubernetes-scheduler-simulator/
ll
cp -f /nvme/wqz/kubernetes-scheduler-simulator/bin/simon* bin/
ll
ll bin/
bin/simon apply --extended-resources "gpu"                   -f example/test-cluster-config.yaml                   -s example/test-scheduler-config.yaml
ll
ll
# pwd: kubernetes-scheduler-simulator/experiments
python run_scripts/generate_run_scripts.py > run_scripts/run_scripts_0511.sh
ll
cd experiments/
python run_scripts/generate_run_scripts.py > run_scripts/run_scripts_0511.sh
vim run_scripts/run_scripts_0511.sh 
ll
cd ..
ll
cd experiments/
ll
ll ../data/
ll ../
cd ..
head -2 experiments/run_scripts/run_scripts_0511.sh 
head -3 experiments/run_scripts/run_scripts_0511.sh 
head -4 experiments/run_scripts/run_scripts_0511.sh 
head -5 experiments/run_scripts/run_scripts_0511.sh 
ll experiments/
EXPDIR="experiments/2023_0511/openb_pod_list_default/01-Random/1.3/42" && mkdir -p ${EXPDIR} && touch "${EXPDIR}/terminal.out" && python3 scripts/generate_config_and_run.py -d "${EXPDIR}" -e -b -f data/openb_pod_list_default -Random 1000 -gpusel random -tune 1.3 -tuneseed 42 --shuffle-pod=true -z "${EXPDIR}/snapshot/ds01" | tee -a "${EXPDIR}/terminal.out" && python3 scripts/analysis.py -f -g ${EXPDIR} | tee -a "${EXPDIR}/terminal.out"
ll
EXPDIR="experiments/2023_0511/openb_pod_list_default/01-Random/1.3/42" && mkdir -p ${EXPDIR} && touch "${EXPDIR}/terminal.out" && python3 scripts/generate_config_and_run.py -d "${EXPDIR}" -e -b -f data/openb_pod_list_default -Random 1000 -gpusel random -tune 1.3 -tuneseed 42 --shuffle-pod=true -z "${EXPDIR}/snapshot/ds01" | tee -a "${EXPDIR}/terminal.out" && python3 scripts/analysis.py -f -g ${EXPDIR} | tee -a "${EXPDIR}/terminal.out"
ll
