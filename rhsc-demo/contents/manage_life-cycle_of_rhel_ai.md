# RHEL AI 업그레이드

**목차**
1. [RHEL AI 업그레이드](./manage_life-cycle_of_rhel_ai.md#1-rhel-ai-업그레이드)<br>
2. [RHEL AI에 패키지 설치]()<br>
<br>
<hr>
<br>

## 1. RHEL AI 업그레이드

### 1.1 업그레이드 진행

#### 1.1.1 레지스트리 로그인

실행 명령어
```bash
sudo podman login registry.redhat.io -u=<USER_NAME> -p=<USER_PASSWORD> --authfile /etc/ostree/auth.json
```

실행 결과
```
[instruct@bastion ~]$ sudo podman login registry.redhat.io -u=<USER_NAME> -p=<USER_PASSWORD> --authfile /etc/ostree/auth.json
Login Succeeded!

[instruct@bastion ~]$
```

#### 1.1.2 RHEL AI의 최신 이미지로 업그레이드

실행 명령어
```bash
sudo bootc switch registry.redhat.io/rhelai1/bootc-nvidia-rhel9:1.4
```
* nVidia 기반 RHEL 9을 위한 이미지 1.4로 업그레이드

실행 결과
```
[instruct@bastion ~]$ sudo bootc switch registry.redhat.io/rhelai1/bootc-nvidia-rhel9:1.4
layers already present: 24; layers needed: 43 (13.4 GB)
Fetched layers: 12.51 GiB in 9 minutes (24.87 MiB/s)
Queued for next boot: registry.redhat.io/rhelai1/bootc-nvidia-rhel9:1.4
  Version: 9.20250213.0
  Digest: sha256:ba1448451eab5581993915ed55e79c4c52664a9b166dee6803888705d49d8bc3

[instruct@bastion ~]$
```

#### 1.1.3 RHEL AI 시스템 재부팅

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
<br>

### 1.2 업그레이드 후 작업

#### 1.2.1 컨테이너 스토리지 구성 확인

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

#### 1.2.2 스토리지 구성 파일을 사용자 환경으로 복사

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

#### 1.2.3 InstructLab 구성 초기화

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

INFO 2025-03-18 11:42:05,232 instructlab.config.init:259: Detecting hardware...
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
--------------------------------------------

[instruct@bastion ~]$
```

#### 1.1.4 InstructLab 구성 파일 확인

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

### 2.2 패키지 구성

#### 2.2.1 패키지 확인

실행 명령어
```bash
rpm-ostree search gdb
```

실행 결과
```
[root@bastion ~]# rpm-ostree search gdb

...<snip>...

===== Name Matched =====
gdb : A stub package for GNU source-level debugger

...<snip>...

[root@bastion ~]#
```

#### 2.2.2 패키지 설치

실행 명령어
```bash
rpm-ostree install gdb
```

실행 결과
```

```

> [!NOTE]
> 주요 패키지 리스트는 다음과 같습니다.<br>
> * python3.11-pip
> * strace
  * tree



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