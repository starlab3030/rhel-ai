# RHEL AI

<img align="left" src="/common-images/이승일--II_컴퓨터.png" width="300px" height="300px" title="100px" alt="안녕"></img>
<br>
<br>
<br>
&nbsp; 1. [RHSC 키노트 데모 소개](./rhsc-demo/introdution-of-lab.md)<br>
&nbsp; 2. [InstructLab 시작](./rhsc-demo/start-with-instructlab.md)<br>
&nbsp; 3. [AI를 앱에 통합](./rhsc-demo/integrate-ai-into-app.md)<br>


[instruct@bastion ~]$ yq -y . .config/instructlab/config.yaml
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
  gpus: 8
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
  cpu_info: null
  gpu_count: 8
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
    gpus: 8
    llm_family: ''
    max_startup_attempts: 120
    vllm_args:
      - --tensor-parallel-size
      - '8'
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
  nproc_per_node: 8
  num_epochs: 8
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

[instruct@bastion ~]$ podman search registry.redhat.io/rhelai1/granite-3.1-8b
NAME                                                  DESCRIPTION
registry.redhat.io/rhelai1/granite-3.1-8b-starter-v1  Red Hat image for granite-3.1-8b-starter-v1
registry.redhat.io/rhelai1/granite-3.1-8b-lab-v1      Red Hat image for granite-3.1-8b-lab-v1

[instruct@bastion ~]$ ilab model download --repository docker://registry.redhat.io/rhelai1/granite-3.1-8b-starter-v1 --release latest                          INFO 2025-03-18 12:59:31,619 instructlab.model.download:193: Downloading model from OCI registry:
    Model: docker://registry.redhat.io/rhelai1/granite-3.1-8b-starter-v1@latest
    Destination: /var/home/instruct/.cache/instructlab/models
Copying blob f609657ba3e3 done   |
Copying blob dd233853f746 done   |
Copying blob a05a85bd5165 done   |
Copying blob b19c07c7ada5 done   |
Copying blob acc250559fc1 done   |
Copying blob 22b1424e35df done   |
Copying blob 935d3259d28f done   |
Copying blob 5c78b58d992e done   |
Copying blob 625f5206d172 done   |
Copying blob adde9662090e done   |
Copying config 44136fa355 done   |
Writing manifest to image destination
INFO 2025-03-18 13:03:04,695 instructlab.model.download:289:
ᕦ(òᴗóˇ)ᕤ docker://registry.redhat.io/rhelai1/granite-3.1-8b-starter-v1 model download completed successfully! ᕦ(òᴗóˇ)ᕤ

INFO 2025-03-18 13:03:04,696 instructlab.model.download:303: Available models (`ilab model list`):
+----------------------------------+---------------------+---------+
| Model Name                       | Last Modified       | Size    |
+----------------------------------+---------------------+---------+
| models/granite-3.1-8b-starter-v1 | 2025-03-18 13:03:04 | 15.2 GB |
+----------------------------------+---------------------+---------+
[instruct@bastion ~]$ ilab model download --repository docker://registry.redhat.io/rhelai1/granite-3.1-8b-lab-v1 --release latest
INFO 2025-03-18 13:06:47,686 instructlab.model.download:193: Downloading model from OCI registry:
    Model: docker://registry.redhat.io/rhelai1/granite-3.1-8b-lab-v1@latest
    Destination: /var/home/instruct/.cache/instructlab/models
Copying blob ee911225bc65 done   |
Copying blob 9e5c20e42c39 done   |
Copying blob 3411b4c69b70 done   |
Copying blob 72438510a985 done   |
Copying blob dd233853f746 done   |
Copying blob f609657ba3e3 done   |
Copying blob 935d3259d28f done   |
Copying blob 5c78b58d992e done   |
Copying blob 625f5206d172 done   |
Copying blob adde9662090e done   |
Copying config 44136fa355 done   |
Writing manifest to image destination
INFO 2025-03-18 13:09:17,861 instructlab.model.download:289:
ᕦ(òᴗóˇ)ᕤ docker://registry.redhat.io/rhelai1/granite-3.1-8b-lab-v1 model download completed successfully! ᕦ(òᴗóˇ)ᕤ

INFO 2025-03-18 13:09:17,861 instructlab.model.download:303: Available models (`ilab model list`):
+----------------------------------+---------------------+---------+
| Model Name                       | Last Modified       | Size    |
+----------------------------------+---------------------+---------+
| models/granite-3.1-8b-starter-v1 | 2025-03-18 13:03:04 | 15.2 GB |
| models/granite-3.1-8b-lab-v1     | 2025-03-18 13:09:17 | 15.2 GB |
+----------------------------------+---------------------+---------+

[instruct@bastion ~]$ ilab model download --repository docker://registry.redhat.io/rhelai1/prometheus-8x7b-v2-0 --release latest
INFO 2025-03-18 13:20:40,006 instructlab.model.download:193: Downloading model from OCI registry:
    Model: docker://registry.redhat.io/rhelai1/prometheus-8x7b-v2-0@latest
    Destination: /var/home/instruct/.cache/instructlab/models
Copying blob a375e93d6f89 done   |
Copying blob 40e6ecbcedfc done   |
Copying blob cc0b434114a0 done   |
Copying blob 9d56d04b36d0 done   |
Copying blob 45147a3fae61 done   |
Copying blob 17e420ee7a3c done   |
Copying blob 07529e846183 done   |
Copying blob 69239081714b done   |
Copying blob 82ba1df1bcff done   |
Copying blob 7dfbb89db40a done   |
Copying blob d6b91c38dcac done   |
Copying blob 042fa6758c75 done   |
Copying blob fc2658c9dba2 done   |
Copying blob 958bf1eb6fc6 done   |
Copying blob 4cfc38eabca1 done   |
Copying blob d89723805505 done   |
Copying blob ad148e16985f done   |
Copying blob 520bd83ae1b8 done   |
Copying blob 189922a4c16e done   |
Copying blob 96b05ad26199 done   |
Copying blob e6086166348b done   |
Copying blob af6f32190c41 done   |
Copying blob 92470b0bd930 done   |
Copying blob a8f30ebfaf56 done   |
Copying blob 96bdbb8504d9 done   |
Copying blob fc4f0bd70b37 done   |
Copying blob dadfd56d7667 done   |
Copying blob 7ada2fa1461c done   |
Copying config 44136fa355 done   |
Writing manifest to image destination
INFO 2025-03-18 13:31:22,577 instructlab.model.download:289:
ᕦ(òᴗóˇ)ᕤ docker://registry.redhat.io/rhelai1/prometheus-8x7b-v2-0 model download completed successfully! ᕦ(òᴗóˇ)ᕤ

INFO 2025-03-18 13:31:22,577 instructlab.model.download:303: Available models (`ilab model list`):
+----------------------------------+---------------------+---------+
| Model Name                       | Last Modified       | Size    |
+----------------------------------+---------------------+---------+
| models/granite-3.1-8b-starter-v1 | 2025-03-18 13:03:04 | 15.2 GB |
| models/granite-3.1-8b-lab-v1     | 2025-03-18 13:09:17 | 15.2 GB |
| models/prometheus-8x7b-v2-0      | 2025-03-18 13:31:22 | 87.0 GB |
+----------------------------------+---------------------+---------+

[instruct@bastion ~]$ ilab model download --repository docker://registry.redhat.io/rhelai1/mixtral-8x7b-instruct-v0-1 --release latest
INFO 2025-03-18 13:34:18,096 instructlab.model.download:193: Downloading model from OCI registry:
    Model: docker://registry.redhat.io/rhelai1/mixtral-8x7b-instruct-v0-1@latest
    Destination: /var/home/instruct/.cache/instructlab/models
Copying blob d0b63fca793c done   |
Copying blob 40e6ecbcedfc done   |
Copying blob 47324f06fdb5 done   |
Copying blob 54669c5aec29 done   |
Copying blob 29e15364d8ab done   |
Copying blob 9d56d04b36d0 done   |
Copying blob 67e0596920fe done   |
Copying blob e330eabd70b4 done   |
Copying blob 048fa5347877 done   |
Copying blob 83bfed6169c1 done   |
Copying blob af316ad78402 done   |
Copying blob 5882e4366c63 done   |
Copying blob 77813d1dbee6 done   |
Copying blob ff24540d9967 done   |
Copying blob 48bc12845676 done   |
Copying blob e56a2e7eda69 done   |
Copying blob da627f6a3c8f done   |
Copying blob 61e0f22bff93 done   |
Copying blob 76466bfc2312 done   |
Copying blob 570af3b802be done   |
Copying blob 4c603b65cbd5 done   |
Copying blob 272f33c76bca done   |
Copying blob a8f30ebfaf56 done   |
Copying blob 6fa06efa2785 done   |
Copying blob 11c08db21487 done   |
Copying blob dadfd56d7667 done   |
Copying blob 475361439e5c done   |
Copying config 44136fa355 done   |
Writing manifest to image destination
INFO 2025-03-18 13:44:39,848 instructlab.model.download:289:
ᕦ(òᴗóˇ)ᕤ docker://registry.redhat.io/rhelai1/mixtral-8x7b-instruct-v0-1 model download completed successfully! ᕦ(òᴗóˇ)ᕤ

INFO 2025-03-18 13:44:39,848 instructlab.model.download:303: Available models (`ilab model list`):
+-----------------------------------+---------------------+---------+
| Model Name                        | Last Modified       | Size    |
+-----------------------------------+---------------------+---------+
| models/granite-3.1-8b-starter-v1  | 2025-03-18 13:03:04 | 15.2 GB |
| models/granite-3.1-8b-lab-v1      | 2025-03-18 13:09:17 | 15.2 GB |
| models/prometheus-8x7b-v2-0       | 2025-03-18 13:31:22 | 87.0 GB |
| models/mixtral-8x7b-instruct-v0-1 | 2025-03-18 13:44:39 | 87.0 GB |
+-----------------------------------+---------------------+---------+

[instruct@bastion ~]$ tree -L 1 .cache/instructlab/models/
.cache/instructlab/models/
├── granite-3.1-8b-lab-v1
├── granite-3.1-8b-starter-v1
├── mixtral-8x7b-instruct-v0-1
└── prometheus-8x7b-v2-0

4 directories, 0 files



[instruct@bastion ~]$







