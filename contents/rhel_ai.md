# RHEL AI 


**목차**
1. [](./rhel_ai.md#1-rhel-ai의-instructlab)<br>
2. [](./rhel_ai.md#2-rhel-ai를-위한-모델-확인-및-구성)<br>
3. []()<br>
<br>
<hr>
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
* ~/.local/share/instructlab/phased/<phase1-or-phase2>/checkpoints/
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
 |Granite LLM 커스텀을 위한 모델|granite-3.1-8b-starter-v1<br>mixtral-8x7b-instruct-v0-1<br>prometheus-8x7b-v2-0|하드웨어 벤더에 종속된 기본 LLM<br>SDG를 위한 교사 모델<br>훈련 및 평가를 위한 판단 모델|
 |LLM 커스텀을 위한 도구|knowledge-adapter-v3<br>skills-adapter-v3|SDG를 위한 LoRA 계층 지식 어댑터<br>SDG를 위한 LoRA 계층 기술 어댑터|
 |추론 서비스 모델|granite-3.1-8b-lab-v1|Granite 3.1 버전|
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
tree -F -L 1 .cache/instructlab/models/
```

실행 결과
```
[instruct@bastion ~]$ tree -F -L 1 .cache/instructlab/models/
.cache/instructlab/models/
|-- granite-3.1-8b-lab-v1/
|-- granite-3.1-8b-starter-v1/
|-- knowledge-adapter-v3/
|-- mixtral-8x7b-instruct-v0-1/
|-- prometheus-8x7b-v2-0/
`-- skills-adapter-v3/

6 directories, 0 files

[instruct@bastion ~]$
```
<br>
<br>

## 3. 

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


<br>
<br>

실행 명령어
```bash

```

실행 결과
```

```


------
[차례](../README.md)