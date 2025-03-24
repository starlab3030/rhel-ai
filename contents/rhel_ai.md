# RHEL AI 

**목차**
1. [RHEL AI의 InstructLab](./rhel_ai.md#1-rhel-ai의-instructlab)<br>
2. [RHEL AI를 위한 모델 확인 및 구성](./rhel_ai.md#2-rhel-ai를-위한-모델-확인-및-구성)<br>
3. [모델 기반 채팅 서비스](./rhel_ai.md#3-모델-기반-채팅-서비스)<br>
<br>
<br>

## 1. RHEL AI의 InstructLab

### 1.1 RHEL AI 상에 InstructLab 기본 구성

#### 1.1.1 InstructLab의 모델 

실행 명령어
```bash
tree -F -L 2 .cache/instructlab/
```

실행 결과
```
[instruct@bastion ~]$ tree -F -L 2 .cache/instructlab/
.cache/instructlab/
|-- models/
`-- oci/

2 directories, 0 files

[instruct@bastion ~]$
```
* ~/.cache/instructlab/models/
  + 다운로드 받은 모든 LLM들
  + 사용자가 RHEL AI를 통해 생성하고 저장한 결과물

#### 1.1.2 InstructLab의 구성 파일

실행 명령어
```bash
tree -F -L 2 .config/instructlab/
```

실행 결과
```
[instruct@bastion ~]$ tree -F -L 2 .config/instructlab/
.config/instructlab/
|-- config.yaml
`-- config.yaml.lock

0 directories, 2 files

[instruct@bastion ~]$
```
* ~/.config/instructlab/config.yaml
  + 시스템 환경 기반 구성파일

#### 1.1.3 InstructLab의 아키텍처

실행 명령어
```bash
tree -F -L 2 .local/share/instructlab/
```

실행 결과
```
[instruct@bastion ~]$ tree -F -L 2 .local/share/instructlab/
.local/share/instructlab/
|-- chatlogs/
|-- checkpoints/
|-- datasets/
|-- internal/
|   |-- eval_data/
|   |-- system_profiles/
|   `-- train_configuration/
|-- logs/
|-- phased/
`-- taxonomy/
    |-- CODE_OF_CONDUCT.md
    |-- CONTRIBUTING.md
    |-- CONTRIBUTOR_ROLES.md
    |-- LICENSE
    |-- MAINTAINERS.md
    |-- Makefile
    |-- README.md
    |-- SECURITY.md
    |-- compositional_skills/
    |-- docs/
    |-- foundational_skills/
    |-- governance.md
    |-- knowledge/
    `-- scripts/

15 directories, 9 files

[instruct@bastion ~]$
```
* ~/.local/share/instructlab/datasets/
  + 분류 저장소(taxonomy)의 수정을 기반으로 구축된 SDG 단계의 데이터 출력을 포함
* ~/.local/share/instructlab/taxonomy/
  + Skill & Knowledge 데이터를 담고 있음
* ~/.local/share/instructlab/phased/\<phase1-or-phase2\>/checkpoints/
  + 여러 단계의 훈련 프로세스 출력을 담고 있음
<br>
<br>

### 1.2 RHEL AI 상에 InstructLab의 시스템 프로파일 설정

#### 1.2.1 ilab 명령으로 시스템 정보 확인

실행 명령어
```bash
ilab system info
```

실행 결과
```
[instruct@bastion ~]$ ilab system info
ggml_cuda_init: GGML_CUDA_FORCE_MMQ:    no
ggml_cuda_init: GGML_CUDA_FORCE_CUBLAS: no
ggml_cuda_init: found 4 CUDA devices:
  Device 0: NVIDIA L4, compute capability 8.9, VMM: yes
  Device 1: NVIDIA L4, compute capability 8.9, VMM: yes
  Device 2: NVIDIA L4, compute capability 8.9, VMM: yes
  Device 3: NVIDIA L4, compute capability 8.9, VMM: yes
Platform:
  sys.version: 3.11.7 (main, Jan  8 2025, 00:00:00) [GCC 11.4.1 20231218 (Red Hat 11.4.1-3)]
  sys.platform: linux
  os.name: posix
  platform.release: 5.14.0-427.50.2.el9_4.x86_64
  platform.machine: x86_64
  platform.node: bastion.4djql.internal
  platform.python_version: 3.11.7
  os-release.ID: rhel
  os-release.VERSION_ID: 9.4
  os-release.PRETTY_NAME: Red Hat Enterprise Linux 9.4 (Plow)
  memory.total: 181.77 GB
  memory.available: 179.51 GB
  memory.used: 0.81 GB

InstructLab:
  instructlab.version: 0.23.2
  instructlab-dolomite.version: 0.2.0
  instructlab-eval.version: 0.5.1
  instructlab-quantize.version: 0.1.0
  instructlab-schema.version: 0.4.2
  instructlab-sdg.version: 0.7.1
  instructlab-training.version: 0.7.0

Torch:
  torch.version: 2.5.1
  torch.backends.cpu.capability: AVX2
  torch.version.cuda: 12.4
  torch.version.hip: None
  torch.cuda.available: True
  torch.backends.cuda.is_built: True
  torch.backends.mps.is_built: False
  torch.backends.mps.is_available: False
  torch.cuda.bf16: True
  torch.cuda.current.device: 0
  torch.cuda.0.name: NVIDIA L4
  torch.cuda.0.free: 21.8 GB
  torch.cuda.0.total: 22.0 GB
  torch.cuda.0.capability: 8.9 (see https://developer.nvidia.com/cuda-gpus#compute)
  torch.cuda.1.name: NVIDIA L4
  torch.cuda.1.free: 21.8 GB
  torch.cuda.1.total: 22.0 GB
  torch.cuda.1.capability: 8.9 (see https://developer.nvidia.com/cuda-gpus#compute)
  torch.cuda.2.name: NVIDIA L4
  torch.cuda.2.free: 21.8 GB
  torch.cuda.2.total: 22.0 GB
  torch.cuda.2.capability: 8.9 (see https://developer.nvidia.com/cuda-gpus#compute)
  torch.cuda.3.name: NVIDIA L4
  torch.cuda.3.free: 21.8 GB
  torch.cuda.3.total: 22.0 GB
  torch.cuda.3.capability: 8.9 (see https://developer.nvidia.com/cuda-gpus#compute)

llama_cpp_python:
  llama_cpp_python.version: 0.3.2
  llama_cpp_python.supports_gpu_offload: True

[instruct@bastion ~]$
```

#### 1.1.2 시스템 프로파일

실행 명령어
```bash
tree .local/share/instructlab/internal/system_profiles/
```

실행 결과
```
[instruct@bastion ~]$ tree .local/share/instructlab/internal/system_profiles/
.local/share/instructlab/internal/system_profiles/
`-- nvidia
    |-- a100
    |   |-- a100_x2.yaml
    |   |-- a100_x4.yaml
    |   `-- a100_x8.yaml
    |-- h100
    |   |-- h100_x2.yaml
    |   |-- h100_x4.yaml
    |   `-- h100_x8.yaml
    |-- l4
    |   `-- l4_x8.yaml
    `-- l40s
        |-- l40s_x4.yaml
        `-- l40s_x8.yaml

5 directories, 9 files

[instruct@bastion ~]$
```

#### 1.1.2 사용자의 instructlab 구성 파일

실행 명령어
```bash
ilab config edit
yq -y . .config/instructlab/config.yaml
```
* 시스템 환경에 맞게 구성 파일 변경
* 예
  + GPU 수 조종
  + GPU 수와 관련된 변수 조정

실행 결과
```yaml
chat:
  context: default
  logs_dir: /var/home/instruct/.local/share/instructlab/chatlogs
  max_tokens: null
  model: /var/home/instruct/.cache/instructlab/models/granite-3.1-8b-lab-v1
  session: null
  temperature: 1.0
  vi_mode: false
  visible_overflow: true
evaluate:
  base_branch: null
  base_model: /var/home/instruct/.cache/instructlab/models/granite-3.1-8b-starter-v1
  branch: null
  dk_bench:
    input_questions: null
    judge_model: gpt-4o
    output_dir: /var/home/instruct/.local/share/instructlab/internal/eval_data/dk_bench
    output_file_formats: jsonl
  gpus: 4
  mmlu:
    batch_size: auto
    few_shots: 5
  mmlu_branch:
    tasks_dir: /var/home/instruct/.local/share/instructlab/datasets
  model: null
  mt_bench:
    judge_model: /var/home/instruct/.cache/instructlab/models/prometheus-8x7b-v2-0
    max_workers: auto
    output_dir: /var/home/instruct/.local/share/instructlab/internal/eval_data/mt_bench
  mt_bench_branch:
    judge_model: /var/home/instruct/.cache/instructlab/models/prometheus-8x7b-v2-0
    output_dir: /var/home/instruct/.local/share/instructlab/internal/eval_data/mt_bench_branch
    taxonomy_path: /var/home/instruct/.local/share/instructlab/taxonomy
  system_prompt: null
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
      gpus: 4
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
  cpu_info: null
  gpu_count: 4
  gpu_family: L4
  gpu_manufacturer: Nvidia
  gpu_sku: null
rag:
  convert:
    output_dir: /var/home/instruct/.local/share/instructlab/converted_documents
    taxonomy_base: origin/main
    taxonomy_path: /var/home/instruct/.local/share/instructlab/taxonomy
  document_store:
    collection_name: ilab
    uri: /var/home/instruct/.local/share/instructlab/embeddings.db
  embedding_model:
    embedding_model_path: /var/home/instruct/.cache/instructlab/models/ibm-granite/granite-embedding-125m-english
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
    gpus: 4
    llm_family: ''
    max_startup_attempts: 120
    vllm_args:
      - --tensor-parallel-size
      - '4'
train:
  additional_args:
    learning_rate: 6.0e-06
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
  lora_quantize_dtype: null
  lora_rank: 0
  max_batch_len: 10000
  max_seq_len: 10000
  model_path: /var/home/instruct/.cache/instructlab/models/granite-3.1-8b-starter-v1
  nproc_per_node: 4
  num_epochs: 4
  phased_base_dir: /var/home/instruct/.local/share/instructlab/phased
  phased_mt_bench_judge: /var/home/instruct/.cache/instructlab/models/prometheus-8x7b-v2-0
  phased_phase1_effective_batch_size: 128
  phased_phase1_learning_rate: 2.0e-05
  phased_phase1_num_epochs: 7
  phased_phase1_samples_per_save: 0
  phased_phase2_effective_batch_size: 3840
  phased_phase2_learning_rate: 6.0e-06
  phased_phase2_num_epochs: 10
  phased_phase2_samples_per_save: 0
  pipeline: accelerated
  save_samples: 0
  training_journal: null
version: 1.0.0
```
<br>
<br>

## 2 RHEL AI를 위한 모델 확인 및 구성

### 2.1 RHEL AI를 위한 모델 이미지

#### 2.1.1 레드햇 레지스트리 상에 이미지 확인

실행 명령어
```bash
podman search registry.redhat.io/rhelai1 | sort -u
```

실행 결과
```
[instruct@bastion ~]$ podman search registry.redhat.io/rhelai1 | sort -u
NAME                                                           DESCRIPTION
registry.redhat.io/rhelai1/bootc-amd-rhel9                     Red Hat image for bootc-amd-rhel9
registry.redhat.io/rhelai1/bootc-intel-rhel9                   Red Hat image for bootc-intel-rhel9
registry.redhat.io/rhelai1/bootc-nvidia-rhel9                  Red Hat image for bootc-nvidia-rhel9
registry.redhat.io/rhelai1/docling-serve-rhel9                 Red Hat image for docling-serve-rhel9
registry.redhat.io/rhelai1/granite-3.1-8b-lab-v1               Red Hat image for granite-3.1-8b-lab-v1
registry.redhat.io/rhelai1/granite-3.1-8b-starter-v1           Red Hat image for granite-3.1-8b-starter-v1
registry.redhat.io/rhelai1/granite-7b-redhat-lab               Red Hat image for granite-7b-redhat-lab
registry.redhat.io/rhelai1/granite-7b-starter                  Red Hat image for granite-7b-starter
registry.redhat.io/rhelai1/granite-8b-code-base                Red Hat image for granite-8b-code-base
registry.redhat.io/rhelai1/granite-8b-lab-v2-preview           Red Hat image for granite-8b-lab-v2-preview
registry.redhat.io/rhelai1/granite-8b-starter-v1               Red Hat image for granite-8b-starter-v1
registry.redhat.io/rhelai1/instructlab-amd-rhel9               Red Hat image for instructlab-amd-rhel9
registry.redhat.io/rhelai1/instructlab-intel-rhel9             Red Hat image for instructlab-intel-rhel9
registry.redhat.io/rhelai1/instructlab-nvidia-rhel9            Red Hat image for instructlab-nvidia-rhel9
registry.redhat.io/rhelai1/knowledge-adapter-v3                Red Hat image for knowledge-adapter-v3
registry.redhat.io/rhelai1/mixtral-8x7b-instruct-v0-1          Red Hat image for mixtral-8x7b-instruct-v0-1
registry.redhat.io/rhelai1/modelcar-docling-tableformer        Red Hat image for modelcar-docling-tableform...
registry.redhat.io/rhelai1/modelcar-granite-7b-redhat-lab      Red Hat image for modelcar-granite-7b-redhat...
registry.redhat.io/rhelai1/modelcar-granite-8b-code-base       Red Hat image for modelcar-granite-8b-code-b...
registry.redhat.io/rhelai1/modelcar-granite-8b-lab-v1          Red Hat image for modelcar-granite-8b-lab-v1
registry.redhat.io/rhelai1/modelcar-granite-8b-lab-v2-preview  Red Hat image for modelcar-granite-8b-lab-v2...
registry.redhat.io/rhelai1/modelcar-granite-8b-starter-v1      Red Hat image for modelcar-granite-8b-starte...
registry.redhat.io/rhelai1/modelcar-knowledge-adapter-v3       Red Hat image for modelcar-knowledge-adapter...
registry.redhat.io/rhelai1/modelcar-prometheus-8x7b-v2-0       Red Hat image for modelcar-prometheus-8x7b-v...
registry.redhat.io/rhelai1/skills-adapter-v3                   Red Hat image for skills-adapter-v3

[instruct@bastion ~]$
```

#### 2.1.2 Granite LLM 

|$\color{lime}{\texttt{목적}}$|$\color{lime}{\texttt{모델}}$|$\color{lime}{\texttt{설명}}$|
|:---:|:---|:---|
|추론 서비스 모델|granite-3.1-8b-lab-v1|Granite 3.1 버전|
|Granite LLM 커스텀을 위한 모델|granite-3.1-8b-starter-v1<br>mixtral-8x7b-instruct-v0-1<br>prometheus-8x7b-v2-0|하드웨어 벤더에 종속된 기본 LLM<br>SDG를 위한 교사 모델<br>훈련 및 평가를 위한 판단 모델|
|LLM 커스텀을 위한 도구|knowledge-adapter-v3<br>skills-adapter-v3|SDG를 위한 LoRA 계층 지식 어댑터<br>SDG를 위한 LoRA 계층 기술 어댑터|
* 합성 데이터 (SDG: Synthetic Data Generation)
* 저랭크 적응 어댑터 (LoRA: Low-rank adaptation)
<br>

### 2.2 모델 다운로드

#### 2.2.1 레지스트리 로그인

실행 명령어
```bash
podman login registry.redhat.io -u='<USER_ID>' -p='<USER_PASSWORD>'
```

실행 결과
```
[instruct@bastion ~]$ podman login registry.redhat.io -u='<USER_ID>' -p='<USER_PASSWORD>' 
Login Succeeded!

[instruct@bastion ~]$
```

#### 2.2.2 모델 다운로드

실행 명령어
```bash
ilab model download --repository docker://registry.redhat.io/rhelai1/granite-3.1-8b-starter-v1 --release latest
ilab model download --repository docker://registry.redhat.io/rhelai1/mixtral-8x7b-instruct-v0-1 --release latest
ilab model download --repository docker://registry.redhat.io/rhelai1/prometheus-8x7b-v2-0 --release latest
ilab model download --repository docker://registry.redhat.io/rhelai1/knowledge-adapter-v3 --release latest
ilab model download --repository docker://registry.redhat.io/rhelai1/skills-adapter-v3 --release latest
ilab model download --repository docker://registry.redhat.io/rhelai1/granite-3.1-8b-lab-v1 --release latest
```

실행 결과
```
[instruct@bastion ~]$ ilab model download --repository docker://registry.redhat.io/rhelai1/granite-3.1-8b-starter-v1 --release latest
INFO 2025-03-19 07:26:29,288 instructlab.model.download:193: Downloading model from OCI registry:
    Model: docker://registry.redhat.io/rhelai1/granite-3.1-8b-starter-v1@latest
    Destination: /var/home/instruct/.cache/instructlab/models
Copying blob b19c07c7ada5 done   |
...<snip>...
Copying blob adde9662090e done   |
Copying config 44136fa355 done   |
Writing manifest to image destination
INFO 2025-03-19 07:28:01,496 instructlab.model.download:289:
ᕦ(òᴗóˇ)ᕤ docker://registry.redhat.io/rhelai1/granite-3.1-8b-starter-v1 model download completed successfully! ᕦ(òᴗóˇ)ᕤ

INFO 2025-03-19 07:28:01,496 instructlab.model.download:303: Available models (`ilab model list`):
+----------------------------------+---------------------+---------+
| Model Name                       | Last Modified       | Size    |
+----------------------------------+---------------------+---------+
| models/granite-3.1-8b-starter-v1 | 2025-03-19 07:28:01 | 15.2 GB |
+----------------------------------+---------------------+---------+

[instruct@bastion ~]$ ilab model download --repository docker://registry.redhat.io/rhelai1/mixtral-8x7b-instruct-v0-1 --release latest
INFO 2025-03-19 07:28:53,521 instructlab.model.download:193: Downloading model from OCI registry:
    Model: docker://registry.redhat.io/rhelai1/mixtral-8x7b-instruct-v0-1@latest
    Destination: /var/home/instruct/.cache/instructlab/models
Copying blob d0b63fca793c done   |
...<snip>...
Copying blob 475361439e5c done   |
Copying config 44136fa355 done   |
Writing manifest to image destination
INFO 2025-03-19 07:35:22,988 instructlab.model.download:289:
ᕦ(òᴗóˇ)ᕤ docker://registry.redhat.io/rhelai1/mixtral-8x7b-instruct-v0-1 model download completed successfully! ᕦ(òᴗóˇ)ᕤ

INFO 2025-03-19 07:35:22,988 instructlab.model.download:303: Available models (`ilab model list`):
+-----------------------------------+---------------------+---------+
| Model Name                        | Last Modified       | Size    |
+-----------------------------------+---------------------+---------+
| models/granite-3.1-8b-starter-v1  | 2025-03-19 07:28:01 | 15.2 GB |
| models/mixtral-8x7b-instruct-v0-1 | 2025-03-19 07:35:22 | 87.0 GB |
+-----------------------------------+---------------------+---------+

[instruct@bastion ~]$ ilab model download --repository docker://registry.redhat.io/rhelai1/prometheus-8x7b-v2-0 --release latest
INFO 2025-03-19 07:36:16,854 instructlab.model.download:193: Downloading model from OCI registry:
    Model: docker://registry.redhat.io/rhelai1/prometheus-8x7b-v2-0@latest
    Destination: /var/home/instruct/.cache/instructlab/models
Copying blob a375e93d6f89 done   |
...<snip>...
Copying blob 7ada2fa1461c done   |
Copying config 44136fa355 done   |
Writing manifest to image destination
INFO 2025-03-19 07:42:48,983 instructlab.model.download:289:
ᕦ(òᴗóˇ)ᕤ docker://registry.redhat.io/rhelai1/prometheus-8x7b-v2-0 model download completed successfully! ᕦ(òᴗóˇ)ᕤ

INFO 2025-03-19 07:42:48,983 instructlab.model.download:303: Available models (`ilab model list`):
+-----------------------------------+---------------------+---------+
| Model Name                        | Last Modified       | Size    |
+-----------------------------------+---------------------+---------+
| models/granite-3.1-8b-starter-v1  | 2025-03-19 07:28:01 | 15.2 GB |
| models/mixtral-8x7b-instruct-v0-1 | 2025-03-19 07:35:22 | 87.0 GB |
| models/prometheus-8x7b-v2-0       | 2025-03-19 07:42:48 | 87.0 GB |
+-----------------------------------+---------------------+---------+

[instruct@bastion ~]$ ilab model download --repository docker://registry.redhat.io/rhelai1/knowledge-adapter-v3 --release latest
INFO 2025-03-19 07:44:26,388 instructlab.model.download:193: Downloading model from OCI registry:
    Model: docker://registry.redhat.io/rhelai1/knowledge-adapter-v3@latest
    Destination: /var/home/instruct/.cache/instructlab/models
Copying blob cfc7749b96f6 done   |
...<snip>...
Copying blob d2313c03a149 done   |
Copying config 44136fa355 done   |
Writing manifest to image destination
INFO 2025-03-19 07:44:43,097 instructlab.model.download:289:
ᕦ(òᴗóˇ)ᕤ docker://registry.redhat.io/rhelai1/knowledge-adapter-v3 model download completed successfully! ᕦ(òᴗóˇ)ᕤ

INFO 2025-03-19 07:44:43,097 instructlab.model.download:303: Available models (`ilab model list`):
+-----------------------------------+---------------------+---------+
| Model Name                        | Last Modified       | Size    |
+-----------------------------------+---------------------+---------+
| models/granite-3.1-8b-starter-v1  | 2025-03-19 07:28:01 | 15.2 GB |
| models/mixtral-8x7b-instruct-v0-1 | 2025-03-19 07:35:22 | 87.0 GB |
| models/prometheus-8x7b-v2-0       | 2025-03-19 07:42:48 | 87.0 GB |
+-----------------------------------+---------------------+---------+

[instruct@bastion ~]$ ilab model download --repository docker://registry.redhat.io/rhelai1/skills-adapter-v3 --release latest
INFO 2025-03-19 07:46:27,447 instructlab.model.download:193: Downloading model from OCI registry:
    Model: docker://registry.redhat.io/rhelai1/skills-adapter-v3@latest
    Destination: /var/home/instruct/.cache/instructlab/models
Copying blob 4452b845ab9c done   |
...<snip>...
Copying blob 5d44fdf2d36d done   |
Copying config 44136fa355 done   |
Writing manifest to image destination
INFO 2025-03-19 07:46:32,510 instructlab.model.download:289:
ᕦ(òᴗóˇ)ᕤ docker://registry.redhat.io/rhelai1/skills-adapter-v3 model download completed successfully! ᕦ(òᴗóˇ)ᕤ

INFO 2025-03-19 07:46:32,510 instructlab.model.download:303: Available models (`ilab model list`):
+-----------------------------------+---------------------+---------+
| Model Name                        | Last Modified       | Size    |
+-----------------------------------+---------------------+---------+
| models/granite-3.1-8b-starter-v1  | 2025-03-19 07:28:01 | 15.2 GB |
| models/mixtral-8x7b-instruct-v0-1 | 2025-03-19 07:35:22 | 87.0 GB |
| models/prometheus-8x7b-v2-0       | 2025-03-19 07:42:48 | 87.0 GB |
+-----------------------------------+---------------------+---------+

[instruct@bastion ~]$ ilab model download --repository docker://registry.redhat.io/rhelai1/granite-3.1-8b-lab-v1 --release latest
INFO 2025-03-19 07:48:12,194 instructlab.model.download:193: Downloading model from OCI registry:
    Model: docker://registry.redhat.io/rhelai1/granite-3.1-8b-lab-v1@latest
    Destination: /var/home/instruct/.cache/instructlab/models
Copying blob ee911225bc65 done   |
...<snip>...
Copying blob adde9662090e done   |
Copying config 44136fa355 done   |
Writing manifest to image destination
INFO 2025-03-19 07:50:11,913 instructlab.model.download:289:
ᕦ(òᴗóˇ)ᕤ docker://registry.redhat.io/rhelai1/granite-3.1-8b-lab-v1 model download completed successfully! ᕦ(òᴗóˇ)ᕤ

INFO 2025-03-19 07:50:11,913 instructlab.model.download:303: Available models (`ilab model list`):
+-----------------------------------+---------------------+---------+
| Model Name                        | Last Modified       | Size    |
+-----------------------------------+---------------------+---------+
| models/granite-3.1-8b-starter-v1  | 2025-03-19 07:28:01 | 15.2 GB |
| models/mixtral-8x7b-instruct-v0-1 | 2025-03-19 07:35:22 | 87.0 GB |
| models/prometheus-8x7b-v2-0       | 2025-03-19 07:42:48 | 87.0 GB |
| models/granite-3.1-8b-lab-v1      | 2025-03-19 07:50:11 | 15.2 GB |
+-----------------------------------+---------------------+---------+

[instruct@bastion ~]$
```
* 합성 데이터를 위한 LoRA 어댑터는 *ilab model list*로 보이지 않음

#### 2.2.3 모델 디렉터리에서 확인

실행 명령어
```bash
tree -F -L 2 .cache/instructlab/
```

실행 결과
```
[instruct@bastion ~]$ tree -F -L 2 .cache/instructlab/
.cache/instructlab/
|-- models/
|   |-- granite-3.1-8b-lab-v1/
|   |-- granite-3.1-8b-starter-v1/
|   |-- knowledge-adapter-v3/
|   |-- mixtral-8x7b-instruct-v0-1/
|   |-- prometheus-8x7b-v2-0/
|   `-- skills-adapter-v3/
`-- oci/
    |-- granite-3.1-8b-lab-v1/
    |-- granite-3.1-8b-starter-v1/
    |-- knowledge-adapter-v3/
    |-- mixtral-8x7b-instruct-v0-1/
    |-- prometheus-8x7b-v2-0/
    `-- skills-adapter-v3/

14 directories, 0 files

[instruct@bastion ~]$
```
* *ilab model*을 통해 내려 받은 컨테이너 이미지는 *models*와 *oci* 디렉터리에 분리되어 저정됨
* *ilab model download*를 통해 내려받은 모델 이미지를 *podman pull*로 내려 받으려 하면 에러가 표시됨
* *models* 및 *oci* 디렉터리에 있는 각각의 모델 이미지 데이터를 *tar*로 묶어 파일 형태로 이동이 가능
<br>

### 2.3 모델 디렉터리 아키텍처

#### 2.3.1 *.cache/instructlab/models/* 디렉터리 확인

실행 명령어
```bash
du -sh .cache/instructlab/models/*
tree -F -L 1 .cache/instructlab/models/
tree -F -L 2 .cache/instructlab/models/
```

실행 결과
```
[instruct@bastion ~]$ du -sh .cache/instructlab/models/*
4.0K    .cache/instructlab/models/granite-3.1-8b-lab-v1
4.0K    .cache/instructlab/models/granite-3.1-8b-starter-v1
4.0K    .cache/instructlab/models/knowledge-adapter-v3
4.0K    .cache/instructlab/models/mixtral-8x7b-instruct-v0-1
4.0K    .cache/instructlab/models/prometheus-8x7b-v2-0
4.0K    .cache/instructlab/models/skills-adapter-v3

[instruct@bastion ~]$ tree -F -L 1 .cache/instructlab/models/
.cache/instructlab/models/
|-- granite-3.1-8b-lab-v1/
|-- granite-3.1-8b-starter-v1/
|-- knowledge-adapter-v3/
|-- mixtral-8x7b-instruct-v0-1/
|-- prometheus-8x7b-v2-0/
`-- skills-adapter-v3/

6 directories, 0 files

[instruct@bastion ~]$ tree -F -L 2 .cache/instructlab/models/
.cache/instructlab/models/
|-- granite-3.1-8b-lab-v1/
|   |-- config.json -> /var/home/instruct/.cache/instructlab/oci/granite-3.1-8b-lab-v1/blobs/sha256/dd233853f746ecfcf429be6483821240a2f6e5f6957a27be05a3330a143a78e4
|   |-- generation_config.json -> /var/home/instruct/.cache/instructlab/oci/granite-3.1-8b-lab-v1/blobs/sha256/f609657ba3e37c56aa24b10462fbea526ea7447a12c0e1ca1d89a7312c1e5d3a
|   |-- model-00001-of-00004.safetensors -> /var/home/instruct/.cache/instructlab/oci/granite-3.1-8b-lab-v1/blobs/sha256/9e5c20e42c39b5492b9227f75af5b80f5f502f08f658f4ace68520a716cc68ff
|   |-- model-00002-of-00004.safetensors -> /var/home/instruct/.cache/instructlab/oci/granite-3.1-8b-lab-v1/blobs/sha256/72438510a985afcf4fb116bb2192190f585bea47581839f65fc91ce68bc1e394
|   |-- model-00003-of-00004.safetensors -> /var/home/instruct/.cache/instructlab/oci/granite-3.1-8b-lab-v1/blobs/sha256/3411b4c69b70469c3c7ac2a230017315072c8b34fdcc3882ed52fab8b4b42f84
|   |-- model-00004-of-00004.safetensors -> /var/home/instruct/.cache/instructlab/oci/granite-3.1-8b-lab-v1/blobs/sha256/ee911225bc656246a6e656876f7d26be94cdd98b20036c68f7d3403cd9c30b46
|   |-- model.safetensors.index.json -> /var/home/instruct/.cache/instructlab/oci/granite-3.1-8b-lab-v1/blobs/sha256/935d3259d28f1070e7079869ebfc41aef0a78a867698b26d587ecedf44b843a3
|   |-- special_tokens_map.json -> /var/home/instruct/.cache/instructlab/oci/granite-3.1-8b-lab-v1/blobs/sha256/5c78b58d992ee6c50167d4bd58e4489de5626ae4a2acfffd908ec4d646cb9552
|   |-- tokenizer.json -> /var/home/instruct/.cache/instructlab/oci/granite-3.1-8b-lab-v1/blobs/sha256/625f5206d172d93c7854f17ac8322f5dcc0113e35406cd217dae3297e53d8430
|   `-- tokenizer_config.json -> /var/home/instruct/.cache/instructlab/oci/granite-3.1-8b-lab-v1/blobs/sha256/adde9662090e3c7980ac20cc9df01411b74770aaf1023033212e9c5ca09e8d3e
|-- granite-3.1-8b-starter-v1/
|   |-- config.json -> /var/home/instruct/.cache/instructlab/oci/granite-3.1-8b-starter-v1/blobs/sha256/dd233853f746ecfcf429be6483821240a2f6e5f6957a27be05a3330a143a78e4
|   |-- generation_config.json -> /var/home/instruct/.cache/instructlab/oci/granite-3.1-8b-starter-v1/blobs/sha256/f609657ba3e37c56aa24b10462fbea526ea7447a12c0e1ca1d89a7312c1e5d3a
|   |-- model-00001-of-00004.safetensors -> /var/home/instruct/.cache/instructlab/oci/granite-3.1-8b-starter-v1/blobs/sha256/a05a85bd5165572c5a1606d02d64641b3be9d9afa633b92a9d35008d017c1af8
|   |-- model-00002-of-00004.safetensors -> /var/home/instruct/.cache/instructlab/oci/granite-3.1-8b-starter-v1/blobs/sha256/22b1424e35df80dea4400e417d1356989aacbf7f44443b23a66b8ef57aea2e3f
|   |-- model-00003-of-00004.safetensors -> /var/home/instruct/.cache/instructlab/oci/granite-3.1-8b-starter-v1/blobs/sha256/acc250559fc174d44f282eaf4f36aec4fbe7a3745c71dbd284ed08cdc06320bb
|   |-- model-00004-of-00004.safetensors -> /var/home/instruct/.cache/instructlab/oci/granite-3.1-8b-starter-v1/blobs/sha256/b19c07c7ada53a610b5b72332b7d5125bc116f3392bab48c48dd69f294ec33c7
|   |-- model.safetensors.index.json -> /var/home/instruct/.cache/instructlab/oci/granite-3.1-8b-starter-v1/blobs/sha256/935d3259d28f1070e7079869ebfc41aef0a78a867698b26d587ecedf44b843a3
|   |-- special_tokens_map.json -> /var/home/instruct/.cache/instructlab/oci/granite-3.1-8b-starter-v1/blobs/sha256/5c78b58d992ee6c50167d4bd58e4489de5626ae4a2acfffd908ec4d646cb9552
|   |-- tokenizer.json -> /var/home/instruct/.cache/instructlab/oci/granite-3.1-8b-starter-v1/blobs/sha256/625f5206d172d93c7854f17ac8322f5dcc0113e35406cd217dae3297e53d8430
|   `-- tokenizer_config.json -> /var/home/instruct/.cache/instructlab/oci/granite-3.1-8b-starter-v1/blobs/sha256/adde9662090e3c7980ac20cc9df01411b74770aaf1023033212e9c5ca09e8d3e
|-- knowledge-adapter-v3/
|   |-- LICENSE.txt -> /var/home/instruct/.cache/instructlab/oci/knowledge-adapter-v3/blobs/sha256/cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30
|   |-- README.md -> /var/home/instruct/.cache/instructlab/oci/knowledge-adapter-v3/blobs/sha256/488e082ff0d13ff1dff2c6cd487c9340a236a1d6be747f74e214f5dacd4cb129
|   |-- adapter_config.json -> /var/home/instruct/.cache/instructlab/oci/knowledge-adapter-v3/blobs/sha256/490c96c184aa23543b2c6f95ec352519105b637158c6289d9b45ac7e14105255
|   |-- adapter_model.safetensors -> /var/home/instruct/.cache/instructlab/oci/knowledge-adapter-v3/blobs/sha256/e84e6056962016df2698a79d024b2f6bd50bc638680b3893f708ebd5f0d61c1f
|   |-- new_embeddings.safetensors -> /var/home/instruct/.cache/instructlab/oci/knowledge-adapter-v3/blobs/sha256/c4334cbcdf177189e6aeee6e093fcf3241e397ab3ef2d8304f2baf814a6a93b5
|   |-- special_tokens_map.json -> /var/home/instruct/.cache/instructlab/oci/knowledge-adapter-v3/blobs/sha256/82d96d7a9e6ced037f12394b7ea6a5b02e6ca87e0d11edaa8d60d9be857ce7db
|   |-- tokenizer.json -> /var/home/instruct/.cache/instructlab/oci/knowledge-adapter-v3/blobs/sha256/0f17dc4a3b977d19b6214fba0ff619996c062eacf2204a0275cffee0ae9fc30c
|   `-- tokenizer_config.json -> /var/home/instruct/.cache/instructlab/oci/knowledge-adapter-v3/blobs/sha256/d2313c03a14930277aad48fdcc29aa62891b81b5882410f0c3c783b1ea97a3c0
|-- mixtral-8x7b-instruct-v0-1/
|   |-- README.md -> /var/home/instruct/.cache/instructlab/oci/mixtral-8x7b-instruct-v0-1/blobs/sha256/47324f06fdb57c8ea682bfc5d404a2772daa8d352dbadb268a7496168601aa04
|   |-- config.json -> /var/home/instruct/.cache/instructlab/oci/mixtral-8x7b-instruct-v0-1/blobs/sha256/9d56d04b36d0fd12ff54ae4c5bac769cc176e254e64ff71144614b6318b40793
|   |-- generation_config.json -> /var/home/instruct/.cache/instructlab/oci/mixtral-8x7b-instruct-v0-1/blobs/sha256/40e6ecbcedfc2b67b7fa8ba37216c9546c18c00242020b2b34f0b58c3558f680
|   |-- model-00001-of-00019.safetensors -> /var/home/instruct/.cache/instructlab/oci/mixtral-8x7b-instruct-v0-1/blobs/sha256/54669c5aec29fe5e4edd8098f7b564a137ba36be22ad25a194cd93f2bb54c940
|   |-- model-00002-of-00019.safetensors -> /var/home/instruct/.cache/instructlab/oci/mixtral-8x7b-instruct-v0-1/blobs/sha256/29e15364d8ab1d6ee229233381f295e9ff96237efed04750591f7da52ab6cc0e
|   |-- model-00003-of-00019.safetensors -> /var/home/instruct/.cache/instructlab/oci/mixtral-8x7b-instruct-v0-1/blobs/sha256/d0b63fca793cc29421cc5a46851992975cbe083aaded1b2f31113a45a0c90954
|   |-- model-00004-of-00019.safetensors -> /var/home/instruct/.cache/instructlab/oci/mixtral-8x7b-instruct-v0-1/blobs/sha256/67e0596920fe543415c0191e867a9a7de942a2924d6277cd98c8c5b34e11e436
|   |-- model-00005-of-00019.safetensors -> /var/home/instruct/.cache/instructlab/oci/mixtral-8x7b-instruct-v0-1/blobs/sha256/e330eabd70b467ddcbd8d3d6b2b9c3eba66655b0ed9f84e19f270da3623dc455
|   |-- model-00006-of-00019.safetensors -> /var/home/instruct/.cache/instructlab/oci/mixtral-8x7b-instruct-v0-1/blobs/sha256/048fa5347877b6d04eccf69765d23e5561cc9820dd4d0e5ba2df0100204dfb04
|   |-- model-00007-of-00019.safetensors -> /var/home/instruct/.cache/instructlab/oci/mixtral-8x7b-instruct-v0-1/blobs/sha256/83bfed6169c1f5b0ae854fb3311b576d06209ee5af45d7d46bcbc25098a4d02b
|   |-- model-00008-of-00019.safetensors -> /var/home/instruct/.cache/instructlab/oci/mixtral-8x7b-instruct-v0-1/blobs/sha256/af316ad784027edba47bf0959c821682c931c9c901d3d755038b358d9c7a28c0
|   |-- model-00009-of-00019.safetensors -> /var/home/instruct/.cache/instructlab/oci/mixtral-8x7b-instruct-v0-1/blobs/sha256/5882e4366c63048a0ad36ef6d90194a2fabdb42a2140be79c8e0ec2e8ac2ccc5
|   |-- model-00010-of-00019.safetensors -> /var/home/instruct/.cache/instructlab/oci/mixtral-8x7b-instruct-v0-1/blobs/sha256/77813d1dbee63419226ac15e4b8f28d075c3f7921cc664090236c491667eaf29
|   |-- model-00011-of-00019.safetensors -> /var/home/instruct/.cache/instructlab/oci/mixtral-8x7b-instruct-v0-1/blobs/sha256/ff24540d9967fe43c0c17cadaea7f2a34d080a2f9e58b913038b9bfd0bf8ca49
|   |-- model-00012-of-00019.safetensors -> /var/home/instruct/.cache/instructlab/oci/mixtral-8x7b-instruct-v0-1/blobs/sha256/48bc12845676eab1adb3cfce7037a7ecd664a0d5f5deaf93c7362a5bb5173298
|   |-- model-00013-of-00019.safetensors -> /var/home/instruct/.cache/instructlab/oci/mixtral-8x7b-instruct-v0-1/blobs/sha256/e56a2e7eda699bf4ec1433bd07d7cb86488420813e66463d2e2296d7accebc5c
|   |-- model-00014-of-00019.safetensors -> /var/home/instruct/.cache/instructlab/oci/mixtral-8x7b-instruct-v0-1/blobs/sha256/da627f6a3c8fdc6e35b9918d2aa53704d4044191fcc86c7c0b1ac57f00e707f7
|   |-- model-00015-of-00019.safetensors -> /var/home/instruct/.cache/instructlab/oci/mixtral-8x7b-instruct-v0-1/blobs/sha256/61e0f22bff93a68e114dbc3d75c1dd1e6687d554dba0cfdf1743950aa04ff1cf
|   |-- model-00016-of-00019.safetensors -> /var/home/instruct/.cache/instructlab/oci/mixtral-8x7b-instruct-v0-1/blobs/sha256/76466bfc2312f11559480981f212e4cca6e98096bf8df0fd90cce1f0f4709a9c
|   |-- model-00017-of-00019.safetensors -> /var/home/instruct/.cache/instructlab/oci/mixtral-8x7b-instruct-v0-1/blobs/sha256/570af3b802bedc0d54d0481d124f63d449dda40a4294a82a39f8dc3704057a5c
|   |-- model-00018-of-00019.safetensors -> /var/home/instruct/.cache/instructlab/oci/mixtral-8x7b-instruct-v0-1/blobs/sha256/4c603b65cbd5ddadcd5ece8add68b9d47f98f7264dbb0a5313172c78491e0329
|   |-- model-00019-of-00019.safetensors -> /var/home/instruct/.cache/instructlab/oci/mixtral-8x7b-instruct-v0-1/blobs/sha256/272f33c76bcacf6cfced497dc0579e107de3874b9f93126f5e69b5b1ae7e72a0
|   |-- model.safetensors.index.json -> /var/home/instruct/.cache/instructlab/oci/mixtral-8x7b-instruct-v0-1/blobs/sha256/a8f30ebfaf569d5cc6358a32009342a3e73d4553a340cc38a6319457d9dc13e6
|   |-- special_tokens_map.json -> /var/home/instruct/.cache/instructlab/oci/mixtral-8x7b-instruct-v0-1/blobs/sha256/6fa06efa2785e450051989a6f8fb4416b10149ded485ddd3f127a40734f5cfd0
|   |-- tokenizer.json -> /var/home/instruct/.cache/instructlab/oci/mixtral-8x7b-instruct-v0-1/blobs/sha256/11c08db21487c885d8c792180f0be237f6a261b89a46f128a6a80a3aa4bd1720
|   |-- tokenizer.model -> /var/home/instruct/.cache/instructlab/oci/mixtral-8x7b-instruct-v0-1/blobs/sha256/dadfd56d766715c61d2ef780a525ab43b8e6da4de6865bda3d95fdef5e134055
|   `-- tokenizer_config.json -> /var/home/instruct/.cache/instructlab/oci/mixtral-8x7b-instruct-v0-1/blobs/sha256/475361439e5c012de9dffdedc416a66a50f1a29f7aa80b375ba014fb13d6bb8a
|-- prometheus-8x7b-v2-0/
|   |-- README.md -> /var/home/instruct/.cache/instructlab/oci/prometheus-8x7b-v2-0/blobs/sha256/17e420ee7a3cc0bbb6a604984424f0e72d8762bd984bbee517d347844958ec98
|   |-- config.json -> /var/home/instruct/.cache/instructlab/oci/prometheus-8x7b-v2-0/blobs/sha256/9d56d04b36d0fd12ff54ae4c5bac769cc176e254e64ff71144614b6318b40793
|   |-- finegrained_eval.JPG -> /var/home/instruct/.cache/instructlab/oci/prometheus-8x7b-v2-0/blobs/sha256/cc0b434114a0e1e215984cddcc7e805c7f1cfab407f940bab919164544ec17e1
|   |-- generation_config.json -> /var/home/instruct/.cache/instructlab/oci/prometheus-8x7b-v2-0/blobs/sha256/40e6ecbcedfc2b67b7fa8ba37216c9546c18c00242020b2b34f0b58c3558f680
|   |-- model-00001-of-00019.safetensors -> /var/home/instruct/.cache/instructlab/oci/prometheus-8x7b-v2-0/blobs/sha256/45147a3fae61fb6b618f8e15a1eb958d32b99d6fa63f8185da7e9e9827f7a492
|   |-- model-00002-of-00019.safetensors -> /var/home/instruct/.cache/instructlab/oci/prometheus-8x7b-v2-0/blobs/sha256/a375e93d6f89971670ae9a262b46f4b3fd8c022ec2b06e1a8119541e9ea114b7
|   |-- model-00003-of-00019.safetensors -> /var/home/instruct/.cache/instructlab/oci/prometheus-8x7b-v2-0/blobs/sha256/07529e8461830eedbdbcccad524c388c91d6aa7ee138a6d30ad45660c5f14d11
|   |-- model-00004-of-00019.safetensors -> /var/home/instruct/.cache/instructlab/oci/prometheus-8x7b-v2-0/blobs/sha256/69239081714b0529eeb08d38e6e05e5daefda63594d9fdbdd99962e40b5822af
|   |-- model-00005-of-00019.safetensors -> /var/home/instruct/.cache/instructlab/oci/prometheus-8x7b-v2-0/blobs/sha256/82ba1df1bcff7a31fdc5864f4f85cc57065e3dd42fa26595caf04f2da44331df
|   |-- model-00006-of-00019.safetensors -> /var/home/instruct/.cache/instructlab/oci/prometheus-8x7b-v2-0/blobs/sha256/7dfbb89db40a7bc3944f32c51207e8b2b5125d7f3e5d50fa79042d4f296e368b
|   |-- model-00007-of-00019.safetensors -> /var/home/instruct/.cache/instructlab/oci/prometheus-8x7b-v2-0/blobs/sha256/d6b91c38dcac0c8314cd27aa5e20452d4332259c8df974421c6f7638691a3769
|   |-- model-00008-of-00019.safetensors -> /var/home/instruct/.cache/instructlab/oci/prometheus-8x7b-v2-0/blobs/sha256/042fa6758c753c337ce91f0b26d636caa2bdca5d45bcbc2a2685258f7685ad89
|   |-- model-00009-of-00019.safetensors -> /var/home/instruct/.cache/instructlab/oci/prometheus-8x7b-v2-0/blobs/sha256/fc2658c9dba220773cde8114bb4c855199832941564fd2e65c2fc8475753ba62
|   |-- model-00010-of-00019.safetensors -> /var/home/instruct/.cache/instructlab/oci/prometheus-8x7b-v2-0/blobs/sha256/958bf1eb6fc6ca8ba6a062d689d9a9803d107287150d66cc6c7bfe2b5bac4dea
|   |-- model-00011-of-00019.safetensors -> /var/home/instruct/.cache/instructlab/oci/prometheus-8x7b-v2-0/blobs/sha256/4cfc38eabca15b4ab48b1b4581ab2d258f96b28578f8466706d2b59a5accbbc1
|   |-- model-00012-of-00019.safetensors -> /var/home/instruct/.cache/instructlab/oci/prometheus-8x7b-v2-0/blobs/sha256/d8972380550511132aa943ffac47f0ccb7a8e2f0e3489efdec79f19cd3dac1e9
|   |-- model-00013-of-00019.safetensors -> /var/home/instruct/.cache/instructlab/oci/prometheus-8x7b-v2-0/blobs/sha256/ad148e16985f4d2680b4f3e0c3c2871f5ce1eba2fd015cecb332ee223978144b
|   |-- model-00014-of-00019.safetensors -> /var/home/instruct/.cache/instructlab/oci/prometheus-8x7b-v2-0/blobs/sha256/520bd83ae1b8c83d09cda5f511492a15b000bef2e13114370379b66f57239ba4
|   |-- model-00015-of-00019.safetensors -> /var/home/instruct/.cache/instructlab/oci/prometheus-8x7b-v2-0/blobs/sha256/189922a4c16e53c2ca085febd70ad8b2af2d0e339542fa8a3eebab52c9d40a43
|   |-- model-00016-of-00019.safetensors -> /var/home/instruct/.cache/instructlab/oci/prometheus-8x7b-v2-0/blobs/sha256/96b05ad261995d9850b83954ddb3302e165434b1a1cf4e8687d48e17fa37811b
|   |-- model-00017-of-00019.safetensors -> /var/home/instruct/.cache/instructlab/oci/prometheus-8x7b-v2-0/blobs/sha256/e6086166348b5394acd0f70d6496b8e6f48ce2c746846d6b3acc11326265d24b
|   |-- model-00018-of-00019.safetensors -> /var/home/instruct/.cache/instructlab/oci/prometheus-8x7b-v2-0/blobs/sha256/af6f32190c41e40f99183d4e94868fa25359fd133006cfe3c77c3adefc4c3803
|   |-- model-00019-of-00019.safetensors -> /var/home/instruct/.cache/instructlab/oci/prometheus-8x7b-v2-0/blobs/sha256/92470b0bd930b31b97b5f4b4a45eb235541412bc1856bd6c9c5934cc916e32da
|   |-- model.safetensors.index.json -> /var/home/instruct/.cache/instructlab/oci/prometheus-8x7b-v2-0/blobs/sha256/a8f30ebfaf569d5cc6358a32009342a3e73d4553a340cc38a6319457d9dc13e6
|   |-- special_tokens_map.json -> /var/home/instruct/.cache/instructlab/oci/prometheus-8x7b-v2-0/blobs/sha256/96bdbb8504d9967606e5f661ccc7cbbac44a3661af863a7a58614670a0ccab33
|   |-- tokenizer.json -> /var/home/instruct/.cache/instructlab/oci/prometheus-8x7b-v2-0/blobs/sha256/fc4f0bd70b3709312d9d1d9e5ba674794b6bc5abc17429897a540f93882f25fc
|   |-- tokenizer.model -> /var/home/instruct/.cache/instructlab/oci/prometheus-8x7b-v2-0/blobs/sha256/dadfd56d766715c61d2ef780a525ab43b8e6da4de6865bda3d95fdef5e134055
|   `-- tokenizer_config.json -> /var/home/instruct/.cache/instructlab/oci/prometheus-8x7b-v2-0/blobs/sha256/7ada2fa1461c581ee7a057c73fc0fe19b909347088e4a2aaa5bcbe10fc5e94a6
`-- skills-adapter-v3/
    |-- LICENSE.txt -> /var/home/instruct/.cache/instructlab/oci/skills-adapter-v3/blobs/sha256/cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30
    |-- README.md -> /var/home/instruct/.cache/instructlab/oci/skills-adapter-v3/blobs/sha256/488e082ff0d13ff1dff2c6cd487c9340a236a1d6be747f74e214f5dacd4cb129
    |-- adapter_config.json -> /var/home/instruct/.cache/instructlab/oci/skills-adapter-v3/blobs/sha256/7898f431429a8766ba4db28f29d5996f1832db70c045a244620e92244eeb9a44
    |-- adapter_model.safetensors -> /var/home/instruct/.cache/instructlab/oci/skills-adapter-v3/blobs/sha256/6f4761a5ce47f16484e5d8568897f238a7ff41103c7f099c222e07c578770b46
    |-- new_embeddings.safetensors -> /var/home/instruct/.cache/instructlab/oci/skills-adapter-v3/blobs/sha256/01f47425d01083b76f68889970226e7f43c330fa4a927c3873f18cc01dbde403
    |-- special_tokens_map.json -> /var/home/instruct/.cache/instructlab/oci/skills-adapter-v3/blobs/sha256/4452b845ab9ca2afa863f59f1411a959e8a32bb4334e264b0e71d5d17dd4dcb9
    |-- tokenizer.json -> /var/home/instruct/.cache/instructlab/oci/skills-adapter-v3/blobs/sha256/d8d4489231c6a3fedd10fc4534b1d7e69e32a3490750643c64b19487041fea58
    `-- tokenizer_config.json -> /var/home/instruct/.cache/instructlab/oci/skills-adapter-v3/blobs/sha256/5d44fdf2d36d0a83195ac2fd0eee7126fca2fddab78d72e15ed80832e0de299b

6 directories, 91 files

[instruct@bastion ~]$
```
* *modesl* 디렉터리에 모델 별 디렉터리에는 모델을 구성하는 파일이 심볼릭 파일로 있음
* 각 심볼릭 파일은 *oci* 디렉터리에 모델 별 디렉터리에 있는 *blobs/sha256/<IMAGE_LAYER_FILE>*을 가리킴

#### 2.3.2 *.cache/instructlab/oci/* 디렉터리 확인

실행 명령어
```bash
du -sh .cache/instructlab/oci/*
tree -F -L 3 .cache/instructlab/oci/
tree -F -L 4 .cache/instructlab/oci/
```

실행 결과
```
[instruct@bastion ~]$ du -sh .cache/instructlab/oci/*
16G     .cache/instructlab/oci/granite-3.1-8b-lab-v1
16G     .cache/instructlab/oci/granite-3.1-8b-starter-v1
111M    .cache/instructlab/oci/knowledge-adapter-v3
87G     .cache/instructlab/oci/mixtral-8x7b-instruct-v0-1
87G     .cache/instructlab/oci/prometheus-8x7b-v2-0
111M    .cache/instructlab/oci/skills-adapter-v3

[instruct@bastion ~]$ tree -F -L 3 .cache/instructlab/oci
.cache/instructlab/oci
|-- granite-3.1-8b-lab-v1/
|   |-- blobs/
|   |   `-- sha256/
|   |-- index.json
|   `-- oci-layout
|-- granite-3.1-8b-starter-v1/
|   |-- blobs/
|   |   `-- sha256/
|   |-- index.json
|   `-- oci-layout
|-- knowledge-adapter-v3/
|   |-- blobs/
|   |   `-- sha256/
|   |-- index.json
|   `-- oci-layout
|-- mixtral-8x7b-instruct-v0-1/
|   |-- blobs/
|   |   `-- sha256/
|   |-- index.json
|   `-- oci-layout
|-- prometheus-8x7b-v2-0/
|   |-- blobs/
|   |   `-- sha256/
|   |-- index.json
|   `-- oci-layout
`-- skills-adapter-v3/
    |-- blobs/
    |   `-- sha256/
    |-- index.json
    `-- oci-layout

18 directories, 12 files

[instruct@bastion ~]$ tree -F -L 4 .cache/instructlab/oci
.cache/instructlab/oci
|-- granite-3.1-8b-lab-v1/
|   |-- blobs/
|   |   `-- sha256/
|   |       |-- 3411b4c69b70469c3c7ac2a230017315072c8b34fdcc3882ed52fab8b4b42f84
|   |       |-- 44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a
|   |       |-- 5c78b58d992ee6c50167d4bd58e4489de5626ae4a2acfffd908ec4d646cb9552
|   |       |-- 625f5206d172d93c7854f17ac8322f5dcc0113e35406cd217dae3297e53d8430
|   |       |-- 72438510a985afcf4fb116bb2192190f585bea47581839f65fc91ce68bc1e394
|   |       |-- 7f3c90dba1a297c3e5e0ce8d4c7f6d07aabf23f28534b1c40522cd9d71eefc32
|   |       |-- 935d3259d28f1070e7079869ebfc41aef0a78a867698b26d587ecedf44b843a3
|   |       |-- 9e5c20e42c39b5492b9227f75af5b80f5f502f08f658f4ace68520a716cc68ff
|   |       |-- adde9662090e3c7980ac20cc9df01411b74770aaf1023033212e9c5ca09e8d3e
|   |       |-- dd233853f746ecfcf429be6483821240a2f6e5f6957a27be05a3330a143a78e4
|   |       |-- ee911225bc656246a6e656876f7d26be94cdd98b20036c68f7d3403cd9c30b46
|   |       `-- f609657ba3e37c56aa24b10462fbea526ea7447a12c0e1ca1d89a7312c1e5d3a
|   |-- index.json
|   `-- oci-layout
|-- granite-3.1-8b-starter-v1/
|   |-- blobs/
|   |   `-- sha256/
|   |       |-- 22b1424e35df80dea4400e417d1356989aacbf7f44443b23a66b8ef57aea2e3f
|   |       |-- 2a39d22b4a02e8b8b88f387e9b244828e0e880df57dfa5397d4a5be35b2b7f6d
|   |       |-- 44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a
|   |       |-- 5c78b58d992ee6c50167d4bd58e4489de5626ae4a2acfffd908ec4d646cb9552
|   |       |-- 625f5206d172d93c7854f17ac8322f5dcc0113e35406cd217dae3297e53d8430
|   |       |-- 935d3259d28f1070e7079869ebfc41aef0a78a867698b26d587ecedf44b843a3
|   |       |-- a05a85bd5165572c5a1606d02d64641b3be9d9afa633b92a9d35008d017c1af8
|   |       |-- acc250559fc174d44f282eaf4f36aec4fbe7a3745c71dbd284ed08cdc06320bb
|   |       |-- adde9662090e3c7980ac20cc9df01411b74770aaf1023033212e9c5ca09e8d3e
|   |       |-- b19c07c7ada53a610b5b72332b7d5125bc116f3392bab48c48dd69f294ec33c7
|   |       |-- dd233853f746ecfcf429be6483821240a2f6e5f6957a27be05a3330a143a78e4
|   |       `-- f609657ba3e37c56aa24b10462fbea526ea7447a12c0e1ca1d89a7312c1e5d3a
|   |-- index.json
|   `-- oci-layout
|-- knowledge-adapter-v3/
|   |-- blobs/
|   |   `-- sha256/
|   |       |-- 0f17dc4a3b977d19b6214fba0ff619996c062eacf2204a0275cffee0ae9fc30c
|   |       |-- 44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a
|   |       |-- 488e082ff0d13ff1dff2c6cd487c9340a236a1d6be747f74e214f5dacd4cb129
|   |       |-- 490c96c184aa23543b2c6f95ec352519105b637158c6289d9b45ac7e14105255
|   |       |-- 74b0b263fa5aec6a512d510cad130dc173a5e4f46dcf26ec1d2552e8d38dc352
|   |       |-- 82d96d7a9e6ced037f12394b7ea6a5b02e6ca87e0d11edaa8d60d9be857ce7db
|   |       |-- c4334cbcdf177189e6aeee6e093fcf3241e397ab3ef2d8304f2baf814a6a93b5
|   |       |-- cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30
|   |       |-- d2313c03a14930277aad48fdcc29aa62891b81b5882410f0c3c783b1ea97a3c0
|   |       `-- e84e6056962016df2698a79d024b2f6bd50bc638680b3893f708ebd5f0d61c1f
|   |-- index.json
|   `-- oci-layout
|-- mixtral-8x7b-instruct-v0-1/
|   |-- blobs/
|   |   `-- sha256/
|   |       |-- 048fa5347877b6d04eccf69765d23e5561cc9820dd4d0e5ba2df0100204dfb04
|   |       |-- 11c08db21487c885d8c792180f0be237f6a261b89a46f128a6a80a3aa4bd1720
|   |       |-- 272f33c76bcacf6cfced497dc0579e107de3874b9f93126f5e69b5b1ae7e72a0
|   |       |-- 29e15364d8ab1d6ee229233381f295e9ff96237efed04750591f7da52ab6cc0e
|   |       |-- 40e6ecbcedfc2b67b7fa8ba37216c9546c18c00242020b2b34f0b58c3558f680
|   |       |-- 44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a
|   |       |-- 47324f06fdb57c8ea682bfc5d404a2772daa8d352dbadb268a7496168601aa04
|   |       |-- 475361439e5c012de9dffdedc416a66a50f1a29f7aa80b375ba014fb13d6bb8a
|   |       |-- 48bc12845676eab1adb3cfce7037a7ecd664a0d5f5deaf93c7362a5bb5173298
|   |       |-- 4c603b65cbd5ddadcd5ece8add68b9d47f98f7264dbb0a5313172c78491e0329
|   |       |-- 54669c5aec29fe5e4edd8098f7b564a137ba36be22ad25a194cd93f2bb54c940
|   |       |-- 570af3b802bedc0d54d0481d124f63d449dda40a4294a82a39f8dc3704057a5c
|   |       |-- 5882e4366c63048a0ad36ef6d90194a2fabdb42a2140be79c8e0ec2e8ac2ccc5
|   |       |-- 61e0f22bff93a68e114dbc3d75c1dd1e6687d554dba0cfdf1743950aa04ff1cf
|   |       |-- 62623b86f2874c659b690a6341fec886daa36feb815d622cba13446a14156bbd
|   |       |-- 67e0596920fe543415c0191e867a9a7de942a2924d6277cd98c8c5b34e11e436
|   |       |-- 6fa06efa2785e450051989a6f8fb4416b10149ded485ddd3f127a40734f5cfd0
|   |       |-- 76466bfc2312f11559480981f212e4cca6e98096bf8df0fd90cce1f0f4709a9c
|   |       |-- 77813d1dbee63419226ac15e4b8f28d075c3f7921cc664090236c491667eaf29
|   |       |-- 83bfed6169c1f5b0ae854fb3311b576d06209ee5af45d7d46bcbc25098a4d02b
|   |       |-- 9d56d04b36d0fd12ff54ae4c5bac769cc176e254e64ff71144614b6318b40793
|   |       |-- a8f30ebfaf569d5cc6358a32009342a3e73d4553a340cc38a6319457d9dc13e6
|   |       |-- af316ad784027edba47bf0959c821682c931c9c901d3d755038b358d9c7a28c0
|   |       |-- d0b63fca793cc29421cc5a46851992975cbe083aaded1b2f31113a45a0c90954
|   |       |-- da627f6a3c8fdc6e35b9918d2aa53704d4044191fcc86c7c0b1ac57f00e707f7
|   |       |-- dadfd56d766715c61d2ef780a525ab43b8e6da4de6865bda3d95fdef5e134055
|   |       |-- e330eabd70b467ddcbd8d3d6b2b9c3eba66655b0ed9f84e19f270da3623dc455
|   |       |-- e56a2e7eda699bf4ec1433bd07d7cb86488420813e66463d2e2296d7accebc5c
|   |       `-- ff24540d9967fe43c0c17cadaea7f2a34d080a2f9e58b913038b9bfd0bf8ca49
|   |-- index.json
|   `-- oci-layout
|-- prometheus-8x7b-v2-0/
|   |-- blobs/
|   |   `-- sha256/
|   |       |-- 042fa6758c753c337ce91f0b26d636caa2bdca5d45bcbc2a2685258f7685ad89
|   |       |-- 07529e8461830eedbdbcccad524c388c91d6aa7ee138a6d30ad45660c5f14d11
|   |       |-- 17e420ee7a3cc0bbb6a604984424f0e72d8762bd984bbee517d347844958ec98
|   |       |-- 189922a4c16e53c2ca085febd70ad8b2af2d0e339542fa8a3eebab52c9d40a43
|   |       |-- 40e6ecbcedfc2b67b7fa8ba37216c9546c18c00242020b2b34f0b58c3558f680
|   |       |-- 44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a
|   |       |-- 45147a3fae61fb6b618f8e15a1eb958d32b99d6fa63f8185da7e9e9827f7a492
|   |       |-- 4cfc38eabca15b4ab48b1b4581ab2d258f96b28578f8466706d2b59a5accbbc1
|   |       |-- 520bd83ae1b8c83d09cda5f511492a15b000bef2e13114370379b66f57239ba4
|   |       |-- 69239081714b0529eeb08d38e6e05e5daefda63594d9fdbdd99962e40b5822af
|   |       |-- 7ada2fa1461c581ee7a057c73fc0fe19b909347088e4a2aaa5bcbe10fc5e94a6
|   |       |-- 7dfbb89db40a7bc3944f32c51207e8b2b5125d7f3e5d50fa79042d4f296e368b
|   |       |-- 82ba1df1bcff7a31fdc5864f4f85cc57065e3dd42fa26595caf04f2da44331df
|   |       |-- 92470b0bd930b31b97b5f4b4a45eb235541412bc1856bd6c9c5934cc916e32da
|   |       |-- 958bf1eb6fc6ca8ba6a062d689d9a9803d107287150d66cc6c7bfe2b5bac4dea
|   |       |-- 96b05ad261995d9850b83954ddb3302e165434b1a1cf4e8687d48e17fa37811b
|   |       |-- 96bdbb8504d9967606e5f661ccc7cbbac44a3661af863a7a58614670a0ccab33
|   |       |-- 9d56d04b36d0fd12ff54ae4c5bac769cc176e254e64ff71144614b6318b40793
|   |       |-- a375e93d6f89971670ae9a262b46f4b3fd8c022ec2b06e1a8119541e9ea114b7
|   |       |-- a8f30ebfaf569d5cc6358a32009342a3e73d4553a340cc38a6319457d9dc13e6
|   |       |-- ad148e16985f4d2680b4f3e0c3c2871f5ce1eba2fd015cecb332ee223978144b
|   |       |-- af6f32190c41e40f99183d4e94868fa25359fd133006cfe3c77c3adefc4c3803
|   |       |-- cc0b434114a0e1e215984cddcc7e805c7f1cfab407f940bab919164544ec17e1
|   |       |-- d6b91c38dcac0c8314cd27aa5e20452d4332259c8df974421c6f7638691a3769
|   |       |-- d8972380550511132aa943ffac47f0ccb7a8e2f0e3489efdec79f19cd3dac1e9
|   |       |-- dadfd56d766715c61d2ef780a525ab43b8e6da4de6865bda3d95fdef5e134055
|   |       |-- e6086166348b5394acd0f70d6496b8e6f48ce2c746846d6b3acc11326265d24b
|   |       |-- e67cf3a822da92c70e01902c354bea6f4450c0873d2092003268cf7c9b369056
|   |       |-- fc2658c9dba220773cde8114bb4c855199832941564fd2e65c2fc8475753ba62
|   |       `-- fc4f0bd70b3709312d9d1d9e5ba674794b6bc5abc17429897a540f93882f25fc
|   |-- index.json
|   `-- oci-layout
`-- skills-adapter-v3/
    |-- blobs/
    |   `-- sha256/
    |       |-- 01f47425d01083b76f68889970226e7f43c330fa4a927c3873f18cc01dbde403
    |       |-- 3102417b3ac425261834ebbb1c24754da0917a0143db52de0f572713c8f369e9
    |       |-- 44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a
    |       |-- 4452b845ab9ca2afa863f59f1411a959e8a32bb4334e264b0e71d5d17dd4dcb9
    |       |-- 488e082ff0d13ff1dff2c6cd487c9340a236a1d6be747f74e214f5dacd4cb129
    |       |-- 5d44fdf2d36d0a83195ac2fd0eee7126fca2fddab78d72e15ed80832e0de299b
    |       |-- 6f4761a5ce47f16484e5d8568897f238a7ff41103c7f099c222e07c578770b46
    |       |-- 7898f431429a8766ba4db28f29d5996f1832db70c045a244620e92244eeb9a44
    |       |-- cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30
    |       `-- d8d4489231c6a3fedd10fc4534b1d7e69e32a3490750643c64b19487041fea58
    |-- index.json
    `-- oci-layout

18 directories, 115 files

[instruct@bastion ~]$
```
* *sha256* 디렉터리에 이미지 계층 파일이 있음
<br>
<br>

## 3. 모델 기반 채팅 서비스

### 3.1 모델 서브 

#### 3.1.1 InstructLab의 기본 모델 서브 확인

실행 명령어
```bash
yq '.serve' .config/instructlab/config.yaml
```

실행 결과
```json
{
  "backend": "vllm",
  "chat_template": "auto",
  "llama_cpp": {
    "gpu_layers": -1,
    "llm_family": "",
    "max_ctx_size": 4096
  },
  "model_path": "/var/home/instruct/.cache/instructlab/models/granite-3.1-8b-lab-v1",
  "server": {
    "backend_type": "",
    "current_max_ctx_size": 4096,
    "host": "127.0.0.1",
    "port": 8000
  },
  "vllm": {
    "gpus": 4,
    "llm_family": "",
    "max_startup_attempts": 120,
    "vllm_args": [
      "--tensor-parallel-size",
      "4"
    ]
  }
}
```

#### 3.1.2 모델 서브 실행

실행 명령어
```bash
ilab model serve
```

실행 결과
```log
[instruct@bastion ~]$ ilab model serve
INFO 2025-03-19 08:08:22,795 instructlab.model.serve_backend:54: Setting backend_type in the serve config to vllm
INFO 2025-03-19 08:08:22,811 instructlab.model.serve_backend:60: Using model '/var/home/instruct/.cache/instructlab/models/granite-3.1-8b-lab-v1' with -1 gpu-layers and 4096 max context size.
INFO 2025-03-19 08:08:22,811 instructlab.model.serve_backend:92: '--gpus' flag used alongside '--tensor-parallel-size' in the vllm_args section of the config file. Using value of the --gpus flag.
INFO 2025-03-19 08:08:22,925 instructlab.model.backends.vllm:332: vLLM starting up on pid 53 at http://127.0.0.1:8000/v1
INFO 03-19 08:08:46 api_server.py:585] vLLM API server version 0.6.4.post1
INFO 03-19 08:08:46 api_server.py:586] args: Namespace(host='127.0.0.1', port=8000, uvicorn_log_level='info', allow_credentials=False, allowed_origins=['*'], allowed_methods=['*'], allowed_headers=['*'], api_key=None, lora_modules=None, prompt_adapters=None, chat_template='/tmp/tmpl_guw8nd', response_role='assistant', ssl_keyfile=None, ssl_certfile=None, ssl_ca_certs=None, ssl_cert_reqs=0, root_path=None, middleware=[], return_tokens_as_token_ids=False, disable_frontend_multiprocessing=False, enable_auto_tool_choice=False, tool_call_parser=None, tool_parser_plugin='', model='/var/home/instruct/.cache/instructlab/models/granite-3.1-8b-lab-v1', task='auto', tokenizer=None, skip_tokenizer_init=False, revision=None, code_revision=None, tokenizer_revision=None, tokenizer_mode='auto', chat_template_text_format='string', trust_remote_code=False, allowed_local_media_path=None, download_dir=None, load_format='auto', config_format=<ConfigFormat.AUTO: 'auto'>, dtype='auto', kv_cache_dtype='auto', quantization_param_path=None, max_model_len=None, guided_decoding_backend='outlines', distributed_executor_backend='mp', worker_use_ray=False, pipeline_parallel_size=1, tensor_parallel_size=4, max_parallel_loading_workers=None, ray_workers_use_nsight=False, block_size=16, enable_prefix_caching=False, disable_sliding_window=False, use_v2_block_manager=False, num_lookahead_slots=0, seed=0, swap_space=4, cpu_offload_gb=0, gpu_memory_utilization=0.9, num_gpu_blocks_override=None, max_num_batched_tokens=None, max_num_seqs=256, max_logprobs=20, disable_log_stats=False, quantization=None, rope_scaling=None, rope_theta=None, hf_overrides=None, enforce_eager=False, max_seq_len_to_capture=8192, disable_custom_all_reduce=False, tokenizer_pool_size=0, tokenizer_pool_type='ray', tokenizer_pool_extra_config=None, limit_mm_per_prompt=None, mm_processor_kwargs=None, enable_lora=False, enable_lora_bias=False, max_loras=1, max_lora_rank=16, lora_extra_vocab_size=256, lora_dtype='auto', long_lora_scaling_factors=None, max_cpu_loras=None, fully_sharded_loras=False, enable_prompt_adapter=False, max_prompt_adapters=1, max_prompt_adapter_token=0, device='auto', num_scheduler_steps=1, multi_step_stream_outputs=True, scheduler_delay_factor=0.0, enable_chunked_prefill=None, speculative_model=None, speculative_model_quantization=None, num_speculative_tokens=None, speculative_disable_mqa_scorer=False, speculative_draft_tensor_parallel_size=None, speculative_max_model_len=None, speculative_disable_by_batch_size=None, ngram_prompt_lookup_max=None, ngram_prompt_lookup_min=None, spec_decoding_acceptance_method='rejection_sampler', typical_acceptance_sampler_posterior_threshold=None, typical_acceptance_sampler_posterior_alpha=None, disable_logprobs_during_spec_decoding=None, model_loader_extra_config=None, ignore_patterns=[], preemption_mode=None, served_model_name=None, qlora_adapter_name_or_path=None, otlp_traces_endpoint=None, collect_detailed_traces=None, disable_async_output_proc=False, scheduling_policy='fcfs', override_neuron_config=None, override_pooler_config=None, disable_log_requests=False, max_log_len=None, disable_fastapi_docs=False, enable_prompt_tokens_details=False)
INFO 03-19 08:08:46 api_server.py:175] Multiprocessing frontend to use ipc:///tmp/cc1f00a5-a119-44e8-9804-88fa6f907607 for IPC Path.
INFO 03-19 08:08:46 api_server.py:194] Started engine process with PID 73
INFO 03-19 08:08:46 config.py:1861] Downcasting torch.float32 to torch.float16.
INFO 03-19 08:08:53 config.py:1861] Downcasting torch.float32 to torch.float16.
INFO 03-19 08:08:54 config.py:1136] Chunked prefill is enabled with max_num_batched_tokens=512.
INFO 03-19 08:09:00 config.py:1136] Chunked prefill is enabled with max_num_batched_tokens=512.
INFO 03-19 08:09:00 llm_engine.py:249] Initializing an LLM engine (v0.6.4.post1) with config: model='/var/home/instruct/.cache/instructlab/models/granite-3.1-8b-lab-v1', speculative_config=None, tokenizer='/var/home/instruct/.cache/instructlab/models/granite-3.1-8b-lab-v1', skip_tokenizer_init=False, tokenizer_mode=auto, revision=None, override_neuron_config=None, tokenizer_revision=None, trust_remote_code=False, dtype=torch.float16, max_seq_len=131072, download_dir=None, load_format=LoadFormat.AUTO, tensor_parallel_size=4, pipeline_parallel_size=1, disable_custom_all_reduce=False, quantization=None, enforce_eager=False, kv_cache_dtype=auto, quantization_param_path=None, device_config=cuda, decoding_config=DecodingConfig(guided_decoding_backend='outlines'), observability_config=ObservabilityConfig(otlp_traces_endpoint=None, collect_model_forward_time=False, collect_model_execute_time=False), seed=0, served_model_name=/var/home/instruct/.cache/instructlab/models/granite-3.1-8b-lab-v1, num_scheduler_steps=1, chunked_prefill_enabled=True multi_step_stream_outputs=True, enable_prefix_caching=False, use_async_output_proc=True, use_cached_outputs=True, chat_template_text_format=string, mm_processor_kwargs=None, pooler_config=None)
INFO 03-19 08:09:00 custom_cache_manager.py:17] Setting Triton cache manager to: vllm.triton_utils.custom_cache_manager:CustomCacheManager
INFO 03-19 08:09:01 selector.py:135] Using Flash Attention backend.
(VllmWorkerProcess pid=181) INFO 03-19 08:09:01 selector.py:135] Using Flash Attention backend.
(VllmWorkerProcess pid=181) INFO 03-19 08:09:01 multiproc_worker_utils.py:215] Worker ready; awaiting tasks
(VllmWorkerProcess pid=180) INFO 03-19 08:09:01 selector.py:135] Using Flash Attention backend.
(VllmWorkerProcess pid=180) INFO 03-19 08:09:01 multiproc_worker_utils.py:215] Worker ready; awaiting tasks
(VllmWorkerProcess pid=182) INFO 03-19 08:09:01 selector.py:135] Using Flash Attention backend.
(VllmWorkerProcess pid=182) INFO 03-19 08:09:01 multiproc_worker_utils.py:215] Worker ready; awaiting tasks
(VllmWorkerProcess pid=181) INFO 03-19 08:09:02 utils.py:961] Found nccl from library libnccl.so.2
INFO 03-19 08:09:02 utils.py:961] Found nccl from library libnccl.so.2
(VllmWorkerProcess pid=180) INFO 03-19 08:09:02 utils.py:961] Found nccl from library libnccl.so.2
(VllmWorkerProcess pid=182) INFO 03-19 08:09:02 utils.py:961] Found nccl from library libnccl.so.2
INFO 03-19 08:09:02 pynccl.py:69] vLLM is using nccl==2.25.1
(VllmWorkerProcess pid=181) INFO 03-19 08:09:02 pynccl.py:69] vLLM is using nccl==2.25.1
(VllmWorkerProcess pid=180) INFO 03-19 08:09:02 pynccl.py:69] vLLM is using nccl==2.25.1
(VllmWorkerProcess pid=182) INFO 03-19 08:09:02 pynccl.py:69] vLLM is using nccl==2.25.1
(VllmWorkerProcess pid=180) WARNING 03-19 08:09:03 custom_all_reduce.py:134] Custom allreduce is disabled because it's not supported on more than two PCIe-only GPUs. To silence this warning, specify disable_custom_all_reduce=True explicitly.

^C

INFO 2025-03-19 08:17:28,422 instructlab.model.backends.vllm:85: vLLM server terminated by keyboard
INFO 03-19 08:17:28 launcher.py:57] Shutting down FastAPI HTTP server.
INFO 03-19 08:17:28 multiproc_worker_utils.py:133] Terminating local vLLM worker processes
(VllmWorkerProcess pid=181) INFO 03-19 08:17:28 multiproc_worker_utils.py:240] Worker exiting
(VllmWorkerProcess pid=180) INFO 03-19 08:17:28 multiproc_worker_utils.py:240] Worker exiting
(VllmWorkerProcess pid=182) INFO 03-19 08:17:28 multiproc_worker_utils.py:240] Worker exiting
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
/usr/lib64/python3.11/multiprocessing/resource_tracker.py:254: UserWarning: resource_tracker: There appear to be 1 leaked shared_memory objects to clean up at shutdown
  warnings.warn('resource_tracker: There appear to be %d '
INFO 2025-03-19 08:17:35,898 instructlab.model.backends.vllm:494: Waiting for GPU VRAM reclamation...

[instruct@bastion ~]$
```

#### 3.1.3 실행 중인 프로세스 확인

실행 명령어
```bash
ps -u instruct
```

실행 결과
```
[instruct@bastion ~]$ ps -u instruct
    PID TTY          TIME CMD
   2029 ?        00:00:00 systemd
   2031 ?        00:00:00 (sd-pam)
   2045 ?        00:00:00 sshd
   2046 pts/0    00:00:00 bash
   2179 ?        00:00:00 catatonit
   2195 ?        00:00:00 dbus-broker-lau
   2196 ?        00:00:00 dbus-broker
   7445 ?        00:00:00 sshd
   7446 pts/1    00:00:00 bash
   7914 pts/0    00:00:00 podman
   7936 ?        00:00:09 fuse-overlayfs
   7946 ?        00:00:00 conmon
   7948 pts/0    00:00:05 ilab
   8002 ?        00:00:10 python3.11
   8023 ?        00:00:00 python3.11
   8024 ?        00:00:37 python3.11
   8133 ?        00:00:31 python3.11
   8134 ?        00:00:31 python3.11
   8135 ?        00:00:31 python3.11
   8435 pts/1    00:00:00 ps

[instruct@bastion ~]$
```

#### 3.1.4 `podman` 프로세스

실행 명령어
```bash
pstree -ps -a 7914
```

실행 결과
```
[instruct@bastion ~]$ pstree -ps -a 7914
systemd,1 --switched-root --system --deserialize 31
  `-sshd,1981
      `-sshd,2025
          `-sshd,2045
              `-bash,2046
                  `-podman,7914 run --rm -it --device nvidia.com/gpu=all --security-opt label=disable --net host --shm-size 10G --pids-limit -1 -v /var/home/instruct:/var/home/instruct -v ...
                      |-{podman},7918
                      |-{podman},7919
                      |-{podman},7920
                      |-{podman},7921
                      |-{podman},7922
                      |-{podman},7923
                      |-{podman},7924
                      |-{podman},7925
                      |-{podman},7926
                      |-{podman},7927
                      |-{podman},7928
                      |-{podman},7929
                      |-{podman},7930
                      |-{podman},7931
                      |-{podman},7932
                      |-{podman},7933
                      |-{podman},7934
                      |-{podman},7939
                      |-{podman},7940
                      |-{podman},7941
                      |-{podman},7943
                      |-{podman},7944
                      `-{podman},7945

[instruct@bastion ~]$
```

#### 3.1.5 `fuse-overlayfs` 프로세스

실행 명령어
```bash
pstree -ps -a 7936
```

실행 결과
```
[instruct@bastion ~]$ pstree -ps -a 7936
systemd,1 --switched-root --system --deserialize 31
  `-fuse-overlayfs,7936 -olowerdir=/usr/lib/containers/storage/overlay/l/3XMERXCKYN5AQ4UVB7KXEJIALJ,upperdir=/var/home/instruct/.local/share/containers/storage/overlay/466a656b79640ebdcbcef5752d4e41ea143d84fec9aa80a51d7a2b7eb8be5387/d

[instruct@bastion ~]$ 
```

#### 3.1.6 `conmon` 프로세스

실행 명령어
```bash
pstree -ps -a 7946
```

실행 결과
```
[instruct@bastion ~]$ pstree -ps -a 7946
systemd,1 --switched-root --system --deserialize 31
  `-conmon,7946 --api-version 1 -c 86b58abf47572315d2a55f3a7b99a3fb0cfac31cd8303ce342bffca2dd58cdc6 -u 86b58abf47572315d2a55f3a7b99a3fb0cfac31cd8303ce342bffca2dd58cdc6 -r /usr/bin/crun -b/var/home/instruct/.local/share/containers/stor
      `-ilab,7948 /opt/app-root/bin/ilab model serve
          `-python3.11,8002 -m vllm.entrypoints.openai.api_server --host 127.0.0.1 --port 8000 --model /var/home/instruct/.cache/instructlab/models/granite-3.1-8b-lab-v1 --chat-template /tmp/tmpx_hr9x31 ...
              |-python3.11,8023 -c from multiprocessing.resource_tracker import main;main(14)
              |-python3.11,8024 -c from multiprocessing.spawn import spawn_main; spawn_main(tracker_fd=15, pipe_handle=17) --multiprocessing-fork
              |   |-python3.11,8133 -c from multiprocessing.spawn import spawn_main; spawn_main(tracker_fd=15, pipe_handle=17) --multiprocessing-fork
              |   |   |-{python3.11},8142

              ...<snip>...
              
              |   |   `-{python3.11},8280
              |   |-python3.11,8134 -c from multiprocessing.spawn import spawn_main; spawn_main(tracker_fd=15, pipe_handle=17) --multiprocessing-fork
              |   |   |-{python3.11},8143

              ...<snip>...
              
              |   |   `-{python3.11},8279
              |   |-python3.11,8135 -c from multiprocessing.spawn import spawn_main; spawn_main(tracker_fd=15, pipe_handle=17) --multiprocessing-fork
              |   |   |-{python3.11},8157
              
              ...<snip>...

              `-{python3.11},8310

[instruct@bastion ~]$
```

#### 3.1.7 `ilab` 프로세스

실행 명령어
```bash
pstree -ps -a 7948
```

실행 결과
```
[instruct@bastion ~]$ pstree -ps -a 7948
systemd,1 --switched-root --system --deserialize 31
  `-conmon,7946 --api-version 1 -c 86b58abf47572315d2a55f3a7b99a3fb0cfac31cd8303ce342bffca2dd58cdc6 -u 86b58abf47572315d2a55f3a7b99a3fb0cfac31cd8303ce342bffca2dd58cdc6 -r /usr/bin/crun -b/var/home/instruct/.local/share/containers/stor
      `-ilab,7948 /opt/app-root/bin/ilab model serve
          `-python3.11,8002 -m vllm.entrypoints.openai.api_server --host 127.0.0.1 --port 8000 --model /var/home/instruct/.cache/instructlab/models/granite-3.1-8b-lab-v1 --chat-template /tmp/tmpx_hr9x31 ...
              |-python3.11,8023 -c from multiprocessing.resource_tracker import main;main(14)
              |-python3.11,8024 -c from multiprocessing.spawn import spawn_main; spawn_main(tracker_fd=15, pipe_handle=17) --multiprocessing-fork
              |   |-python3.11,8133 -c from multiprocessing.spawn import spawn_main; spawn_main(tracker_fd=15, pipe_handle=17) --multiprocessing-fork
              |   |   |-{python3.11},8142
              |   |   |-{python3.11},8158
              
              ...<snip>...

              |   |   `-{python3.11},8280
              |   |-python3.11,8134 -c from multiprocessing.spawn import spawn_main; spawn_main(tracker_fd=15, pipe_handle=17) --multiprocessing-fork
              |   |   |-{python3.11},8143

              ...<snip>...

              |   |   `-{python3.11},8279
              |   |-python3.11,8135 -c from multiprocessing.spawn import spawn_main; spawn_main(tracker_fd=15, pipe_handle=17) --multiprocessing-fork
              |   |   |-{python3.11},8157

              ...<snip>...

              |-{python3.11},8309
              `-{python3.11},8310

[instruct@bastion ~]$
```
<br>

### 3.2 모델 채팅

#### 3.2.1 InstructLab의 기본 모델 채팅 확인

실행 명령어
```bash
yq '.chat' .config/instructlab/config.yaml
```

실행 결과
```json
{
  "context": "default",
  "logs_dir": "/var/home/instruct/.local/share/instructlab/chatlogs",
  "max_tokens": null,
  "model": "/var/home/instruct/.cache/instructlab/models/granite-3.1-8b-lab-v1",
  "session": null,
  "temperature": 1.0,
  "vi_mode": false,
  "visible_overflow": true
}
```

#### 3.2.2 채팅 실행

실행 명령어
```bash
ilab model chat
```

실행 결과
```
[instruct@bastion ~]$ ilab model chat
╭───────────────────────────────────────────────────── system ──────────────────────────────────────────────────────╮
│ Welcome to InstructLab Chat w/ GRANITE-3.1-8B-LAB-V1 (type /h for help)                                           │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
>>> hello                                                                                                [S][default]
╭────────────────────────────────────────────── granite-3.1-8b-lab-v1 ──────────────────────────────────────────────╮
│ Hello! How can I assist you today?                                                                                │
╰─────────────────────────────────────────────────────────────────────────────────────────── elapsed 0.176 seconds ─╯
>>> 안녕하세요?                                                                                          [S][default]
╭────────────────────────────────────────────── granite-3.1-8b-lab-v1 ──────────────────────────────────────────────╮
│ 안녕하세요! I'm glad you reached out. I'm here to help answer any questions you have.                             │
╰─────────────────────────────────────────────────────────────────────────────────────────── elapsed 0.481 seconds ─╯
>>> what is your job?                                                                                    [S][default]
╭────────────────────────────────────────────── granite-3.1-8b-lab-v1 ──────────────────────────────────────────────╮
│ I'm designed to provide information and assistance to users, such as answering questions, providing               │
│ recommendations, and helping users with tasks.                                                                    │
╰─────────────────────────────────────────────────────────────────────────────────────────── elapsed 0.522 seconds ─╯
>>> 당신의 직업은 무엇입니까?                                                                            [S][default]
╭────────────────────────────────────────────── granite-3.1-8b-lab-v1 ──────────────────────────────────────────────╮
│ 나는 정보와 지침을 제공하고 사용자를 도와주는 기계로 설계되어 있으며, 질문을 답변하고 상담을 제공하며, 작업을     │
│ 돕는 등의 독특한 유능성을 가지고 있습니다.                                                                        │
╰─────────────────────────────────────────────────────────────────────────────────────────── elapsed 1.248 seconds ─╯
>>> exit                                                                                                 [S][default]
[instruct@bastion ~]$
```

#### 3.2.3 실행 중인 프로세스 확인

실행 명령어
```bash
ps -u instruct
```

실행 결과
```
[instruct@bastion ~]$ ps -u instruct
    PID TTY          TIME CMD
   2029 ?        00:00:00 systemd
   2031 ?        00:00:00 (sd-pam)
   2045 ?        00:00:00 sshd
   2046 pts/0    00:00:00 bash
   2179 ?        00:00:00 catatonit
   2195 ?        00:00:00 dbus-broker-lau
   2196 ?        00:00:00 dbus-broker
   7445 ?        00:00:00 sshd
   7446 pts/1    00:00:00 bash
   7914 pts/0    00:00:03 podman
   7936 ?        00:00:09 fuse-overlayfs
   7946 ?        00:00:00 conmon
   7948 pts/0    00:00:05 ilab
   8002 ?        00:00:12 python3.11
   8023 ?        00:00:00 python3.11
   8024 ?        00:00:47 python3.11
   8133 ?        00:00:42 python3.11
   8134 ?        00:00:41 python3.11
   8135 ?        00:00:41 python3.11
   8564 pts/1    00:00:00 podman
   8589 ?        00:00:02 fuse-overlayfs
   8604 ?        00:00:00 conmon
   8606 pts/0    00:00:05 ilab
   8666 ?        00:00:00 sshd
   8667 pts/2    00:00:00 bash
   8694 pts/2    00:00:00 ps

[instruct@bastion ~]$
```

#### 3.2.4 `podman` 프로세스

실행 명령어
```bash
pstree -ps -a 8564
```

실행 결과
```
[instruct@bastion ~]$ pstree -ps -a 8564
systemd,1 --switched-root --system --deserialize 31
  `-sshd,1981
      `-sshd,7442
          `-sshd,7445
              `-bash,7446
                  `-podman,8564 run --rm -it --device nvidia.com/gpu=all --security-opt label=disable --net host --shm-size 10G ...
                      |-{podman},8568
                      |-{podman},8569
                      |-{podman},8570
                      |-{podman},8571
                      |-{podman},8572
                      |-{podman},8573
                      |-{podman},8574
                      |-{podman},8575
                      |-{podman},8576
                      |-{podman},8577
                      |-{podman},8578
                      |-{podman},8579
                      |-{podman},8581
                      |-{podman},8582
                      |-{podman},8585
                      |-{podman},8586
                      |-{podman},8597
                      |-{podman},8598
                      |-{podman},8599
                      |-{podman},8600
                      `-{podman},8601

[instruct@bastion ~]$
```

#### 3.2.5 `fuse-overlayfs` 프로세스

실행 명령어
```bash
pstree -ps -a 8589
```

실행 결과
```
[instruct@bastion ~]$ pstree -ps -a 8589
systemd,1 --switched-root --system --deserialize 31
  `-fuse-overlayfs,8589 -olowerdir=/usr/lib/containers/storage/overlay/l/3XMERXCKYN5AQ4UVB7KXEJIALJ,upperdir=/var/home/instruct/.local/sh

[instruct@bastion ~]$
```

#### 3.2.6 `conmon` 프로세스

실행 명령어
```bash
pstree -ps -a 8604
```

실행 결과
```
[instruct@bastion ~]$ pstree -ps -a 8604
systemd,1 --switched-root --system --deserialize 31
  `-conmon,8604 --api-version 1 -c 7e8e8168543bc064e990b9fe6501f2e35fdee58566606e24e9d815622d870033 -u7e8e8168543bc064e990b9fe6501f2e35fd
      `-ilab,8606 /opt/app-root/bin/ilab model chat

[instruct@bastion ~]$
```

#### 3.2.7 `ilab` 프로세스

실행 명령어
```bash
pstree -ps -a 8606
```

실행 결과
```
[instruct@bastion ~]$ pstree -ps -a 8606
systemd,1 --switched-root --system --deserialize 31
  `-conmon,8604 --api-version 1 -c 7e8e8168543bc064e990b9fe6501f2e35fdee58566606e24e9d815622d870033 -u7e8e8168543bc064e990b9fe6501f2e35fd
      `-ilab,8606 /opt/app-root/bin/ilab model chat

[instruct@bastion ~]$
```
<br>
<br>

------
[차례](../README.md)