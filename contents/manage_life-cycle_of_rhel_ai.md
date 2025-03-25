# RHEL AI 관리

**목차**
1. [RHEL AI 업그레이드](./manage_life-cycle_of_rhel_ai.md#1-rhel-ai-업그레이드)<br>
2. [RHEL AI에 패키지 설치](./manage_life-cycle_of_rhel_ai.md#2-rhel-ai에-패키지-설치)<br>
3. [RHEL AI 설정 관련 케이스들](./manage_life-cycle_of_rhel_ai.md#3-rhel-ai-설치-및-구성-관련)<br>
<br>
<hr>
<br>

## 1. RHEL AI 업그레이드

레드햇 포탈에서 RHEL AI의 ISO을 *rhel-ai-intel-1.4.2-1741364246-x86_64.iso* 형식을 가집니다.
* 이는 RHEL의 이미지 모드 설치 형식을 가짐
  + 이를 기반으로 실제 환경에 맞게 이미지를 빌드 필요할 수 있음
  + 기본 이미지로 사용 시에, 하드웨어 벤더 (예: nVidia)에 필요한 드라이버 / 유틸리티 등의 패키지 포함되어 있지 않는 경우가 있음
  + 특정 디바이스 파일을 찾거나 등의 에러가 발생
* 기본 설치 후, 하드웨어 벤더에 맞추어 운영체제 이미지를 업데이트 가능
  + 예) 부팅 이미지 확인
    ```
    [root@bastion ~]# podman search registry.redhat.io/rhelai1/bootc-*
    NAME                                                 DESCRIPTION
    registry.redhat.io/rhelai1/bootc-amd-rhel9           Red Hat image for bootc-amd-rhel9
    registry.redhat.io/rhelai1/bootc-nvidia-rhel9        Red Hat image for bootc-nvidia-rhel9
    registry.redhat.io/rhelai1/bootc-intel-rhel9         Red Hat image for bootc-intel-rhel9
    registry.redhat.io/rhelai1/bootc-azure-nvidia-rhel9  Red Hat image for bootc-azure-nvidia-rhel9
    registry.redhat.io/rhelai1/bootc-gcp-nvidia-rhel9    Red Hat image for bootc-gcp-nvidia-rhel9
    registry.redhat.io/rhelai1/bootc-ibm-nvidia-rhel9    Red Hat image for bootc-ibm-nvidia-rhel9
    registry.redhat.io/rhelai1/bootc-azure-amd-rhel9     Red Hat image for bootc-azure-amd-rhel9
    registry.redhat.io/rhelai1/bootc-aws-nvidia-rhel9    Red Hat image for bootc-aws-nvidia-rhel9
    
    [root@bastion ~]#
    ```
  + nVidia 하드웨어가 설치가 된 경우에, *bootc-nvidia-rhel9*로 변경
<br>

### 1.1 현재 상태 확인

#### 1.1.1 부팅 이미지 확인

```bash
sudo bootc status
```

실행결과
```yaml
apiVersion: org.containers.bootc/v1alpha1
kind: BootcHost
metadata:
  name: host
spec:
  image:
    image: registry.stage.redhat.io/rhelai1/bootc-aws-nvidia-rhel9:1.3.1
    transport: registry
  bootOrder: default
status:
  staged: null
  booted:
    image:
      image:
        image: registry.stage.redhat.io/rhelai1/bootc-aws-nvidia-rhel9:1.3.1
        transport: registry
      version: 9.20241104.0
      timestamp: null
      imageDigest: sha256:5ac008d151162e6c97f11f8e3c2523eccc0af0fb790cde8865b7d3d2a352df1a
    cachedUpdate: null
    incompatible: false
    pinned: false
    store: ostreeContainer
    ostree:
      checksum: b5da7da5ee90882e5c2de77493d3b4e142bf11aa0c58db0cc5d51b10f551b51f
      deploySerial: 0
  rollback: null
  rollbackQueued: false
  type: bootcHost
```
* 현재 시스템의 이미지
  + registry.stage.redhat.io/rhelai1/bootc-aws-nvidia-rhel9:1.3.1

#### 1.1.2 시스템의 이미지

```bash
podman images
sudo podman images
```

실행 결과
```
[instruct@bastion ~]$ podman images
REPOSITORY  TAG         IMAGE ID    CREATED     SIZE

[instruct@bastion ~]$ sudo podman images
REPOSITORY                                                 TAG               IMAGE ID      CREATED       SIZE        R/O
registry.stage.redhat.io/rhelai1/instructlab-nvidia-rhel9  1.3.1-1733951397  5a5e2ed36334  3 months ago  18.1 GB     true

[instruct@bastion ~]$
```
<br>

### 1.2 업그레이드 진행

#### 1.2.1 레지스트리 로그인

실행 명령어
```bash
sudo podman login registry.redhat.io -u=<USER_NAME> -p=<USER_PASSWORD> --authfile /etc/ostree/auth.json
```

실행 결과
```
[instruct@bastion ~]$ sudo podman login registry.redhat.io -u=<USER_NAME> -p=<USER_PASSWORD> --authfile /etc/ostree/auth.json
Login Succeeded!

[instruct@bastion ~]$ sudo cat /etc/ostree/auth.json
{
        "auths": {
                "registry.redhat.io": {
                        "auth": "...<SNIP>..."
                }
        }
}

[instruct@bastion ~]$
```

#### 1.2.2 RHEL AI 이미지 리스트

실행 명령어
```bash
sudo podman search registry.redhat.io/rhelai1/bootc
```

실행 결과
```
[instruct@bastion ~]$ sudo podman search registry.redhat.io/rhelai1/bootc
NAME                                                 DESCRIPTION
registry.redhat.io/rhelai1/bootc-amd-rhel9           Red Hat image for bootc-amd-rhel9
registry.redhat.io/rhelai1/bootc-nvidia-rhel9        Red Hat image for bootc-nvidia-rhel9
registry.redhat.io/rhelai1/bootc-intel-rhel9         Red Hat image for bootc-intel-rhel9
registry.redhat.io/rhelai1/bootc-azure-nvidia-rhel9  Red Hat image for bootc-azure-nvidia-rhel9
registry.redhat.io/rhelai1/bootc-gcp-nvidia-rhel9    Red Hat image for bootc-gcp-nvidia-rhel9
registry.redhat.io/rhelai1/bootc-ibm-nvidia-rhel9    Red Hat image for bootc-ibm-nvidia-rhel9
registry.redhat.io/rhelai1/bootc-azure-amd-rhel9     Red Hat image for bootc-azure-amd-rhel9
registry.redhat.io/rhelai1/bootc-aws-nvidia-rhel9    Red Hat image for bootc-aws-nvidia-rhel9

[instruct@bastion ~]$
```
* 부팅 이미지 형식
  + bootc-<hardware-vendor>-rhel9:<rhel-ai-version>
* 하드웨어 벤더
  + nvidia
  + amd
  + intel

#### 1.2.3 RHEL AI 이미지의 태그 리스트

실행 명령어
```bash
sudo skopeo list-tags docker://registry.redhat.io/rhelai1/bootc-aws-nvidia-rhel9 --authfile /etc/ostree/auth.json | jq -r '.Tags[]' | grep "^1.4"
```

실행 결과
```
[instruct@bastion ~]$ sudo skopeo list-tags docker://registry.redhat.io/rhelai1/bootc-aws-nvidia-rhel9 --authfile /etc/ostree/auth.json | jq -r '.Tags[]' | grep "^1.4"
1.4
1.4.0
1.4.0-source
1.4.1
1.4.1-1740489361
1.4.1-1740489361-source
1.4-1739101341
1.4-1739101341-source
1.4.1-source
1.4-source

[instruct@bastion ~]$
```

#### 1.2.4 RHEL AI의 최신 이미지로 업그레이드

실행 명령어
```bash
sudo bootc switch registry.redhat.io/rhelai1/bootc-aws-nvidia-rhel9:1.4
sudo podman images
```
* nVidia 기반 RHEL 9을 위한 이미지 1.4로 업그레이드

실행 결과
```
[instruct@bastion ~]$ sudo bootc switch registry.redhat.io/rhelai1/bootc-aws-nvidia-rhel9:1.4
layers already present: 24; layers needed: 44 (13.8 GB)
Fetched layers: 12.83 GiB in 7 minutes (32.93 MiB/s)
Queued for next boot: registry.redhat.io/rhelai1/bootc-aws-nvidia-rhel9:1.4
  Version: 9.20250213.0
  Digest: sha256:fd646d49eed80d5fed7934837b76e12ceb5cfa30dcbc787d0eecd8265d511ea8

[instruct@bastion ~]$ sudo podman images
REPOSITORY                                                 TAG               IMAGE ID      CREATED       SIZE        R/O
registry.stage.redhat.io/rhelai1/instructlab-nvidia-rhel9  1.3.1-1733951397  5a5e2ed36334  3 months ago  18.1 GB     true

[instruct@bastion ~]$
```
* 이미지는 1.3.1 버전을 보여줌

#### 1.2.5 bootc 상태 확인

실행 명령어
```bash
sudo bootc status
```

실행 결과
```yaml
apiVersion: org.containers.bootc/v1alpha1
kind: BootcHost
metadata:
  name: host
spec:
  image:
    image: registry.redhat.io/rhelai1/bootc-aws-nvidia-rhel9:1.4
    transport: registry
  bootOrder: default
status:
  staged:
    image:
      image:
        image: registry.redhat.io/rhelai1/bootc-aws-nvidia-rhel9:1.4
        transport: registry
      version: 9.20250213.0
      timestamp: null
      imageDigest: sha256:fd646d49eed80d5fed7934837b76e12ceb5cfa30dcbc787d0eecd8265d511ea8
    cachedUpdate: null
    incompatible: false
    pinned: false
    store: ostreeContainer
    ostree:
      checksum: 7bd6c3bff876879185995a5318ee838596a248d87d17b5cc87249282ee195d04
      deploySerial: 0
  booted:
    image:
      image:
        image: registry.stage.redhat.io/rhelai1/bootc-aws-nvidia-rhel9:1.3.1
        transport: registry
      version: 9.20241104.0
      timestamp: null
      imageDigest: sha256:5ac008d151162e6c97f11f8e3c2523eccc0af0fb790cde8865b7d3d2a352df1a
    cachedUpdate: null
    incompatible: false
    pinned: false
    store: ostreeContainer
    ostree:
      checksum: b5da7da5ee90882e5c2de77493d3b4e142bf11aa0c58db0cc5d51b10f551b51f
      deploySerial: 0
  rollback: null
  rollbackQueued: false
  type: bootcHost
```
* `.status.staged` 이미지
  + registry.redhat.io/rhelai1/bootc-aws-nvidia-rhel9:1.4
* `.status.booted` 이미지
  + registry.stage.redhat.io/rhelai1/bootc-aws-nvidia-rhel9:1.3.1

#### 1.2.6 RHEL AI 시스템 재부팅

실행 명령어
```bash
sudo reboot -n
```

실행 결과
```
[instruct@bastion ~]$ sudo reboot -n
...<노드 재부팅>...

[instruct@bastion ~]
```

#### 1.2.7 재부팅 후 이미지 확인

실행 명령어
```bash
sudo podman images
```

실행 결과
```
[instruct@bastion ~]$ sudo podman images
REPOSITORY                                           TAG               IMAGE ID      CREATED      SIZE        R/O
registry.redhat.io/rhelai1/instructlab-nvidia-rhel9  1.4.1-1739870750  9549237ffb9a  4 weeks ago  21.2 GB     true

[instruct@bastion ~]$
```
* 이미지 버전이 1.4.1로 바뀜

#### 1.2.8 재부팅 후 bootc 상태 확인

실행 명령어
```bash
sudo bootc status
```

실행 결과
```yaml
apiVersion: org.containers.bootc/v1alpha1
kind: BootcHost
metadata:
  name: host
spec:
  image:
    image: registry.redhat.io/rhelai1/bootc-aws-nvidia-rhel9:1.4
    transport: registry
  bootOrder: default
status:
  staged: null
  booted:
    image:
      image:
        image: registry.redhat.io/rhelai1/bootc-aws-nvidia-rhel9:1.4
        transport: registry
      version: 9.20250213.0
      timestamp: null
      imageDigest: sha256:fd646d49eed80d5fed7934837b76e12ceb5cfa30dcbc787d0eecd8265d511ea8
    cachedUpdate: null
    incompatible: false
    pinned: false
    store: ostreeContainer
    ostree:
      checksum: 7bd6c3bff876879185995a5318ee838596a248d87d17b5cc87249282ee195d04
      deploySerial: 0
  rollback:
    image:
      image:
        image: registry.stage.redhat.io/rhelai1/bootc-aws-nvidia-rhel9:1.3.1
        transport: registry
      version: 9.20241104.0
      timestamp: null
      imageDigest: sha256:5ac008d151162e6c97f11f8e3c2523eccc0af0fb790cde8865b7d3d2a352df1a
    cachedUpdate: null
    incompatible: false
    pinned: false
    store: ostreeContainer
    ostree:
      checksum: b5da7da5ee90882e5c2de77493d3b4e142bf11aa0c58db0cc5d51b10f551b51f
      deploySerial: 0
  rollbackQueued: false
  type: bootcHost
```
* `.status.booted` 이미지
  + registry.redhat.io/rhelai1/bootc-aws-nvidia-rhel9:1.4
* `.status.rollback` 이미지
  + registry.stage.redhat.io/rhelai1/bootc-aws-nvidia-rhel9:1.3.1
<br>

### 1.3 업그레이드 후 작업

#### 1.3.1 컨테이너 스토리지 구성 확인

실행 명령어
```bash
cat /etc/skel/.config/containers/storage.conf
```

storage.conf 파일 확인
```conf
[storage]
driver = "overlay"

[storage.options]
size = ""
remap-uids = ""
remap-gids = ""
ignore_chown_errors = ""
remap-user = ""
remap-group = ""
skip_mount_home = ""
mount_program = "/usr/bin/fuse-overlayfs"
mountopt = ""
additionalimagestores = [ "/usr/lib/containers/storage",]

[storage.options.overlay]
force_mask = "shared"
```

#### 1.3.2 스토리지 구성 파일을 사용자 환경으로 복사

실행 명령어
```bash
mkdir -pv .config/containers
cp /etc/skel/.config/containers/storage.conf .config/containers/
ls -lh .config/containers/storage.conf
```

실행 결과
```
[instruct@bastion ~]$ mkdir -pv .config/containers
mkdir: created directory '.config/containers'

[instruct@bastion ~]$ cp /etc/skel/.config/containers/storage.conf .config/containers/

[instruct@bastion ~]$ ls -lh .config/containers/storage.conf
-rw-r--r--. 1 instruct users 330 Mar 18 11:39 .config/containers/storage.conf

[instruct@bastion ~]$
```

#### 1.3.4 시스템 확인

실행 명령어
```bash
lscpu
free -h
lspci |grep -i nvidia
nvidia-smi --list-gpus
nvidia-smi
```

실행 결과
```
[instruct@bastion ~]$ lscpu
Architecture:             x86_64
  CPU op-mode(s):         32-bit, 64-bit
  Address sizes:          48 bits physical, 48 bits virtual
  Byte Order:             Little Endian
CPU(s):                   48
  On-line CPU(s) list:    0-47
Vendor ID:                AuthenticAMD
  Model name:             AMD EPYC 7R13 Processor
    CPU family:           25
    Model:                1
    Thread(s) per core:   2
    Core(s) per socket:   24
    Socket(s):            1
    Stepping:             1
    BogoMIPS:             5300.00
    Flags:                fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ht
                          syscall nx mmxext fxsr_opt pdpe1gb rdtscp lm constant_tsc rep_good nopl nonstop_tsc cpuid extd_apicid
                           aperfmperf tsc_known_freq pni pclmulqdq ssse3 fma cx16 pcid sse4_1 sse4_2 x2apic movbe popcnt aes xs
                          ave avx f16c rdrand hypervisor lahf_lm cmp_legacy cr8_legacy abm sse4a misalignsse 3dnowprefetch topo
                          ext ssbd ibrs ibpb stibp vmmcall fsgsbase bmi1 avx2 smep bmi2 invpcid rdseed adx smap clflushopt clwb
                           sha_ni xsaveopt xsavec xgetbv1 clzero xsaveerptr rdpru wbnoinvd arat npt nrip_save vaes vpclmulqdq r
                          dpid
Virtualization features:
  Hypervisor vendor:      KVM
  Virtualization type:    full
Caches (sum of all):
  L1d:                    768 KiB (24 instances)
  L1i:                    768 KiB (24 instances)
  L2:                     12 MiB (24 instances)
  L3:                     96 MiB (3 instances)
NUMA:
  NUMA node(s):           1
  NUMA node0 CPU(s):      0-47
Vulnerabilities:
  Gather data sampling:   Not affected
  Itlb multihit:          Not affected
  L1tf:                   Not affected
  Mds:                    Not affected
  Meltdown:               Not affected
  Mmio stale data:        Not affected
  Reg file data sampling: Not affected
  Retbleed:               Not affected
  Spec rstack overflow:   Vulnerable: Safe RET, no microcode
  Spec store bypass:      Mitigation; Speculative Store Bypass disabled via prctl
  Spectre v1:             Mitigation; usercopy/swapgs barriers and __user pointer sanitization
  Spectre v2:             Mitigation; Retpolines; IBPB conditional; IBRS_FW; STIBP always-on; RSB filling; PBRSB-eIBRS Not affe
                          cted; BHI Not affected
  Srbds:                  Not affected
  Tsx async abort:        Not affected

[instruct@bastion ~]$ free -h
               total        used        free      shared  buff/cache   available
Mem:           181Gi       2.1Gi       180Gi       1.0Mi       683Mi       179Gi
Swap:          8.0Gi          0B       8.0Gi


[instruct@bastion ~]$ lspci |grep -i nvidia
38:00.0 3D controller: NVIDIA Corporation AD104GL [L4] (rev a1)
3a:00.0 3D controller: NVIDIA Corporation AD104GL [L4] (rev a1)
3c:00.0 3D controller: NVIDIA Corporation AD104GL [L4] (rev a1)
3e:00.0 3D controller: NVIDIA Corporation AD104GL [L4] (rev a1)

[instruct@bastion ~]$ nvidia-smi --list-gpus
GPU 0: NVIDIA L4 (UUID: GPU-c2507ce8-9002-692b-09ab-a911bef79d62)
GPU 1: NVIDIA L4 (UUID: GPU-1a401bbb-397e-f2ab-8727-67ae75b10d44)
GPU 2: NVIDIA L4 (UUID: GPU-d72a67a9-98af-e739-eaaa-4f6ccbf067d6)
GPU 3: NVIDIA L4 (UUID: GPU-7575d30e-08e9-0606-7c8b-56eec2028340)

[instruct@bastion ~]$ nvidia-smi
Wed Mar 19 04:29:42 2025
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 550.144.03             Driver Version: 550.144.03     CUDA Version: 12.4     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA L4                      On  |   00000000:38:00.0 Off |                    0 |
| N/A   28C    P8             11W /   72W |       1MiB /  23034MiB |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+
|   1  NVIDIA L4                      On  |   00000000:3A:00.0 Off |                    0 |
| N/A   27C    P8             11W /   72W |       1MiB /  23034MiB |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+
|   2  NVIDIA L4                      On  |   00000000:3C:00.0 Off |                    0 |
| N/A   28C    P8             11W /   72W |       1MiB /  23034MiB |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+
|   3  NVIDIA L4                      On  |   00000000:3E:00.0 Off |                    0 |
| N/A   27C    P8             11W /   72W |       1MiB /  23034MiB |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+

+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI        PID   Type   Process name                              GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|  No running processes found                                                             |
+-----------------------------------------------------------------------------------------+

[instruct@bastion ~]$

```

#### 1.3.3 InstructLab 구성 초기화

실행 명령어
```bash
ilab config init
```

실행 결과
```
[instruct@bastion ~]$ ilab config init

----------------------------------------------------
         Welcome to the InstructLab CLI
  This guide will help you to setup your environment
----------------------------------------------------

Please provide the following values to initiate the environment [press 'Enter' for default options when prompted]
Cloning https://github.com/instructlab/taxonomy.git...

Generating config file:
    /var/home/instruct/.config/instructlab/config.yaml

INFO 2025-03-19 04:33:04,883 instructlab.config.init:259: Detecting hardware...
Please choose a system profile.
Profiles set hardware-specific defaults for all commands and sections of the configuration.
First, please select the hardware vendor your system falls into
[0] NO SYSTEM PROFILE
[1] NVIDIA
Enter the number of your choice [0]: 1
You selected: NVIDIA
Next, please select the specific hardware configuration that most closely matches your system.
[0] NO SYSTEM PROFILE
[1] NVIDIA L4 X8
[2] NVIDIA L40S X4
[3] NVIDIA L40S X8
[4] NVIDIA H100 X4
[5] NVIDIA H100 X2
[6] NVIDIA H100 X8
[7] NVIDIA A100 X4
[8] NVIDIA A100 X2
[9] NVIDIA A100 X8
Enter the number of your choice [hit enter for hardware defaults] [0]: 1
You selected: /var/home/instruct/.local/share/instructlab/internal/system_profiles/nvidia/l4/l4_x8.yaml

--------------------------------------------
    Initialization completed successfully!
  You're ready to start using `ilab`. Enjoy!

[instruct@bastion ~]$
```

#### 1.3.4 InstructLab 구성 파일 확인

실행 명령어
```bash
ilab config show | egrep -v "^[[:space:]]?+#"
```

실행 결과
```yaml
chat:
  context: default
  logs_dir: /var/home/instruct/.local/share/instructlab/chatlogs
  max_tokens:
  model: /var/home/instruct/.cache/instructlab/models/granite-3.1-8b-lab-v1
  session:
  temperature: 1.0
  vi_mode: false
  visible_overflow: true
evaluate:
  base_branch:
  base_model: /var/home/instruct/.cache/instructlab/models/granite-3.1-8b-starter-v1
  branch:
  dk_bench:
    input_questions:
    judge_model: gpt-4o
    output_dir: /var/home/instruct/.local/share/instructlab/internal/eval_data/dk_bench
    output_file_formats: jsonl
  gpus: 8
  mmlu:
    batch_size: auto
    few_shots: 5
  mmlu_branch:
    tasks_dir: /var/home/instruct/.local/share/instructlab/datasets
  model:
  mt_bench:
    judge_model: /var/home/instruct/.cache/instructlab/models/prometheus-8x7b-v2-0
    max_workers: auto
    output_dir: /var/home/instruct/.local/share/instructlab/internal/eval_data/mt_bench
  mt_bench_branch:
    judge_model: /var/home/instruct/.cache/instructlab/models/prometheus-8x7b-v2-0
    output_dir: /var/home/instruct/.local/share/instructlab/internal/eval_data/mt_bench_branch
    taxonomy_path: /var/home/instruct/.local/share/instructlab/taxonomy
  system_prompt:
  temperature: 0.0
general:
  debug_level: 0
  log_format: '%(levelname)s %(asctime)s %(name)s:%(lineno)d: %(message)s'
  log_level: INFO
  use_legacy_tmpl: false
generate:
  chunk_word_count: 1000
  max_num_tokens: 4096
  model: /var/home/instruct/.cache/instructlab/models/mixtral-8x7b-instruct-v0-1
  num_cpus: 10
  num_instructions: -1
  output_dir: /var/home/instruct/.local/share/instructlab/datasets
  pipeline: /usr/share/instructlab/sdg/pipelines/agentic
  sdg_scale_factor: 30
  seed_file: /var/home/instruct/.local/share/instructlab/internal/seed_tasks.json
  taxonomy_base: empty
  taxonomy_path: /var/home/instruct/.local/share/instructlab/taxonomy
  teacher:
    backend: vllm
    chat_template: tokenizer
    llama_cpp:
      gpu_layers: -1
      llm_family: ''
      max_ctx_size: 4096
    model_path: /var/home/instruct/.cache/instructlab/models/mixtral-8x7b-instruct-v0-1
    server:
      backend_type: ''
      current_max_ctx_size: 4096
      host: 127.0.0.1
      port: 8000
    vllm:
      gpus: 8
      llm_family: mixtral
      max_startup_attempts: 120
      vllm_args:
        - --enable-lora
        - --max-lora-rank
        - '64'
        - --dtype
        - bfloat16
        - --lora-dtype
        - bfloat16
        - --fully-sharded-loras
        - --lora-modules
        - skill-classifier-v3-clm=/var/home/instruct/.cache/instructlab/models/skills-adapter-v3
        - text-classifier-knowledge-v3-clm=/var/home/instruct/.cache/instructlab/models/knowledge-adapter-v3
metadata:
  cpu_info:
  gpu_count: 8
  gpu_family: L4
  gpu_manufacturer: Nvidia
  gpu_sku:
rag:
  convert:
    output_dir: /var/home/instruct/.local/share/instructlab/converted_documents
    taxonomy_base: origin/main
    taxonomy_path: /var/home/instruct/.local/share/instructlab/taxonomy
  document_store:
    collection_name: ilab
    uri: /var/home/instruct/.local/share/instructlab/embeddings.db
  embedding_model:
    embedding_model_path:
      /var/home/instruct/.cache/instructlab/models/ibm-granite/granite-embedding-125m-english
  enabled: false
  retriever:
    top_k: 3
serve:
  backend: vllm
  chat_template: auto
  llama_cpp:
    gpu_layers: -1
    llm_family: ''
    max_ctx_size: 4096
  model_path: /var/home/instruct/.cache/instructlab/models/granite-3.1-8b-lab-v1
  server:
    backend_type: ''
    current_max_ctx_size: 4096
    host: 127.0.0.1
    port: 8000
  vllm:
    gpus: 8
    llm_family: ''
    max_startup_attempts: 120
    vllm_args:
      - --tensor-parallel-size
      - '8'
train:
  additional_args:
    learning_rate: 6e-6
    lora_alpha: 32
    lora_dropout: 0.1
    warmup_steps: 25
    use_dolomite: true
  checkpoint_at_epoch: true
  ckpt_output_dir: /var/home/instruct/.local/share/instructlab/checkpoints
  data_output_dir: /var/home/instruct/.local/share/instructlab/internal
  data_path: /var/home/instruct/.local/share/instructlab/datasets
  deepspeed_cpu_offload_optimizer: false
  device: cuda
  disable_flash_attn: false
  distributed_backend: fsdp
  effective_batch_size: 128
  fsdp_cpu_offload_optimizer: false
  is_padding_free: false
  lora_quantize_dtype:
  lora_rank: 0
  max_batch_len: 10000
  max_seq_len: 10000
  model_path: /var/home/instruct/.cache/instructlab/models/granite-3.1-8b-starter-v1
  nproc_per_node: 8
  num_epochs: 8
  phased_base_dir: /var/home/instruct/.local/share/instructlab/phased
  phased_mt_bench_judge: /var/home/instruct/.cache/instructlab/models/prometheus-8x7b-v2-0
  phased_phase1_effective_batch_size: 128
  phased_phase1_learning_rate: 2e-05
  phased_phase1_num_epochs: 7
  phased_phase1_samples_per_save: 0
  phased_phase2_effective_batch_size: 3840
  phased_phase2_learning_rate: 6e-06
  phased_phase2_num_epochs: 10
  phased_phase2_samples_per_save: 0
  pipeline: accelerated
  save_samples: 0
  training_journal:
version: 1.0.0
```
<br>
<br>

## 2. RHEL AI에 패키지 설치

### 2.1 서브스크립션 등록

실행 명령어
```bash
sudo -i
subscription-manager register
```

실행 결과
```
[instruct@bastion ~]$ sudo -i

[root@bastion ~]# subscription-manager register
Registering to: subscription.rhsm.redhat.com:443/subscription
Username: <USER_ID>
Password: <USER_PASSWD>
The system has been registered with ID: de074957-463f-4c7d-afcc-28f310aca6f6
The registered system name is: bastion.x8b9l.internal

[root@bastion ~]#
```
<br>

### 2.2 시스템 레벨 패키지 구성

#### 2.2.1 패키지 확인

실행 명령어
```bash
rpm-ostree search pip
```

실행 결과
```
[root@bastion ~]# rpm-ostree search pip

...<snip>...
python3-pip : A tool for installing and managing Python3 packages
...<snip>...

[root@bastion ~]#
```

#### 2.2.2 패키지 설치

실행 명령어
```bash
rpm-ostree install gdb python3.12-pip strace tree
```

실행 결과
```
[root@bastion ~]# rpm-ostree install gdb python3-pip strace tree
Checking out tree 7bd6c3b... done
Enabled rpm-md repositories: rhel-9-for-x86_64-baseos-rpms rhel-9-for-x86_64-baseos-eus-rpms rhel-9-for-x86_64-appstream-rpms rhel-9-for-x86_64-appstream-eus-rpms codeready-builder-for-rhel-9-x86_64-rpms codeready-builder-for-rhel-9-x86_64-eus-rpms
Importing rpm-md... done
rpm-md repo 'rhel-9-for-x86_64-baseos-rpms' (cached); generated: 2025-03-17T18:43:21Z solvables: 8568
rpm-md repo 'rhel-9-for-x86_64-baseos-eus-rpms' (cached); generated: 2025-03-19T00:13:45Z solvables: 9307
rpm-md repo 'rhel-9-for-x86_64-appstream-rpms' (cached); generated: 2025-03-17T18:45:30Z solvables: 23716
rpm-md repo 'rhel-9-for-x86_64-appstream-eus-rpms' (cached); generated: 2025-03-19T00:16:03Z solvables: 24844
rpm-md repo 'codeready-builder-for-rhel-9-x86_64-rpms' (cached); generated: 2025-03-17T18:54:58Z solvables: 6335
rpm-md repo 'codeready-builder-for-rhel-9-x86_64-eus-rpms' (cached); generated: 2025-03-19T00:16:37Z solvables: 6669
Resolving dependencies... done
Will download: 16 packages (23.7?MB)
Downloading from 'rhel-9-for-x86_64-appstream-eus-rpms'... done
Downloading from 'rhel-9-for-x86_64-appstream-rpms'... done
Downloading from 'rhel-9-for-x86_64-baseos-rpms'... done
Importing packages... done
Checking out packages... done
Running pre scripts... done
Running post scripts... done
Running posttrans scripts... done
Writing rpmdb... done
Writing OSTree commit... done
Staging deployment... done
Added:
  boost-regex-1.75.0-8.el9.x86_64
  dnf-plugins-core-4.3.0-13.el9.noarch
  gdb-10.2-13.el9.x86_64
  gdb-headless-10.2-13.el9.x86_64
  libbabeltrace-1.5.8-10.el9.x86_64
  libipt-2.0.4-5.el9.x86_64
  libnsl2-2.0.0-1.el9.x86_64
  mpdecimal-2.5.1-3.el9.x86_64
  python3.12-3.12.1-4.el9_4.5.x86_64
  python3.12-libs-3.12.1-4.el9_4.5.x86_64
  python3.12-pip-23.2.1-4.el9.noarch
  python3.12-pip-wheel-23.2.1-4.el9.noarch
  python3.12-setuptools-68.2.2-3.el9_4.1.noarch
  source-highlight-3.1.9-11.el9.x86_64
  strace-5.18-2.el9.x86_64
  tree-1.8.0-10.el9.x86_64
Changes queued for next boot. Run "systemctl reboot" to start a reboot

[root@bastion ~]#
```

> [!NOTE]
> 주요 패키지 리스트는 다음과 같습니다.<br>
> * gdb
> * python3-pip (혹은 python3.12-pip)
> * strace
> * tree

#### 2.2.3 시스템 재부팅

실행 명령어
```bash
systemctl reboot
```

실행 결과
```
[root@bastion ~]# systemctl reboot
...<시스템 재부팅>...

[instruct@bastion ~]$
```

#### 2.2.4 사용자를 패키지 구성

실행 명령어
```bash
which pip-3.12
mkdir -pv .local/bin
ln -s /usr/bin/pip-3.12 .local/bin/pip
ls -lh .local/bin/pip
```

실행 결과
```
[instruct@bastion ~]$ which pip-3.12
/usr/bin/pip-3.12

[instruct@bastion ~]$ mkdir -pv .local/bin
mkdir: created directory '.local/bin'

[instruct@bastion ~]$ ln -s /usr/bin/pip-3.12 .local//bin/pip

[instruct@bastion ~]$ ls -lh .local/bin/pip
lrwxrwxrwx. 1 instruct users 17 Mar 19 05:03 .local/bin/pip -> /usr/bin/pip-3.12

[instruct@bastion ~]$
```
<br>

### 2.3 사용자 레벨 패키지 구성

#### 2.3.1 pip 기반 패키지 설치

실행 명령어
```bash
pip install yq
which yq
```

실행 결과
```
[instruct@bastion ~]$ pip install yq
Defaulting to user installation because normal site-packages is not writeable
Collecting yq
  Downloading yq-3.4.3-py3-none-any.whl (18 kB)
Collecting PyYAML>=5.3.1
  Downloading PyYAML-6.0.2-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (762 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 763.0/763.0 kB 12.0 MB/s eta 0:00:00
Collecting xmltodict>=0.11.0
  Downloading xmltodict-0.14.2-py2.py3-none-any.whl (10.0 kB)
Collecting tomlkit>=0.11.6
  Downloading tomlkit-0.13.2-py3-none-any.whl (37 kB)
Collecting argcomplete>=1.8.1
  Downloading argcomplete-3.6.0-py3-none-any.whl (43 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 43.8/43.8 kB 3.0 MB/s eta 0:00:00
Installing collected packages: xmltodict, tomlkit, PyYAML, argcomplete, yq
Successfully installed PyYAML-6.0.2 argcomplete-3.6.0 tomlkit-0.13.2 xmltodict-0.14.2 yq-3.4.3

[instruct@bastion ~]$ which yq
~/.local/bin/yq

[instruct@bastion ~]$
```

#### 2.3.2 사용자 홈 디렉터리

실행 명령어
```bash
pwd
tree -Fa -L 3 .
```

실행 결과
```
[instruct@bastion ~]$ pwd
/var/home/instruct

[instruct@bastion ~]$ tree -Fa -L 3 .
.
|-- .bash_history
|-- .bash_logout
|-- .bash_profile
|-- .bashrc
|-- .cache/
|   |-- instructlab/
|   |   |-- models/
|   |   `-- oci/
|   `-- pip/
|       |-- http/
|       `-- selfcheck/
|-- .config/
|   |-- cni/
|   |   `-- net.d/
|   |-- containers/
|   |   `-- storage.conf
|   `-- instructlab/
|       |-- config.yaml
|       `-- config.yaml.lock
|-- .lesshst
|-- .local/
|   |-- bin/
|   |   |-- activate-global-python-argcomplete*
|   |   |-- pip -> /usr/bin/pip-3.12*
|   |   |-- python-argcomplete-check-easy-install-script*
|   |   |-- register-python-argcomplete*
|   |   |-- tomlq*
|   |   |-- xq*
|   |   `-- yq*
|   |-- lib/
|   |   `-- python3.12/
|   `-- share/
|       |-- containers/
|       `-- instructlab/
|-- .python_history
|-- .ssh/
|   |-- 4djqlkey.pem
|   |-- 4djqlkey.pub
|   |-- authorized_keys
|   `-- config
|-- .viminfo
|-- .vimrc
`-- nvidia.txt

20 directories, 23 files

[instruct@bastion ~]$
```
<br>
<br>

## 3. RHEL AI 설치 및 구성 관련

### 3.1 KVM 가상화 환경에서 GPU passthrough 구성

#### 3.1.1 호스트 운영체제에 IOMMU 구성을 위한 GRUB 구성 설정

실행 명령어 - 인텔의 경우
```bash
grubby --args="intel_iommu=on iommu_pt" --update-kernel DEFAULT
systemctl reboot
```
* AMD의 경우 *--args="iommu=pt"*

실행 결과
```
[root@rhel94 ~]# grubby --args="intel_iommu=on iommu_pt" --update-kernel DEFAULT

[root@rhel94 ~]# systemctl reboot
...
```

#### 3.1.2 GPU 장비의 PCI 버스 주소 확인

실행 명령어
```bash
lspci -Dnn | egrep -i "nvidia|vga"
```

실행 결과
```
[root@rhel94 ~]# lspci -Dnn | egrep -i "nvidia|vga"
0000:04:00.0 VGA compatible controller [0300]: ASPEED Technology, Inc. ASPEED Graphics Family [1a03:2000] (rev 52)
0000:07:00.0 Bridge [0680]: NVIDIA Corporation GH100 [H100 NVSwitch] [10de:22a3] (rev a1)
0000:08:00.0 Bridge [0680]: NVIDIA Corporation GH100 [H100 NVSwitch] [10de:22a3] (rev a1)
0000:09:00.0 Bridge [0680]: NVIDIA Corporation GH100 [H100 NVSwitch] [10de:22a3] (rev a1)
0000:0a:00.0 Bridge [0680]: NVIDIA Corporation GH100 [H100 NVSwitch] [10de:22a3] (rev a1)
0000:1b:00.0 3D controller [0302]: NVIDIA Corporation GH100 [H100 SXM5 80GB] [10de:2330] (rev a1)
0000:43:00.0 3D controller [0302]: NVIDIA Corporation GH100 [H100 SXM5 80GB] [10de:2330] (rev a1)
0000:52:00.0 3D controller [0302]: NVIDIA Corporation GH100 [H100 SXM5 80GB] [10de:2330] (rev a1)
0000:61:00.0 3D controller [0302]: NVIDIA Corporation GH100 [H100 SXM5 80GB] [10de:2330] (rev a1)
0000:9d:00.0 3D controller [0302]: NVIDIA Corporation GH100 [H100 SXM5 80GB] [10de:2330] (rev a1)
0000:c3:00.0 3D controller [0302]: NVIDIA Corporation GH100 [H100 SXM5 80GB] [10de:2330] (rev a1)
0000:d1:00.0 3D controller [0302]: NVIDIA Corporation GH100 [H100 SXM5 80GB] [10de:2330] (rev a1)
0000:df:00.0 3D controller [0302]: NVIDIA Corporation GH100 [H100 SXM5 80GB] [10de:2330] (rev a1)

[root@rhel94 ~]#
```
* nVidia의 H100은 총 8개가 있으며, PCI 주소는 *`10de:2330`* 임

#### 3.1.3 nVidia GPU를 Stub로 등록

호스트의 드라이버가 해당 GPU를 사용하지 않도록 *pci-stub* 드라이버 구성

실행 명령어
```bash
grubby --args="pci-stub.ids=10de:2330" --update-kernel DEFAULT
systemctl reboot
```

실행 결과
```
[root@rhel94 ~]# grubby --args="pci-stub.ids=10de:2330" --update-kernel DEFAULT

[root@rhel94 ~]# systemctl reboot
...
```

#### 3.1.4 nVidia GPU를 가상머신에 PCI passthrough로 전달하는 XML 파일 생성

실행 명령어
```bash
cat /redhat/assign-gpus/assign-gpus-to-rhel_ai.xml 
```

실행 결과
```xml
<hostdev mode='subsystem' type='pci' managed='yes'>
 <driver name='vfio'/>
 <source>
  <address domain='0x0000' bus='0x1b' slot='0x00' function='0x0'/>
 </source>
</hostdev>
```
* 각각의 디바이스 별로, 위의 형식으로 구성

#### 3.1.5 가상머신에 해당 디바이스를 추가

실행 명령어
```bash
virsh attach-device RHEL_AI --file /redhat/assign-gpus/assign-gpus-to-rhel_ai.xml  --persistent
```

실행 결과
```
[root@rhel94 ~]# virsh attach-device RHEL_AI --file /redhat/assign-gpus/assign-gpus-to-rhel_ai.xml  --persistent
Device attached successfully.

[root@rhel94 ~]#
```

#### 3.1.6 가상머신 RHEL_AI의 구성파일 확인

실행 명령어
```bash
virsh dumpxml RHEL_AI > RHEL_AI.xml
xq '.domain.devices.hostdev|length' RHEL_AI.xml
xq -x '.domain.devices.hostdev[]|.source' RHEL_AI.xml
xq -x '.domain.devices.hostdev[]|.address' RHEL_AI.xml
```

실행 결과
```xml
[root@rhel94 ~]# virsh dumpxml RHEL_AI > RHEL_AI.xml

[root@rhel94 ~]# xq '.domain.devices.hostdev|length' RHEL_AI.xml
4

[root@rhel94 ~]# xq -x '.domain.devices.hostdev[]|.source' RHEL_AI.xml
<address domain="0x0000" bus="0x1b" slot="0x00" function="0x0"></address>
<address domain="0x0000" bus="0x43" slot="0x00" function="0x0"></address>
<address domain="0x0000" bus="0x52" slot="0x00" function="0x0"></address>
<address domain="0x0000" bus="0x61" slot="0x00" function="0x0"></address>

[root@rhel94 ~]# xq -x '.domain.devices.hostdev[]|.address' RHEL_AI.xml 
<@type>pci</@type><@domain>0x0000</@domain><@bus>0x09</@bus><@slot>0x00</@slot><@function>0x0</@function>
<@type>pci</@type><@domain>0x0000</@domain><@bus>0x0a</@bus><@slot>0x00</@slot><@function>0x0</@function>
<@type>pci</@type><@domain>0x0000</@domain><@bus>0x0b</@bus><@slot>0x00</@slot><@function>0x0</@function>
<@type>pci</@type><@domain>0x0000</@domain><@bus>0x0c</@bus><@slot>0x00</@slot><@function>0x0</@function>

[root@rhel94 ~]#
```

#### 3.1.7 가상머신 RHEL_AI에서 GPU 확인

실행 명령어
```bash
lspci -Dnn | egrep -i "nvidia|vga"
```

실행 결과
```
[root@rhel_ai ~]# lspci -Dnn | egrep -i "nvidia|vga"
0000:00:01.0 VGA compatible controller [0300]: Red Hat, Inc. Virtio 1.0 GPU [1af4:1050] (rev 01)
0000:09:00.0 3D controller [0302]: NVIDIA Corporation GH100 [H100 SXM5 80GB] [10de:2330] (rev a1)
0000:0a:00.0 3D controller [0302]: NVIDIA Corporation GH100 [H100 SXM5 80GB] [10de:2330] (rev a1)
0000:0b:00.0 3D controller [0302]: NVIDIA Corporation GH100 [H100 SXM5 80GB] [10de:2330] (rev a1)
0000:0c:00.0 3D controller [0302]: NVIDIA Corporation GH100 [H100 SXM5 80GB] [10de:2330] (rev a1)

[root@rhel_ai ~]# 
```
* 각각의 nVidia의 GPU (**domain.devices.hostdev[].source*)가 매핑된 주소(*domain.devices.hostdev[].address*)로 가상머신에서 보임

#### 3.1.8 nVidia NVSwitch를 Stub로 등록

호스트의 드라이버가 해당 NVSwitch를 사용하지 않도록 *pci-stub* 드라이버 구성

실행 명령어
```bash
grubby --args="pci-stub.ids=10de:22a3" --update-kernel DEFAULT
systemctl reboot
```

실행 결과
```
[root@rhel94 ~]# grubby --args="pci-stub.ids=10de:22a3" --update-kernel DEFAULT

[root@rhel94 ~]# systemctl reboot
...
```

#### 3.1.9 nVidia NVSwitch를 가상머신에 PCI passthrough로 전달하는 XML 파일 생성

실행 명령어
```bash
cat /redhat/assign-gpus/assign-nvswitch-to-rhel_ai.xml 
```

실행 결과
```xml
<hostdev mode='subsystem' type='pci' managed='yes'>
 <driver name='vfio'/>
 <source>
  <address domain='0x0000' bus='0x07' slot='0x00' function='0x0'/>
 </source>
</hostdev>
```
* 각각의 디바이스 별로, 위의 형식으로 구성

#### 3.1.10 가상머신에 해당 디바이스를 추가

실행 명령어
```bash
virsh attach-device RHEL_AI --file /redhat/assign-gpus/assign-nvswitch-to-rhel_ai.xml  --persistent
```

실행 결과
```
[root@rhel94 ~]# virsh attach-device RHEL_AI --file /redhat/assign-gpus/assign-nvswitch-to-rhel_ai.xml  --persistent
Device attached successfully.

[root@rhel94 ~]#
```

#### 3.1.11 가상머신 RHEL_AI의 구성파일 확인

실행 명령어
```bash
virsh dumpxml RHEL_AI > RHEL_AI.xml
xq '.domain.devices.hostdev|length' RHEL_AI.xml
xq -x '.domain.devices.hostdev[]|.source' RHEL_AI.xml
xq -x '.domain.devices.hostdev[]|.address' RHEL_AI.xml
```

실행 결과
```xml
[root@rhel94 ~]# virsh dumpxml RHEL_AI > RHEL_AI.xml

[root@rhel94 ~]# xq '.domain.devices.hostdev|length' RHEL_AI.xml
6

[root@rhel94 ~]# xq -x '.domain.devices.hostdev[]|.source' RHEL_AI.xml
...<snip>...
<address domain="0x0000" bus="0x07" slot="0x00" function="0x0"></address>
<address domain="0x0000" bus="0x08" slot="0x00" function="0x0"></address>

[root@rhel94 ~]# xq -x '.domain.devices.hostdev[]|.address' RHEL_AI.xml 
...<snip>...
<@type>pci</@type><@domain>0x0000</@domain><@bus>0x0d</@bus><@slot>0x00</@slot><@function>0x0</@function>
<@type>pci</@type><@domain>0x0000</@domain><@bus>0x0e</@bus><@slot>0x00</@slot><@function>0x0</@function>

[root@rhel94 ~]#
```

#### 3.1.12 가상머신 RHEL_AI에서 NVSwitch 확인

실행 명령어
```bash
lspci -Dnn | egrep -i "nvidia|vga|nvswitch"
```

실행 결과
```
[root@rhel_ai ~]# lspci -Dnn | egrep -i "nvidia|vga"
0000:00:01.0 VGA compatible controller [0300]: Red Hat, Inc. Virtio 1.0 GPU [1af4:1050] (rev 01)
0000:09:00.0 3D controller [0302]: NVIDIA Corporation GH100 [H100 SXM5 80GB] [10de:2330] (rev a1)
0000:0a:00.0 3D controller [0302]: NVIDIA Corporation GH100 [H100 SXM5 80GB] [10de:2330] (rev a1)
0000:0b:00.0 3D controller [0302]: NVIDIA Corporation GH100 [H100 SXM5 80GB] [10de:2330] (rev a1)
0000:0c:00.0 3D controller [0302]: NVIDIA Corporation GH100 [H100 SXM5 80GB] [10de:2330] (rev a1)
0000:0d:00.0 Bridge [0680]: NVIDIA Corporation GH100 [H100 NVSwitch] [10de:22a3] (rev a1)
0000:0e:00.0 Bridge [0680]: NVIDIA Corporation GH100 [H100 NVSwitch] [10de:22a3] (rev a1)

[root@rhel_ai ~]# 
```
* 각각의 nVidia의 NVSwitch (**domain.devices.hostdev[].source*)가 매핑된 주소(*domain.devices.hostdev[].address*)로 가상머신에서 보임

> [!INFOMRTANT]
> nVidia GPU는 종류/버전 등에 따라 토폴로지 구성이 다를 수 있습니다. 각각의 환경 및 조건에 맞게 가상머신 환경으로 구성이 필요합니다.

#### 3.1.13 nVidia의 H100, NVLink 및 NVSwitch를 가상머신에 할당

실행 명령어 - 가상머신 상에서 할당된 리소스 확인
```bash
lspci -Dnn | egrep -i "nvidia"
```

실행 결과
```
[root@rhel_ai ~]# lspci -Dnn | egrep -i "nvidia"
0000:09:00.0 Bridge [0680]: NVIDIA Corporation GH100 [H100 NVSwitch] [10de:22a3] (rev a1)
0000:0a:00.0 Bridge [0680]: NVIDIA Corporation GH100 [H100 NVSwitch] [10de:22a3] (rev a1)
0000:0b:00.0 Bridge [0680]: NVIDIA Corporation GH100 [H100 NVSwitch] [10de:22a3] (rev a1)
0000:0c:00.0 Bridge [0680]: NVIDIA Corporation GH100 [H100 NVSwitch] [10de:22a3] (rev a1)
0000:0d:00.0 3D controller [0302]: NVIDIA Corporation GH100 [H100 SXM5 80GB] [10de:2330] (rev a1)
0000:0e:00.0 3D controller [0302]: NVIDIA Corporation GH100 [H100 SXM5 80GB] [10de:2330] (rev a1)
0000:0f:00.0 3D controller [0302]: NVIDIA Corporation GH100 [H100 SXM5 80GB] [10de:2330] (rev a1)
0000:10:00.0 3D controller [0302]: NVIDIA Corporation GH100 [H100 SXM5 80GB] [10de:2330] (rev a1)
0000:11:00.0 3D controller [0302]: NVIDIA Corporation GH100 [H100 SXM5 80GB] [10de:2330] (rev a1)
0000:12:00.0 3D controller [0302]: NVIDIA Corporation GH100 [H100 SXM5 80GB] [10de:2330] (rev a1)
0000:13:00.0 3D controller [0302]: NVIDIA Corporation GH100 [H100 SXM5 80GB] [10de:2330] (rev a1)
0000:14:00.0 3D controller [0302]: NVIDIA Corporation GH100 [H100 SXM5 80GB] [10de:2330] (rev a1)

[root@rhel_ai ~]# 
```

#### 3.1.14 nVidia의 패브릭 확안

실행 명령어
```bash
systemctl status nvidia-fabricmanager.service 
```

실행 결과
```
[root@rhel_ai ~]# systemctl status nvidia-fabricmanager.service 
● nvidia-fabricmanager.service - NVIDIA fabric manager service
     Loaded: loaded (/usr/lib/systemd/system/nvidia-fabricmanager.service; enabled; preset: disabled)
     Active: active (running) since Tue 2025-03-25 02:10:15 UTC; 2h 37min ago
TriggeredBy: ● nvidia-nvswitch-devices.path
    Process: 2114 ExecStart=/usr/bin/nv-fabricmanager -c /usr/share/nvidia/nvswitch/fabricmanager.cfg (code=exited, status=0/SUCCESS)
   Main PID: 2116 (nv-fabricmanage)
      Tasks: 18 (limit: 1649170)
     Memory: 18.1M
        CPU: 4.847s
     CGroup: /system.slice/nvidia-fabricmanager.service
             └─2116 /usr/bin/nv-fabricmanager -c /usr/share/nvidia/nvswitch/fabricmanager.cfg

Mar 25 02:10:14 rhelai-02.redhat.lab systemd[1]: Starting NVIDIA fabric manager service...
Mar 25 02:10:15 rhelai-02.redhat.lab nv-fabricmanager[2116]: Connected to 1 node.
Mar 25 02:10:15 rhelai-02.redhat.lab nv-fabricmanager[2116]: Successfully configured all the available NVSwitches to route GPU NVLink traffic. NVLink Peer-to-Peer support will be enabled once the GPUs are succ>
Mar 25 02:10:15 rhelai-02.redhat.lab systemd[1]: Started NVIDIA fabric manager service.

[root@rhel_ai ~]#
```
* 패브릭 구성에 이슈가 없으며, NVSwitch가 GPU의 NVLink로 라우트 되는 것을 확인

#### 3.1.15 nVidia의 NVSwitch 확인

실행 명령어
```bash
systemctl status nvidia-nvswitch-devices.path 
```

실행 결과
```
[root@rhel_ai ~]# systemctl status nvidia-nvswitch-devices.path 
● nvidia-nvswitch-devices.path - NVIDIA NVSwitch Devices
     Loaded: loaded (/usr/lib/systemd/system/nvidia-nvswitch-devices.path; disabled; preset: disabled)
     Active: active (running) since Tue 2025-03-25 02:14:46 UTC; 2h 34min ago
      Until: Tue 2025-03-25 02:14:46 UTC; 2h 34min ago
   Triggers: ● nvidia-fabricmanager.service

Mar 25 02:14:46 rhelai-02.redhat.lab systemd[1]: Started NVIDIA NVSwitch Devices.

[root@rhel_ai ~]# 
```

#### 3.1.16 가상머신에서 nVidia 확인

실행 명령어
```bash
nvidia-smi --list-gpus
```

실행 결과
```
[root@rhel_ai ~]# nvidia-smi --list-gpus
GPU 0: NVIDIA H100 80GB HBM3 (UUID: GPU-c7a0294c-c2c2-5476-438c-fb468eaa223b)
GPU 1: NVIDIA H100 80GB HBM3 (UUID: GPU-27196ced-a067-4406-2159-46448710fc9c)
GPU 2: NVIDIA H100 80GB HBM3 (UUID: GPU-0d9ce0d5-22a0-fdf7-c891-f26e86f907b6)
GPU 3: NVIDIA H100 80GB HBM3 (UUID: GPU-7353c83a-0617-7238-ca5a-9b9c80212c46)
GPU 4: NVIDIA H100 80GB HBM3 (UUID: GPU-b71a1811-5b24-ae65-9a8f-4118c7c1db31)
GPU 5: NVIDIA H100 80GB HBM3 (UUID: GPU-4a360bd8-44cd-43cb-9dc8-1b47ce52e162)
GPU 6: NVIDIA H100 80GB HBM3 (UUID: GPU-590d9f08-faf1-6a7d-70a1-b15156fd95aa)
GPU 7: NVIDIA H100 80GB HBM3 (UUID: GPU-5534d557-2a95-300a-81e6-7b626d87378a)

[root@rhel_ai ~]# nvidia-smi topo --matrix
	GPU0	GPU1	GPU2	GPU3	GPU4	GPU5	GPU6	GPU7	CPU Affinity	NUMA Affinity	GPU NUMA ID
GPU0	 X 	NV18	NV18	NV18	NV18	NV18	NV18	NV18	0-63	0		N/A
GPU1	NV18	 X 	NV18	NV18	NV18	NV18	NV18	NV18	0-63	0		N/A
GPU2	NV18	NV18	 X 	NV18	NV18	NV18	NV18	NV18	0-63	0		N/A
GPU3	NV18	NV18	NV18	 X 	NV18	NV18	NV18	NV18	0-63	0		N/A
GPU4	NV18	NV18	NV18	NV18	 X 	NV18	NV18	NV18	0-63	0		N/A
GPU5	NV18	NV18	NV18	NV18	NV18	 X 	NV18	NV18	0-63	0		N/A
GPU6	NV18	NV18	NV18	NV18	NV18	NV18	 X 	NV18	0-63	0		N/A
GPU7	NV18	NV18	NV18	NV18	NV18	NV18	NV18	 X 	0-63	0		N/A

Legend:

  X    = Self
  SYS  = Connection traversing PCIe as well as the SMP interconnect between NUMA nodes (e.g., QPI/UPI)
  NODE = Connection traversing PCIe as well as the interconnect between PCIe Host Bridges within a NUMA node
  PHB  = Connection traversing PCIe as well as a PCIe Host Bridge (typically the CPU)
  PXB  = Connection traversing multiple PCIe bridges (without traversing the PCIe Host Bridge)
  PIX  = Connection traversing at most a single PCIe bridge
  NV#  = Connection traversing a bonded set of # NVLinks

[root@rhel_ai ~]# nvidia-smi nvlink --status
GPU 0: NVIDIA H100 80GB HBM3 (UUID: GPU-c7a0294c-c2c2-5476-438c-fb468eaa223b)
	 Link 0: 26.562 GB/s
	 Link 1: 26.562 GB/s
   ...<snip>...
	 Link 17: 26.562 GB/s
GPU 1: NVIDIA H100 80GB HBM3 (UUID: GPU-27196ced-a067-4406-2159-46448710fc9c)
	 Link 0: 26.562 GB/s
	 Link 1: 26.562 GB/s
   ...<snip>...
	 Link 17: 26.562 GB/s
GPU 2: NVIDIA H100 80GB HBM3 (UUID: GPU-0d9ce0d5-22a0-fdf7-c891-f26e86f907b6)
	 Link 0: 26.562 GB/s
	 Link 1: 26.562 GB/s
   ...<snip>...
	 Link 17: 26.562 GB/s
GPU 3: NVIDIA H100 80GB HBM3 (UUID: GPU-7353c83a-0617-7238-ca5a-9b9c80212c46)
	 Link 0: 26.562 GB/s
	 Link 1: 26.562 GB/s
   ...<snip>...
	 Link 17: 26.562 GB/s
GPU 4: NVIDIA H100 80GB HBM3 (UUID: GPU-b71a1811-5b24-ae65-9a8f-4118c7c1db31)
	 Link 0: 26.562 GB/s
	 Link 1: 26.562 GB/s
   ...<snip>...
	 Link 17: 26.562 GB/s
GPU 5: NVIDIA H100 80GB HBM3 (UUID: GPU-4a360bd8-44cd-43cb-9dc8-1b47ce52e162)
	 Link 0: 26.562 GB/s
	 Link 1: 26.562 GB/s
   ...<snip>...
	 Link 17: 26.562 GB/s
GPU 6: NVIDIA H100 80GB HBM3 (UUID: GPU-590d9f08-faf1-6a7d-70a1-b15156fd95aa)
	 Link 0: 26.562 GB/s
	 Link 1: 26.562 GB/s
   ...<snip>...
	 Link 17: 26.562 GB/s
GPU 7: NVIDIA H100 80GB HBM3 (UUID: GPU-5534d557-2a95-300a-81e6-7b626d87378a)
	 Link 0: 26.562 GB/s
	 Link 1: 26.562 GB/s
   ...<snip>...
	 Link 17: 26.562 GB/s

[root@rhel_ai ~]# 
```





<br>

### 3.2 RHEL AI 작업 시, Red Hat Insights 관련 메시지 발생

#### 3.2.1 Red Hat Insights 연결 구성 메시지 발생

```
[root@rhel_ai ~]# ilab --help
This host is not connected to Red Hat Insights.

To connect this host to Red Hat Insights run the following command:
sudo rhc connect --organization <org_id> --activation-key <your_activation_key>

To generate an Activation Key:
https://console.redhat.com/insights/connector/activation-keys (this page will also display your Organization ID).

For more information on Red Hat Insights, please visit:
https://docs.redhat.com/en/documentation/subscription_central/1-latest/html/getting_started_with_activation_keys_on_the_hybrid_cloud_console/assembly-creating-managing-activation-keys

[root@rhel_ai ~]#
```

#### 3.2.2 레드햇 인사이트 연결

*console.redhat.com*에서 조직의 ID랑 관련된 *activation_key*를 확인 후 명령어 실행
```bash
rhc connect --organization <org_id> --activation-key <your_activation_key>
```

#### 3.2.3 외부 연결이 안되는 환경 등일 때

실행 명령어
```bash
mkdir -pv /etc/ilab
touch /etc/ilab/insights-opt-out
ls -lh /etc/ilab/insights-opt-out 
ilab --help
```

실행 결과
```
[root@rhel_ai ~]# mkdir -pv /etc/ilab
mkdir: created directory '/etc/ilab'

[root@rhel_ai ~]# touch /etc/ilab/insights-opt-out

[root@rhel_ai ~]# ls -lh /etc/ilab/insights-opt-out 
-rw-r--r--. 1 root root 0 Mar 25 00:12 /etc/ilab/insights-opt-out

[root@rhel_ai ~]# ilab --help
Usage: ilab [OPTIONS] COMMAND [ARGS]...

...<snip>...

[root@rhel_ai ~]# 
```
<br>
<br>

실행 명령어
```bash

```

실행 결과
```

```

<br>
<br>

------
[차례](../README.md)