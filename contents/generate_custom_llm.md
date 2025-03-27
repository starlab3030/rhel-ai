# RHEL AI를 사용하여 커스텀 LLM 생성

1. [SDG로 새 데이터 세트 생성](generate_custom_llm.md#1-sdg로-새-데이터-세트-생성)<br>
2. [모델 학습](generate_custom_llm.md#2-모델-학습)<br>
3. [모델 평가](generate_custom_llm.md#3-모델-평가)<br>
4. [새 모델 제공 및 채팅](generate_custom_llm.md#4-새-모델-제공-및-채팅)<br>
5. [샘플 예제](generate_custom_llm.md#5-샘플-예제)<br>
&nbsp;&nbsp;5.1 [택소노미 트리](generate_custom_llm.md#51-택소노미-트리)<br>
&nbsp;&nbsp;5.2 [합성 데이터 생성](generate_custom_llm.md#52-샘플-예제-합성-데이터-생성)<br>
&nbsp;&nbsp;5.3 [Phase1 훈련](generate_custom_llm.md#53-phase1-훈련)<br>
&nbsp;&nbsp;5.4 [Phase2 훈련](generate_custom_llm.md#54-phase2-훈련)<br>
&nbsp;&nbsp;5.5 [모델 평가](generate_custom_llm.md#55-모델-평가)<br>
&nbsp;&nbsp;5.6 [모델 훈련 결과 확인](generate_custom_llm.md#56-모델-훈련-결과-확인)<br>
&nbsp;&nbsp;5.7 [새 모델 제공 및 채팅](generate_custom_llm.md#57-새-모델-제공-및-채팅)<br>
&nbsp;&nbsp;5.8 [모델 업로드](generate_custom_llm.md#58-모델-업로드)<br>
&nbsp;&nbsp;5.9 [모델 양자화](generate_custom_llm.md#59-모델-양자화)<br>
<br>
<br>

## 1. SDG로 새 데이터 세트 생성

택소노미 트리를 사용자 지정한 후 RHEL AI에서 SDG(Synthetic Data Generation) 프로세스를 사용하여 합성 데이터 세트를 생성할 수 있습니다.
* SDG는 제공된 예를 기반으로 실제 데이터를 모방하는 인공적으로 생성된 데이터 세트를 만드는 프로세스
* SDG는 질문과 답변 쌍을 포함하는 YAML 파일을 입력 데이터로 사용
* SDG는 *mixtral-8x7b-instruct-v0-1* LLM을 교사 모델로 사용하여 유사한 질문과 답변 쌍을 생성
* SDG 파이프라인에서 많은 질문이 품질에 따라 생성되고 점수가 매겨지며, *mixtral-8x7b-instruct-v0-1* 교사 모델은 질문의 관련성과 일관성을 평가
* 그런 다음 파이프라인은 필터링 메커니즘을 적용하여 가장 높은 점수를 받은 질문을 선택
  + 해당 답변을 생성한 다음 원래 예제 질문을 기반으로 정확도를 추가로 평가
  + 그런 다음 최종 고품질 질문과 답변 쌍 세트가 훈련에 사용되는 합성 데이터 세트에 포함

### 1.1 사전 준비 사항

* RHEL AI 노드 준비
* 지식 데이터를 가진 커스텀 *qna.yaml* 파일 생성
* 이미지 준비
  + SDG를 위한 교사 모델로 *mixtral-8x7b-instruct-v0-1* 다운로드
  + LoRA 계층화된 기술 및 지식 어댑터 용 이미지 다운로드
    - *skills-adapter-v3:1.4*
    - *knowledge-adapter-v3:1.4*
<br>

**InstructLab의 합성 데이터 모델 구성**
```bash
yq '.generate' .config/instructlab/config.yaml
```

실행 결과
```json
{
  "chunk_word_count": 1000,
  "max_num_tokens": 4096,
  "model": "/var/home/instruct/.cache/instructlab/models/mixtral-8x7b-instruct-v0-1",
  "num_cpus": 10,
  "num_instructions": -1,
  "output_dir": "/var/home/instruct/.local/share/instructlab/datasets",
  "pipeline": "/usr/share/instructlab/sdg/pipelines/agentic",
  "sdg_scale_factor": 30,
  "seed_file": "/var/home/instruct/.local/share/instructlab/internal/seed_tasks.json",
  "taxonomy_base": "empty",
  "taxonomy_path": "/var/home/instruct/.local/share/instructlab/taxonomy",
  "teacher": {
    "backend": "vllm",
    "chat_template": "tokenizer",
    "llama_cpp": {
      "gpu_layers": -1,
      "llm_family": "",
      "max_ctx_size": 4096
    },
    "model_path": "/var/home/instruct/.cache/instructlab/models/mixtral-8x7b-instruct-v0-1",
    "server": {
      "backend_type": "",
      "current_max_ctx_size": 4096,
      "host": "127.0.0.1",
      "port": 8000
    },
    "vllm": {
      "gpus": 4,
      "llm_family": "mixtral",
      "max_startup_attempts": 120,
      "vllm_args": [
        "--enable-lora",
        "--max-lora-rank",
        "64",
        "--dtype",
        "bfloat16",
        "--lora-dtype",
        "bfloat16",
        "--fully-sharded-loras",
        "--lora-modules",
        "skill-classifier-v3-clm=/var/home/instruct/.cache/instructlab/models/skills-adapter-v3",
        "text-classifier-knowledge-v3-clm=/var/home/instruct/.cache/instructlab/models/knowledge-adapter-v3"
      ]
    }
  }
}
```

### 1.2 예제를 사용하여 합성 데이터 세트를 생성

#### 1.2.1 합성 데이터 세트 생성

지식을 기반으로 사용자 정의 분류법을 기반으로 새로운 합성 데이터 세트를 생성
```bash
ilab data generate
```
* *--enable-serving-output*: vLLM 시작 로그를 표시

#### 1.2.2 vLLM 서버 시작

SDG 프로세스가 시작될 때 vLLM은 *mixtral-8x7B-instruct* 교사 모델을 호스팅하는 서버를 시작하려고 시도

예) vLLM이 서버를 시작 로그
```log
Starting a temporary vLLM server at http://127.0.0.1:47825/v1
INFO 2024-08-22 17:01:09,461 instructlab.model.backends.backends:480: Waiting for the vLLM server to start at http://127.0.0.1:47825/v1, this might take a moment... Attempt: 1/120
INFO 2024-08-22 17:01:14,213 instructlab.model.backends.backends:480: Waiting for the vLLM server to start at http://127.0.0.1:47825/v1, this might take a moment... Attempt: 2/120
```

#### 1.2.3 vLLM 서버 연결 및 SDG 생성

vLLM이 연결되면 SDG 프로세스는 *qna.yaml* 파일에 있는 시드 예제를 기반으로 합성 데이터를 생성하기 시작

예) vLLM 연결 및 SDG 생성 로그
```log
INFO 2024-08-22 15:16:43,497 instructlab.model.backends.backends:480: Waiting for the vLLM server to start at http://127.0.0.1:49311/v1, this might take a moment... Attempt: 74/120
INFO 2024-08-22 15:16:45,949 instructlab.model.backends.backends:487: vLLM engine successfully started at http://127.0.0.1:49311/v1
Generating synthetic data using '/usr/share/instructlab/sdg/pipelines/agentic' pipeline, '/var/home/cloud-user/.cache/instructlab/models/mixtral-8x7b-instruct-v0-1' model, '/var/home/cloud-user/.local/share/instructlab/taxonomy' taxonomy, against http://127.0.0.1:49311/v1 server
INFO 2024-08-22 15:16:46,594 instructlab.sdg:375: Synthesizing new instructions. If you aren't satisfied with the generated instructions, interrupt training (Ctrl-C) and try adjusting your YAML files. Adding more examples may help.
```

#### 1.2.4 CLI에 새 데이터 세트의 위치가 표시되면 SDG 프로세스가 완료

예) 성공적인 SDG 실행
```log
INFO 2024-08-16 17:12:46,548 instructlab.sdg.datamixing:200: Mixed Dataset saved to /home/example-user/.local/share/instructlab/datasets/skills_train_msgs_2024-08-16T16_50_11.jsonl
INFO 2024-08-16 17:12:46,549 instructlab.sdg:438: Generation took 1355.74s
```
 
> [!NOTE] 
> 하드웨어 사양에 따라 시간이 많이 걸릴 수 있습니다.
<br>

### 1.3 생성된 SDG 파일 검증

#### 1.3.1 생성된 파일 확인

*~/.local/share/instructlab/datasets/* 디렉토리로 이동하여 데이터가 생성된 날짜에 해당하는 파일을 나열

실행 명령어
```bash
ls 2024-03-24_194933
```

실행 결과
```
knowledge_recipe_2024-03-24T20_54_21.yaml                   skills_recipe_2024-03-24T20_54_21.yaml
knowledge_train_msgs_2024-03-24T20_54_21.jsonl              skills_train_msgs_2024-03-24T20_54_21.jsonl
messages_granite-7b-lab-Q4_K_M_2024-03-24T20_54_21.jsonl    node_datasets_2024-03-24T15_12_12/
```

> [!IMPORTANT]
> 가장 최근의 *knowledge_train_msgs.jsonl* 및 *skills_train_msgs.jsonl* 파일을 기록해 두세요. 다중 단계 훈련 중에 이 파일을 지정해야 합니다. 각 JSONL에는 파일에 타임스탬프가 있습니다. (예: knowledge_train_msgs_2024-08-08T20_04_28.jsonl). 훈련 시 가장 최근 파일을 사용하세요.

#### 1.3.2 (옵션) JSONL 파일을 열어 SDG 출력을 확인

*~/.local/share/datasets/\<generation-date\>* 디렉토리로 이동하고 JSONL 파일을 열어 SDG 출력을 확인

실행 명령어
```bash
cat ~/.local/share/datasets/<generation-date>/<jsonl-dataset>
```

실행 결과
```
{"messages":[{"content":"I am, Red Hat\u00ae Instruct Model based on Granite 7B, an AI language model developed by Red Hat and IBM Research, based on the Granite-7b-base language model. My primary function is to be a chat assistant.","role":"system"},{"content":"<|user|>\n### Deep-sky objects\n\nThe constellation does not lie on the [galactic\nplane](galactic_plane \"wikilink\") of the Milky Way, and there are no\nprominent star clusters. [NGC 625](NGC_625 \"wikilink\") is a dwarf\n[irregular galaxy](irregular_galaxy \"wikilink\") of apparent magnitude\n11.0 and lying some 12.7 million light years distant.
Only 24000 light\nyears in diameter, it is an outlying member of the [Sculptor\nGroup](Sculptor_Group \"wikilink\"). NGC 625 is thought to have been\ninvolved in a collision and is experiencing a burst of [active star\nformation](Active_galactic_nucleus \"wikilink\"). [NGC\n37](NGC_37 \"wikilink\") is a [lenticular\ngalaxy](lenticular_galaxy \"wikilink\") of apparent magnitude 14.66. It is\napproximately 42 [kiloparsecs](kiloparsecs \"wikilink\") (137,000\n[light-years](light-years \"wikilink\")) in diameter and about 12.9\nbillion years old. [Robert's Quartet](Robert's_Quartet \"wikilink\")\n(composed of the
irregular galaxy [NGC 87](NGC_87 \"wikilink\"), and three\nspiral galaxies [NGC 88](NGC_88 \"wikilink\"), [NGC 89](NGC_89 \"wikilink\")\nand [NGC 92](NGC_92 \"wikilink\")) is a group of four galaxies located\naround 160 million light-years away which are in the process of\ncolliding and merging. They are within a circle of radius of 1.6 arcmin,\ncorresponding to about 75,000 light-years. Located in the galaxy ESO\n243-49 is [HLX-1](HLX-1 \"wikilink\"), an [intermediate-mass black\nhole](intermediate-mass_black_hole \"wikilink\")\u2014the first one of its kind\nidentified. It is thought to be a remnant of a dwarf
galaxy that was\nabsorbed in a [collision](Interacting_galaxy \"wikilink\") with ESO\n243-49. Before its discovery, this class of black hole was only\nhypothesized.\n\nLying within the bounds of the constellation is the gigantic [Phoenix\ncluster](Phoenix_cluster \"wikilink\"), which is around 7.3 million light\nyears wide and 5.7 billion light years away, making it one of the most\nmassive [galaxy clusters](galaxy_cluster \"wikilink\"). It was first\ndiscovered in 2010, and the central galaxy is producing an estimated 740\nnew stars a year. Larger still is [El\nGordo](El_Gordo_(galaxy_cluster) \"wikilink\"),
or officially ACT-CL\nJ0102-4915, whose discovery was announced in 2012.
```
<br>

### 1.4 백그라운드에서 SDG(Synthetic Data Generation) 실행

#### 1.4.1 백그라운드에서 SDG 프로세스를 시작

실행 명령어
```bash
ilab data generate -dt
```

실행 결과
```log
INFO 2025-01-15 11:36:47,557 instructlab.process.process:236: Started subprocess with PID 68289. Logs are being written to /Users/<user-name>/.local/share/instructlab/logs/generation/generation-e85623ac-d35e-11ef-bc70-2a1c6126d703.log.
```

#### 1.4.2 분리된 SDG 프로세스를 관리, 보고, 상호 작용

실행 명령어 - 실행 중인 모든 프로세스 및 상태 확인
```bash
ilab process list
```

실행 결과
```
+------------+-------+--------------------------------------+----------------------------------------------------------------------------------------------------------------+----------+---------+
| Type       | PID   | UUID                                 | Log File                                                                                                       | Runtime  | Status  |
+------------+-------+--------------------------------------+----------------------------------------------------------------------------------------------------------------+----------+---------+
| Generation | 30334 | f2623406-de55-11ef-b684-2a1c6126d703 | /Users/<user-name>/.local/share/instructlab/logs/generation/generation-f2623406-de55-11ef-b684-2a1c6126d703.log| 00:08:30 | Running |
+------------+-------+--------------------------------------+----------------------------------------------------------------------------------------------------------------+----------+---------+
```

실행 명령어 - 가장 최신의 프로세스에 참여
```bash
ilab process attach --latest
```
* 한 번 *attach*하면 *dettach*할 수 없음
<br>
<br>

## 2. 모델 훈련

### 2.1 새로 학습된 모델

RHEL AI는 택소노미 트리와 합성 데이터를 사용하여 다중 단계 학습 및 평가를 통해 도메인별 지식 또는 기술로 새로 학습된 모델을 만들 수 있습니다.

* 생성한 합성 데이터 세트를 사용하여 전체 학습 및 평가 프로세스를 실행 가능
* 다중 단계 학습의 LAB 최적화 기술은 여러 단계의 학습 및 평가를 거치는 LLM 학습 유형
  + 다양한 단계에서 RHEL AI는 학습 프로세스를 실행하고 모델 체크포인트를 생성
  + 다음 단계에 가장 적합한 체크포인트를 선택
  + 이 프로세스는 여러 체크포인트를 생성하고 가장 높은 점수를 받은 체크포인트를 선택
  + 이 가장 높은 점수를 받은 체크포인트가 새로 학습된 LLM

전체 프로세스는 택소노미 트리의 합성 데이터를 사용하여 학습 및 평가되는 새로 생성된 모델을 생성합니다.

**InstructLab의 훈련 모델 구성**
```bash
yq '.train' .config/instructlab/config.yaml
```

실행 결과
```json
{
  "additional_args": {
    "learning_rate": 0.000006,
    "lora_alpha": 32,
    "lora_dropout": 0.1,
    "warmup_steps": 25,
    "use_dolomite": true
  },
  "checkpoint_at_epoch": true,
  "ckpt_output_dir": "/var/home/instruct/.local/share/instructlab/checkpoints",
  "data_output_dir": "/var/home/instruct/.local/share/instructlab/internal",
  "data_path": "/var/home/instruct/.local/share/instructlab/datasets",
  "deepspeed_cpu_offload_optimizer": false,
  "device": "cuda",
  "disable_flash_attn": false,
  "distributed_backend": "fsdp",
  "effective_batch_size": 128,
  "fsdp_cpu_offload_optimizer": false,
  "is_padding_free": false,
  "lora_quantize_dtype": null,
  "lora_rank": 0,
  "max_batch_len": 10000,
  "max_seq_len": 10000,
  "model_path": "/var/home/instruct/.cache/instructlab/models/granite-3.1-8b-starter-v1",
  "nproc_per_node": 4,
  "num_epochs": 4,
  "phased_base_dir": "/var/home/instruct/.local/share/instructlab/phased",
  "phased_mt_bench_judge": "/var/home/instruct/.cache/instructlab/models/prometheus-8x7b-v2-0",
  "phased_phase1_effective_batch_size": 128,
  "phased_phase1_learning_rate": 0.00002,
  "phased_phase1_num_epochs": 7,
  "phased_phase1_samples_per_save": 0,
  "phased_phase2_effective_batch_size": 3840,
  "phased_phase2_learning_rate": 0.000006,
  "phased_phase2_num_epochs": 10,
  "phased_phase2_samples_per_save": 0,
  "pipeline": "accelerated",
  "save_samples": 0,
  "training_journal": null
}
```
<br>

### 2.2 데이터로 모델 훈련하기

RHEL AI를 사용하여 합성적으로 생성된 데이터로 모델을 훈련할 수 있습니다. 

> [!IMPORTANT] 
> RHEL AI 일반 가용성은 동시에 학습과 추론 제공을 지원하지 않습니다. 추론 서버를 실행 중인 경우 학습 프로세스를 시작하기 전에 닫아야 합니다.


#### 2.2.1 사전 준비

* RHEL AI 노드
* *스타터* 모델인 *granite-3.1-8b-starter-v1* 이미지 다운로드
* 지식 데이터로 사용자 지정 *qna.yaml* 파일을 생성
* 합성 데이터 생성(SDG) 프로세스를 실행
* 판단 모델인 *prometheus-8x7b-v2-0* 이미지를 다운로드

#### 2.2.2 수행 절차

SDG에서 생성된 데이터 파일로 다음 명령을 실행하면 다단계 학습 및 평가를 실행할 수 있습니다.

실행 명령어
```bash
ilab model train --strategy lab-multiphase \
  --phased-phase1-data ~/.local/share/instructlab/datasets/<generation-date>/<knowledge-train-messages-jsonl-file> \
  --phased-phase2-data ~/.local/share/instructlab/datasets/<generation-date>/<skills-train-messages-jsonl-file>
```
* *ilab model train --enable-serving-output* 명령으로 학습 로그를 표시
* \<generation-date\>
  + 합성 데이터 생성(SDG)을 실행한 날짜
* \<knowledge-train-messages-file\>
  + Phase1은 지식 관련 훈련
  + SDG 중에 생성된 knowledge_messages.jsonl 파일의 위치
  + RHEL AI는 *.jsonl 파일의 데이터를 사용하여 학생 모델 *granite-3.1-8b-starter-v1*를 훈련
  + 경로 예
    ```
    ~/.local/share/instructlab/datasets/2024-09-07_194933/knowledge_train_msgs_2024-09-07T20_54_21.jsonl.
    ```
* \<skills-train-messages-file\>
  + Phase2는 기술 관련 훈련
  + SDG 중에 생성된 skills_messages.jsonl 파일의 위치
  + RHEL AI는 *.jsonl 파일의 데이터를 사용하여 학생 모델 *granite-3.1-8b-starter-v1*를 훈련
  + 경로 예
    ```
    ~/.local/share/instructlab/datasets/2024-09-07_194933/skills_train_msgs_2024-09-07T20_54_21.jsonl.
    ```

#### 2.2.3 기술에 대해서만 모델을 훈련하는 명령어

*--strategy lab-skills-only* 옵션으로 실행
```bash
ilab model train --strategy lab-skills-only --phased-phase2-data ~/.local/share/instructlab/datasets/<skills-train-messages-jsonl-file>
```
<br>

### 2.3 모델 훈련 예

#### 2.3.1 지식 기여를 통해 얻은 합성 데이터를 사용하여 모델을 훈련

지식 훈련의 출력 예
```log
Training Phase 1/2...
TrainingArgs for current phase: TrainingArgs(model_path='/opt/app-root/src/.cache/instructlab/models/granite-7b-starter', chat_tmpl_path='/opt/app-root/lib64/python3.11/site-packages/instructlab/training/chat_templates/ibm_generic_tmpl.py', data_path='/tmp/jul19-knowledge-26k.jsonl', ckpt_output_dir='/tmp/e2e/phase1/checkpoints', data_output_dir='/opt/app-root/src/.local/share/instructlab/internal', max_seq_len=4096, max_batch_len=55000, num_epochs=2, effective_batch_size=128, save_samples=0, learning_rate=2e-05, warmup_steps=25, is_padding_free=True, random_seed=42, checkpoint_at_epoch=True, mock_data=False, mock_data_len=0, deepspeed_options=DeepSpeedOptions(cpu_offload_optimizer=False, cpu_offload_optimizer_ratio=1.0, cpu_offload_optimizer_pin_memory=False, save_samples=None), disable_flash_attn=False, lora=LoraOptions(rank=0, alpha=32, dropout=0.1, target_modules=('q_proj', 'k_proj', 'v_proj', 'o_proj'), quantize_data_type=<QuantizeDataType.NONE: None>))
```

#### 2.3.2 RHEL AI는 다음 단계에 사용할 가장 적합한 체크포인트를 선택

#### 2.3.3 다음 단계에서는 기술 데이터의 합성 데이터를 사용하여 모델을 훈련

기술 훈련의 예
```log
Training Phase 2/2...
TrainingArgs for current phase: TrainingArgs(model_path='/tmp/e2e/phase1/checkpoints/hf_format/samples_52096', chat_tmpl_path='/opt/app-root/lib64/python3.11/site-packages/instructlab/training/chat_templates/ibm_generic_tmpl.py', data_path='/usr/share/instructlab/sdg/datasets/skills.jsonl', ckpt_output_dir='/tmp/e2e/phase2/checkpoints', data_output_dir='/opt/app-root/src/.local/share/instructlab/internal', max_seq_len=4096, max_batch_len=55000, num_epochs=2, effective_batch_size=3840, save_samples=0, learning_rate=2e-05, warmup_steps=25, is_padding_free=True, random_seed=42, checkpoint_at_epoch=True, mock_data=False, mock_data_len=0, deepspeed_options=DeepSpeedOptions(cpu_offload_optimizer=False, cpu_offload_optimizer_ratio=1.0, cpu_offload_optimizer_pin_memory=False, save_samples=None), disable_flash_attn=False, lora=LoraOptions(rank=0, alpha=32, dropout=0.1, target_modules=('q_proj', 'k_proj', 'v_proj', 'o_proj'), quantize_data_type=<QuantizeDataType.NONE: None>))
```

#### 2.3.4 2단계 모델 훈련의 체크포인트 평가 및 반환

RHEL AI는 Multi-turn Benchmark(MT-Bench)를 사용하여 2단계 모델 학습의 모든 체크포인트를 평가하고 완전히 학습된 출력 모델로 가장 성능이 좋은 체크포인트를 반환

기술 평가 출력의 예
```log
MT-Bench evaluation for Phase 2...
Using gpus from --gpus or evaluate config and ignoring --tensor-parallel-size configured in serve vllm_args
INFO 2024-08-15 10:04:51,065 instructlab.model.backends.backends:437: Trying to connect to model server at http://127.0.0.1:8000/v1
INFO 2024-08-15 10:04:53,580 instructlab.model.backends.vllm:208: vLLM starting up on pid 79388 at http://127.0.0.1:54265/v1
INFO 2024-08-15 10:04:53,580 instructlab.model.backends.backends:450: Starting a temporary vLLM server at http://127.0.0.1:54265/v1
INFO 2024-08-15 10:04:53,580 instructlab.model.backends.backends:465: Waiting for the vLLM server to start at http://127.0.0.1:54265/v1, this might take a moment... Attempt: 1/300
INFO 2024-08-15 10:04:58,003 instructlab.model.backends.backends:465: Waiting for the vLLM server to start at http://127.0.0.1:54265/v1, this might take a moment... Attempt: 2/300
INFO 2024-08-15 10:05:02,314 instructlab.model.backends.backends:465: Waiting for the vLLM server to start at http://127.0.0.1:54265/v1, this might take a moment... Attempt: 3/300
moment... Attempt: 3/300
INFO 2024-08-15 10:06:07,611 instructlab.model.backends.backends:472: vLLM engine successfully started at http://127.0.0.1:54265/v1
```

#### 2.3.5 훈련이 완료되면 확인 메시지가 나타나고 가장 잘 수행된 체크포인트가 표시

완전한 다단계 훈련 실행의 출력 예
```log
Training finished! Best final checkpoint: samples_1945 with score: 6.813759384
```
* 평가 및 제공에 이 경로가 필요하므로 이 체크포인트를 기록 필요
<br>

### 2.4 검증

#### 2.4.1 훈련된 데이터 포인트

* *ilab model train*으로 모델을 훈련할 때, 여러 개의 체크포인트는 훈련된 데이터 포인트 수에 따라 samples_ 접두사로 저장
* *~/.local/share/instructlab/phase/* 디렉토리에 저장 됨

#### 2.4.2 실행 예

실행 명령어
```bash
ls ~/.local/share/instructlab/phase/<phase1-or-phase2>/checkpoints/
```

실행 결과 - 새로운 모델의 출력 예
```log
samples_1711 samples_1945 samples_1456 samples_1462 samples_1903
```
<br>

### 2.5 훈련 재시작 혹은 이어하기

RHEL AI를 사용하면 다중 단계 훈련 중에 실패했을 수 있는 훈련 실행을 계속할 수 있습니다.

**훈련 실행이 실패하는 경우**
* vLLM 서버가 올바르게 시작되지 않음
* 가속기 또는 GPU가 정지되어 훈련이 중단
* ***InstructLab***의 *config.yaml* 파일에 오류

처음으로 다중 단계 훈련을 실행하면 초기 훈련 데이터가 *journalfile.yaml* 파일에 저장됩니다.
* 필요한 경우 파일의 이 메타데이터를 사용하여 실패한 훈련을 다시 시작 가능
* 다중 단계 훈련을 실행할 때 CLI 프롬프트에 따라 훈련 데이터를 지우는 훈련 실행을 다시 시작 가능

#### 2.5.1 다단계 훈련 명령을 다시 실행

```bash
ilab model train --strategy lab-multiphase \
    --phased-phase1-data ~/.local/share/instructlab/datasets/<generation-date>/<knowledge-train-messages-jsonl-file> \
    --phased-phase2-data ~/.local/share/instructlab/datasets/<generation-date>/<skills-train-messages-jsonl-file>
```
* RHEL AI CLI는 *journalfile.yaml* 파일이 있는지 읽고 해당 지점에서 학습 실행을 계속

#### 2.5.2 교육 실행을 계속할지 아니면 처음부터 시작할지 선택

* ***n***을 입력하여, 미리보기 학습 실행을 계속
  ```
  Metadata (checkpoints, the training journal) may have been saved from a previous training run.
  By default, training will resume from this metadata if it exists
  Alternatively, the metadata can be cleared, and training can start from scratch
  Would you like to START TRAINING FROM THE BEGINNING? n
  ```

* ***y***를 입력하여, 훈련 실행을 다시 시작
  ```
  Metadata (checkpoints, the training journal) may have been saved from a previous training run.
  By default, training will resume from this metadata if it exists
  Alternatively, the metadata can be cleared, and training can start from scratch
  Would you like to START TRAINING FROM THE BEGINNING? y
  ```
* 재시작하면 이전 검사점, 저널 파일 및 기타 교육 데이터의 시스템 캐시도 지워짐
<br>
<br>

## 3. 모델 평가

새 모델의 개선 사항을 측정하려면 평가 프로세스를 통해 기본 모델과 성능을 비교할 수 있습니다.
* 모델과 직접 채팅하여 새 모델이 새로 만든 지식을 학습했는지 정성적으로 확인 가능
* 모델 개선 사항에 대한 정량적 결과를 더 원하면 RHEL AI CLI에서 평가 프로세스를 실행 가능

**InstructLab의 모델 평가 구성**
```bash
yq '.evaluate' .config/instructlab/config.yaml
```

실행 결과
```json
{
  "base_branch": null,
  "base_model": "/var/home/instruct/.cache/instructlab/models/granite-3.1-8b-starter-v1",
  "branch": null,
  "dk_bench": {
    "input_questions": null,
    "judge_model": "gpt-4o",
    "output_dir": "/var/home/instruct/.local/share/instructlab/internal/eval_data/dk_bench",
    "output_file_formats": "jsonl"
  },
  "gpus": 4,
  "mmlu": {
    "batch_size": "auto",
    "few_shots": 5
  },
  "mmlu_branch": {
    "tasks_dir": "/var/home/instruct/.local/share/instructlab/datasets"
  },
  "model": null,
  "mt_bench": {
    "judge_model": "/var/home/instruct/.cache/instructlab/models/prometheus-8x7b-v2-0",
    "max_workers": "auto",
    "output_dir": "/var/home/instruct/.local/share/instructlab/internal/eval_data/mt_bench"
  },
  "mt_bench_branch": {
    "judge_model": "/var/home/instruct/.cache/instructlab/models/prometheus-8x7b-v2-0",
    "output_dir": "/var/home/instruct/.local/share/instructlab/internal/eval_data/mt_bench_branch",
    "taxonomy_path": "/var/home/instruct/.local/share/instructlab/taxonomy"
  },
  "system_prompt": null,
  "temperature": 0.0
}
```

### 3.1 새 모델 평가

#### 3.1.1 *qna.yaml* 파일을 생성한 작업 git 브랜치로 이동

#### 3.1.2 벤치마크에서 평가 프로세스를 실행

각 명령에는 평가할 훈련된 `samples` 모델에 대한 경로가 필요하며, `~/.local/share/instructlab/checkpoints` 폴더에서 이러한 체크포인트에 액세스할 수 있습니다.

**MMLU_BRANCH** 벤치마크
* 귀하의 지식 기여가 모델에 어떤 영향을 미쳤는지 측정하려면 다음 명령을 실행하여 mmlu_branch 벤치마크를 실행
  ```bash
  ilab model evaluate --benchmark mmlu_branch
      --model ~/.local/share/instructlab/phased/phase2/checkpoints/hf_format/<checkpoint> \
      --tasks-dir ~/.local/share/instructlab/datasets/<generation-date>/<node-dataset> \
      --base-model ~/.cache/instructlab/models/granite-7b-starter
  ```
  + \<checkpoint\>: 다중 단계 훈련 중 생성된 최고 점수의 체크포인트 파일을 지정
  + \<node-dataset\>
     - ~/.local/share/instructlab/datasets/\<generation-date\> 디렉토리에 SDG 동안 생성된 node_datasets 디렉토리를 지정
     - 모드 학습에 사용된 *.jsonl 파일과 동일한 타임스탬프를 지정

* 실행 결과 예
  ```
  # KNOWLEDGE EVALUATION REPORT
  
  ## BASE MODEL (SCORE)
  /home/user/.cache/instructlab/models/instructlab/granite-7b-lab/ (0.74/1.0)
  
  ## MODEL (SCORE)
  /home/user/local/share/instructlab/phased/phases2/checkpoints/hf_format/samples_665(0.78/1.0)
  
  ### IMPROVEMENTS (0.0 to 1.0):
  1. tonsils: 0.74 -> 0.78 (+0.04)
  ```

**MT_BENCH_BRANCH** 벤치마크
* 기술 기여가 모델에 어떤 영향을 미쳤는지 측정하려면 다음 명령을 실행
  ```bash
  ilab model evaluate \
      --benchmark mt_bench_branch \
      --model ~/.local/share/instructlab/phased/phase2/checkpoints/hf_format/<checkpoint> \
      --judge-model ~/.cache/instructlab/models/prometheus-8x7b-v2-0 \
      --branch <worker-branch> \
      --base-branch <worker-branch>
  ```
  + \<checkpoint\>: 여러 단계로 구성된 훈련 중 생성된 가장 높은 점수를 받은 체크포인트 파일을 지정
  + \<worker-branch\>: 택소노미 트리에 데이터를 추가할 때 사용한 분기를 지정
  + \<num-gpus\>: 평가에 사용할 GPU 수를 지정
* 실행 결과 예
  ```
  # SKILL EVALUATION REPORT
  
  ## BASE MODEL (SCORE)
  /home/user/.cache/instructlab/models/instructlab/granite-7b-lab (5.78/10.0)
  
  ## MODEL (SCORE)
  /home/user/local/share/instructlab/phased/phases2/checkpoints/hf_format/samples_665(6.00/10.0)
  
  ### IMPROVEMENTS (0.0 to 10.0):
  1. foundational_skills/reasoning/linguistics_reasoning/object_identification/qna.yaml: 4.0 -> 6.67 (+2.67)
  2. foundational_skills/reasoning/theory_of_mind/qna.yaml: 3.12 -> 4.0 (+0.88)
  3. foundational_skills/reasoning/linguistics_reasoning/logical_sequence_of_words/qna.yaml: 9.33 -> 10.0 (+0.67)
  4. foundational_skills/reasoning/logical_reasoning/tabular/qna.yaml: 5.67 -> 6.33 (+0.67)
  5. foundational_skills/reasoning/common_sense_reasoning/qna.yaml: 1.67 -> 2.33 (+0.67)
  6. foundational_skills/reasoning/logical_reasoning/causal/qna.yaml: 5.67 -> 6.0 (+0.33)
  7. foundational_skills/reasoning/logical_reasoning/general/qna.yaml: 6.6 -> 6.8 (+0.2)
  8. compositional_skills/writing/grounded/editing/content/qna.yaml: 6.8 -> 7.0 (+0.2)
  9. compositional_skills/general/synonyms/qna.yaml: 4.5 -> 4.67 (+0.17)
  
  ### REGRESSIONS (0.0 to 10.0):
  1. foundational_skills/reasoning/unconventional_reasoning/lower_score_wins/qna.yaml: 5.67 -> 4.0 (-1.67)
  2. foundational_skills/reasoning/mathematical_reasoning/qna.yaml: 7.33 -> 6.0 (-1.33)
  3. foundational_skills/reasoning/temporal_reasoning/qna.yaml: 5.67 -> 4.67 (-1.0)
  
  ### NO CHANGE (0.0 to 10.0):
  1. foundational_skills/reasoning/linguistics_reasoning/odd_one_out/qna.yaml (9.33)
  2. compositional_skills/grounded/linguistics/inclusion/qna.yaml (6.5)
  ```


#### 3.1.3 (옵션) 수동 평가

MMLU 및 MT_BENCH 벤치마크를 사용하여 각 체크포인트를 수동으로 평가할 수 있습니다.
* 표준화된 지식 또는 기술 집합에 대해 모든 모델을 평가하여 다른 LLM과 자신의 모델의 점수를 비교

**MMLU**
* 표준화된 지식 데이터 집합에 대한 새 모델의 평가 점수를 확인하려면 다음 명령을 실행하여 mmlu 벤치마크를 설정
  ```bash
  ilab model evaluate --benchmark mmlu --model ~/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_665
  ```
  + \<checkpoint\>: 다단계 학습 중 생성된 체크포인트 파일 중 하나를 지정
* 실행 결과 예
  ```
  # KNOWLEDGE EVALUATION REPORT
  
  ## MODEL (SCORE)
  /home/user/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_665
  
  ### SCORES (0.0 to 1.0):
  mmlu_abstract_algebra - 0.31
  mmlu_anatomy - 0.46
  mmlu_astronomy - 0.52
  mmlu_business_ethics - 0.55
  mmlu_clinical_knowledge - 0.57
  mmlu_college_biology - 0.56
  mmlu_college_chemistry - 0.38
  mmlu_college_computer_science - 0.46
  ...
  ```

> [!NOTE]
> **MMLU (Massive Multitask Language Understanding)**<br>
> <br>
> 인공지능 모델이 획득한 지식을 측정하는 벤치하크로, 약 57개의 주제에 대해 다지선다 문제를 푸는 테스트 입니다. 특히 zero-shot 환경이나 few-shot 환경에 맞게 되어 있습니다.

**MT_BENCH**
* 표준화된 기술 세트와 비교하여 새 모델의 평가 점수를 확인하려면 다음 명령을 실행하여 mt_bench 벤치마크를 설정
  ```bash
  ilab model evaluate --benchmark mt_bench --model ~/.local/share/instructlab/phased/phases2/checkpoints/hf_format/samples_665
  ```
  + \<checkpoint\>: 다단계 학습 중 생성된 체크포인트 파일 중 하나를 지정
* 실행 결과 예
  ```
  # SKILL EVALUATION REPORT
  
  ## MODEL (SCORE)
  /home/user/local/share/instructlab/phased/phases2/checkpoints/hf_format/samples_665(7.27/10.0)
  
  ### TURN ONE (0.0 to 10.0):
  7.48
  
  ### TURN TWO (0.0 to 10.0):
  7.05
  ```

> [!NOTE]
> **MT-Bench (Multi-turn Benchmark)**<br>
> <br>
> 언어 모델이 얼마나 잘 대화할 수 있는지 평가하기 위한 프레임워크입니다. 다양한 모델의 성능을 비교하고 강점과 약점을 파악하는 데 사용됩니다.
<br>

### 3.2 도메인 지식 벤치마크 평가

RHEL AI, MMLU 및 MMLU_branch의 현재 지식 평가 벤치마크는 다중 선택형 질문에 답하는 능력에 따라 모델을 평가합니다.
* 도메인 지식 벤치마크(Domain Knowledge Benchmark: DK-bench) 평가는 사용자 지정 평가 질문을 제공하고 모델 답변을 척도에 따라 평가할 수 있는 기능을 제공
* 제공된 각 답변은 참조 답변과 비교되고 심사 모델이 다음 척도에 따라 등급을 매김

**도메인 지식 벤치마크 루브릭**
|$\color{lime}{\texttt{점수}}$|$\color{lime}{\texttt{기준}}$|
|:--:|:---|
|1|응답은 전혀 틀렸거나, 관련성이 없거나, 어떤 의미 있는 방식으로든 참조 내용과 일치하지 않음|
|2|응답은 참조 내용과 부분적으로 일치하지만, 중대한 오류, 중요한 누락 또는 관련 없는 정보가 포함되어 있음|
|3|응답은 전반적인 참고 자료와 일치하지만 충분한 세부 정보나 명확성이 부족하거나 사소한 부정확성을 포함하고 있음|
|4|응답은 대체로 정확하고, 참고 자료와 긴밀하게 일치하며, 사소한 문제점이나 누락만 포함되어 있음|
|5|답변은 완벽히 정확하고, 참고문헌과 완벽히 일치하며, 명확하고, 철저하고, 상세함|
<br>

### 3.3 수행 절차

#### 3.3.1 평가 질문 파일 생성

사용자 정의 평가를 활용하려면 모델에 답하고 평가할 모든 질문을 포함하는 jsonl 파일을 만들어야 합니다.

예) DK-bench를 위한 `jsonl` 파일
```
{"user_input":"What is the capital of Canada?","reference":"The capital of Canada is Ottawa."}
```
* user_input: 모델에 대한 질문이 포함
* reference: 질문에 대한 답변이 포함

#### 3.3.2 평가를 위한 벤치마크 실행

사용자 정의 평가 질문으로 DK-bench 벤치마크를 실행
```bash
ilab model evaluate --benchmark dk_bench --input-questions /home/use/path/to/questions.jsonl --model ~/.cache/instructlab/models/instructlab/granite-7b-lab
```
* \<path-to-jsonl-file\>: 질문과 답변이 포함된 jsonl 파일의 경로를 지정
* \<path-to-model\>: 평가하려는 모델의 경로를 지정

실행 명령어
```bash
ilab model evaluate --benchmark dk_bench --input-questions /home/use/path/to/questions.jsonl --model ~/.cache/instructlab/models/instructlab/granite-7b-lab
```

실행 결과
```
# DK-BENCH REPORT

## MODEL: granite-7b-lab

Question #1:     5/5
Question #2:     5/5
Question #3:     5/5
Question #4:     5/5
Question #5:     2/5
Question #6:     3/5
Question #7:     2/5
Question #8:     3/5
Question #9:     5/5
Question #10:     5/5
----------------------------
Average Score:   4.00/5
Total Score:     40/50
```
<br>

### 3.4 한국어 평가 사례

다양한 인공지능 모델이 계속해서 나오고 있지만, 대부분이 영어를 기반으로 하고 있으며, 모델에 대한 평가도 영어(데이터 세트)로 수행되어 결과가 발표되고 있습니다.

한국어를 기반으로 모델을 훈련하고 이를 평가하는 방안에 대한 얘기가 국내에서 이루어지고 있으며, 다음은 이를 위해 모델을 평가하는 방안 및 결과에 대한 사례 입니다.

|$\color{lime}{\texttt{벤치마크}}$|$\color{lime}{\texttt{참조}}$|
|:---|:---|
|CLIcK (Cultural and Linguistic Intelligence in Korean)|[깃허브](https://github.com/rladmstn1714/CLIcK)<br>[논문](https://arxiv.org/abs/2403.06412)<br>[허깅페이스](https://huggingface.co/datasets/EunsuKim/CLIcK)|
|HAE_RAE_BENCH 1.0|[깃허브](https://github.com/HAE-RAE/HAE-RAE-BENCH)<br>[논문](https://arxiv.org/abs/2309.02706)<br>[허깅페이스](https://huggingface.co/datasets/HAERAE-HUB/HAE_RAE_BENCH_1.0)|
|KMMLU|<br>[논문](https://arxiv.org/abs/2402.11548)<br>[허깅페이스](https://huggingface.co/datasets/HAERAE-HUB/KMMLU)|
|KMMLU-HARD|<br>[논문](https://arxiv.org/abs/2402.11548)<br>[허깅페이스](https://huggingface.co/datasets/HAERAE-HUB/KMMLU-HARD)|

#### 3.4.1 CLIcK (Cultural and Linguistic Intelligence in Korean)

* 다음 과목 영역에서 한국어 능력을 평가
  + 한국 문화
    - 역사
    - 지리
    - 법률
    - 정치
    - 사회
    - 전통
    - 경제
    - 대중 문화
  + 한국어
    - 텍스트
    - 기능
    - 문법
* 11개 범주에 총 1,995개의 샘플 데이터
* 4개 또는 5개의 객관식 문제를 제시
* 질문에 따라 추가 맥락이 제공

#### 3.4.2 HAE_RAE_BENCH 1.0

* 다음 6가지 범주에서 한국어 능력을 평가
  + 일반 지식
  + 역사
  + 외래어
  + 희귀어
  + 독해 이해
  + 표준 명명법
* CLiCK과 유사하게, 이 과제는 객관식 문제를 푸는 것이지만, 추가 맥락은 없음
* 6가지 범주에 총 1,538개의 샘플 데이터

#### 3.4.3 KMMLU

* 한국어로 된 대규모 멀티태스크 언어 이해 평가 데이터 세트
* MMLU 데이터셋을 단순히 번역한 것이 아니라 한국어 텍스트에서 생성된 데이터로, 한국어에서 LLM/SLM이 얼마나 잘 작동하는지 평가
* STEM, 응용 과학, HUMSS, 기타 등 총 45개 카테고리와 4개 슈퍼 카테고리로 구성

#### 3.4.4 KMMLU-HARD

* KMMLU 데이터 세트의 확장 버전으로 더 어려운 질문이 포함
* 한국어 NLP 모델의 한계를 더욱 평가하도록 설계
* 특히 높은 수준의 이해 및 추론 기술이 필요한 질문이 포함

<br>
<br>

## 4. 새 모델 제공 및 채팅

모델을 제공함으로써 모델을 머신에 배포해야 합니다.
* 모델이 배포되고 모델을 상호 작용하고 채팅 가능

### 4.1 새로운 모델을 제공

새 모델과 상호 작용하려면 서빙을 통해 머신에서 모델을 활성화해야 합니다.

#### 4.1.1 모델과 채팅할 수 있는 vLLM 서버를 시작

```bash
ilab model serve --model-path <path-to-best-performed-checkpoint>
```
* \<path-to-best-performed-checkpoint\>
  + 훈련 후 빌드한 체크포인트의 전체 경로를 지정
  + 새 모델은 훈련 후 파일 경로가 표시된 가장 잘 수행된 체크포인트

#### 4.1.2 실행 예

실행 명령 예
```bash
ilab model serve --model-path ~/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_1945/
```

실행 결과 예
```log
$ ilab model serve --model-path ~/.local/share/instructlab/phased/phase2/checkpoints/hf_format/<checkpoint>
INFO 2024-03-02 02:21:11,352 lab.py:201 Using model /home/example-user/.local/share/instructlab/checkpoints/hf_format/checkpoint_1945 with -1 gpu-layers and 4096 max context size.
Starting server process
After application startup complete see http://127.0.0.1:8000/docs for API.
Press CTRL+C to shut down the server.
```
<br>

### 4.2 새로운 모델과의 채팅

#### 4.2.1 새로운 터미널 실행

하나의 터미널 창에서 모델을 제공하고 있으므로 모델과 채팅하려면 새 터미널 창을 열어야 합니다.

#### 4.2.2 새 모델과 채팅하려면 다음 명령을 실행

명령어 형식
```bash
ilab model chat --model <path-to-best-performed-checkpoint-file>
```
* \<path-to-best-performed-checkpoint-file\>
  + 훈련 후 빌드한 새 모델 체크포인트 파일을 지정
  + 새 모델은 훈련 후 파일 경로가 표시된 가장 잘 수행된 체크포인트

실행 예
```bash
$ ilab model chat --model ~/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_1945
```

#### 4.2.3 InstructLab 챗봇의 출력 예

```
$ ilab model chat
╭────────────────────────────────────────────────────────────────────────────────────────────────────────────────── system ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Welcome to InstructLab Chat w/ CHECKPOINT_1945 (type /h for help)                                                                                                                                                                    │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
>>>                                                                                                                                                                                                                        [S][default]
```
<br>

### 4.3 훈련된 모델 업로드 

실행 명령어
```bash
ilab model upload --model <name-of-model> --destination <registry-location> --dest-type <registry-type>
```
* \<name-of-model\>
  + 업로드 할 체크포인트 이름
  + 체크포인트 경로 지정 가능
* \<registry-location\>
  + 모델 업로드 위치
* \<registry-type\>
  + 모델 형식 지정
  + 현재 `s3` 지원

예 - s3 버킷에 업로드
```
ilab model upload --model samples_0801 --destination example-s3-bucket --dest-type s3
```
<br>
<br>

## 5. 샘플 예제

홈 디렉터리 구성
```bash
export ILAB_HOME=~/.local/share/instructlab
ln -s $ILAB_HOME ./instructlab
ln -s $ILAB_HOME/taxonomy ./taxonomy
ln -s $ILAB_HOME/datasets ./datasets
ln -s $ILAB_HOME/logs ./logs
ln -s $ILAB_HOME/phased ./phased
```

### 5.1 택소노미 트리

#### 5.1.1 지식 파일 확인

실행 명령어
```bash
cd ~/taxonomy
find knowledge/ -name qna.yaml
```

실행 결과
```
[root@rhel_ai taxonomy]# find knowledge/ -name qna.yaml
knowledge/arts/music/fandom/swifties/qna.yaml
knowledge/science/animals/birds/black_capped_chickadee/qna.yaml
knowledge/science/astronomy/constellations/phoenix/qna.yaml
knowledge/science/astronomy/constellations/phoenix_eng/qna.yaml

[root@rhel_ai taxonomy]#
```

#### 5.1.2 지식 파일 내 Markdown 문서 확인

실행 명령어
```bash
for yaml in $(find knowledge/ -name qna.yaml); do echo $yaml; grep md $yaml; done
```

실행 결과
```log
[root@rhelai-02 taxonomy]# for yaml in $(find knowledge/ -name qna.yaml); do echo $yaml; grep md $yaml; done
knowledge/arts/music/fandom/swifties/qna.yaml
    - swifties.md
knowledge/science/animals/birds/black_capped_chickadee/qna.yaml
    - chickadee.md
knowledge/science/astronomy/constellations/phoenix/qna.yaml
    - phoenix_constellation.md
knowledge/science/astronomy/constellations/phoenix_eng/qna.yaml
    - phoenix.md

[root@rhelai-02 taxonomy]# 
```

#### 5.1.3 기술 파일 확인

실행 명령어
```bash
find foundational_skills/ -name qna.yaml
find compositional_skills/ -name qna.yaml
```

실행 결과
```
[root@rhel_ai taxonomy]# find foundational_skills/ -name qna.yaml
foundational_skills/reasoning/common_sense_reasoning/qna.yaml
foundational_skills/reasoning/linguistics_reasoning/logical_sequence_of_words/qna.yaml
foundational_skills/reasoning/linguistics_reasoning/object_identification/qna.yaml
foundational_skills/reasoning/linguistics_reasoning/odd_one_out/qna.yaml
foundational_skills/reasoning/logical_reasoning/causal/qna.yaml
foundational_skills/reasoning/logical_reasoning/general/qna.yaml
foundational_skills/reasoning/logical_reasoning/tabular/qna.yaml
foundational_skills/reasoning/mathematical_reasoning/qna.yaml
foundational_skills/reasoning/temporal_reasoning/qna.yaml
foundational_skills/reasoning/theory_of_mind/qna.yaml
foundational_skills/reasoning/unconventional_reasoning/lower_score_wins/qna.yaml

[root@rhel_ai taxonomy]# find compositional_skills/ -name qna.yaml
compositional_skills/grounded/linguistics/inclusion/qna.yaml
compositional_skills/grounded/linguistics/writing/rewriting/qna.yaml
compositional_skills/linguistics/synonyms/qna.yaml

[root@rhel_ai taxonomy]# 
```
<br>

### 5.2 샘플 예제 합성 데이터 생성

#### 5.2.1 합성 데이터 생성 로그 리스트

실행 명령어
```bash
ls -lht ~/logs/generation/
```

실행 결과
```log
[root@rhel_ai ~]# ls -lh ~/logs/generation/
total 14M
-rw-r--r--. 1 root root 5.9M Mar 25 07:41 generation-3b987c54-093d-11f0-b522-5254007e4ee5.log <<<<<
-rw-r--r--. 1 root root  30K Mar 25 05:43 generation-8154407c-093b-11f0-b39a-5254007e4ee5.log
-rw-r--r--. 1 root root 7.9M Mar 25 05:30 generation-6aad0984-0928-11f0-a4a5-5254007e4ee5.log

[root@rhel_ai ~]#
```

#### 5.2.2 최신 로그 파일 확인

실행 명령어
```bash
less ~/logs/generation/generation-3b987c54-093d-11f0-b522-5254007e4ee5.log
```

실행 결과
```log
[root@rhel_ai ~]# less ~/logs/generation/generation-3b987c54-093d-11f0-b522-5254007e4ee5.log
INFO 2025-03-25 05:51:45,286 instructlab.model.backends.vllm:115: Trying to connect to model server at http://127.0.0.1:8000/v1
INFO 2025-03-25 05:51:46,565 instructlab.model.backends.vllm:332: vLLM starting up on pid 77 at http://127.0.0.1:41749/v1
INFO 2025-03-25 05:51:46,565 instructlab.model.backends.vllm:123: Starting a temporary vLLM server at http://127.0.0.1:41749/v1

...<snip>...

INFO 2025-03-25 05:53:29,383 instructlab.model.backends.vllm:145: vLLM engine successfully started at http://127.0.0.1:41749/v1
INFO 2025-03-25 05:53:31,366 instructlab:206: Generating synthetic data using '/usr/share/instructlab/sdg/pipelines/agentic' pipeline, '/root/.cache/instructlab/models/mixtral-8x7b-instruct-v0-1' model, '/root/.local/share/instructlab/taxonomy' taxonomy, against http://127.0.0.1:41749/v1 server
INFO 2025-03-25 05:53:32,693 instructlab.sdg.utils.taxonomy:160: Processing files...
INFO 2025-03-25 05:53:32,693 instructlab.sdg.utils.taxonomy:166: Pattern 'swifties.md' matched 1 files.
INFO 2025-03-25 05:53:32,693 instructlab.sdg.utils.taxonomy:170: Processing file: /root/.local/share/instructlab/datasets/2025-03-25_055144/preprocessed_2025-03-25T05_53_31/documents/knowledge_arts_music_fandom_swifties_ej6u86bu/swifties.md
INFO 2025-03-25 05:53:32,694 instructlab.sdg.utils.taxonomy:184: Appended Markdown content from /root/.local/share/instructlab/datasets/2025-03-25_055144/preprocessed_2025-03-25T05_53_31/documents/knowledge_arts_music_fandom_swifties_ej6u86bu/swifties.md
INFO 2025-03-25 05:53:33,746 instructlab.sdg.utils.taxonomy:160: Processing files...
INFO 2025-03-25 05:53:33,746 instructlab.sdg.utils.taxonomy:166: Pattern 'chickadee.md' matched 1 files.
INFO 2025-03-25 05:53:33,746 instructlab.sdg.utils.taxonomy:170: Processing file: /root/.local/share/instructlab/datasets/2025-03-25_055144/preprocessed_2025-03-25T05_53_31/documents/knowledge_science_animals_birds_black_capped_chickadee_40xwivz6/chickadee.md
INFO 2025-03-25 05:53:33,746 instructlab.sdg.utils.taxonomy:184: Appended Markdown content from /root/.local/share/instructlab/datasets/2025-03-25_055144/preprocessed_2025-03-25T05_53_31/documents/knowledge_science_animals_birds_black_capped_chickadee_40xwivz6/chickadee.md
INFO 2025-03-25 05:53:34,643 instructlab.sdg.utils.taxonomy:160: Processing files...
INFO 2025-03-25 05:53:34,643 instructlab.sdg.utils.taxonomy:166: Pattern 'phoenix_constellation.md' matched 1 files.
INFO 2025-03-25 05:53:34,643 instructlab.sdg.utils.taxonomy:170: Processing file: /root/.local/share/instructlab/datasets/2025-03-25_055144/preprocessed_2025-03-25T05_53_31/documents/knowledge_science_astronomy_constellations_phoenix__n63d5jo/phoenix_constellation.md
INFO 2025-03-25 05:53:34,643 instructlab.sdg.utils.taxonomy:184: Appended Markdown content from /root/.local/share/instructlab/datasets/2025-03-25_055144/preprocessed_2025-03-25T05_53_31/documents/knowledge_science_astronomy_constellations_phoenix__n63d5jo/phoenix_constellation.md
INFO 2025-03-25 05:53:35,510 instructlab.sdg.utils.taxonomy:160: Processing files...
INFO 2025-03-25 05:53:35,510 instructlab.sdg.utils.taxonomy:166: Pattern 'phoenix.md' matched 1 files.
INFO 2025-03-25 05:53:35,510 instructlab.sdg.utils.taxonomy:170: Processing file: /root/.local/share/instructlab/datasets/2025-03-25_055144/preprocessed_2025-03-25T05_53_31/documents/knowledge_science_astronomy_constellations_phoenix_eng_ix6mqmov/phoenix.md
INFO 2025-03-25 05:53:35,510 instructlab.sdg.utils.taxonomy:184: Appended Markdown content from /root/.local/share/instructlab/datasets/2025-03-25_055144/preprocessed_2025-03-25T05_53_31/documents/knowledge_science_astronomy_constellations_phoenix_eng_ix6mqmov/phoenix.md
INFO 2025-03-25 05:53:38,178 instructlab.sdg.utils.chunkers:123: Found the docling models
INFO 2025-03-25 05:53:39,153 instructlab.sdg.utils.chunkers:271: Successfully loaded tokenizer from: /root/.cache/instructlab/models/mixtral-8x7b-instruct-v0-1
INFO 2025-03-25 05:53:39,344 instructlab.sdg.utils.chunkers:534: Processed 1 docs, of which 0 failed
INFO 2025-03-25 05:53:39,345 instructlab.sdg.utils.chunkers:184: Processing parsed docling json file: /root/.local/share/instructlab/datasets/2025-03-25_055144/preprocessed_2025-03-25T05_53_31/documents/docling-artifacts/swifties.json
INFO 2025-03-25 05:53:39,499 instructlab.sdg.utils.chunkers:123: Found the docling models
INFO 2025-03-25 05:53:39,656 instructlab.sdg.utils.chunkers:271: Successfully loaded tokenizer from: /root/.cache/instructlab/models/mixtral-8x7b-instruct-v0-1
INFO 2025-03-25 05:53:40,121 instructlab.sdg.utils.chunkers:534: Processed 1 docs, of which 0 failed
INFO 2025-03-25 05:53:40,121 instructlab.sdg.utils.chunkers:184: Processing parsed docling json file: /root/.local/share/instructlab/datasets/2025-03-25_055144/preprocessed_2025-03-25T05_53_31/documents/docling-artifacts/swifties.json
INFO 2025-03-25 05:53:40,243 instructlab.sdg.utils.chunkers:184: Processing parsed docling json file: /root/.local/share/instructlab/datasets/2025-03-25_055144/preprocessed_2025-03-25T05_53_31/documents/docling-artifacts/chickadee.json
INFO 2025-03-25 05:53:40,398 instructlab.sdg.utils.chunkers:123: Found the docling models
INFO 2025-03-25 05:53:40,557 instructlab.sdg.utils.chunkers:271: Successfully loaded tokenizer from: /root/.cache/instructlab/models/mixtral-8x7b-instruct-v0-1
INFO 2025-03-25 05:53:40,573 instructlab.sdg.utils.chunkers:534: Processed 1 docs, of which 0 failed
INFO 2025-03-25 05:53:40,573 instructlab.sdg.utils.chunkers:184: Processing parsed docling json file: /root/.local/share/instructlab/datasets/2025-03-25_055144/preprocessed_2025-03-25T05_53_31/documents/docling-artifacts/swifties.json
INFO 2025-03-25 05:53:40,695 instructlab.sdg.utils.chunkers:184: Processing parsed docling json file: /root/.local/share/instructlab/datasets/2025-03-25_055144/preprocessed_2025-03-25T05_53_31/documents/docling-artifacts/chickadee.json
INFO 2025-03-25 05:53:40,821 instructlab.sdg.utils.chunkers:184: Processing parsed docling json file: /root/.local/share/instructlab/datasets/2025-03-25_055144/preprocessed_2025-03-25T05_53_31/documents/docling-artifacts/phoenix_constellation.json
INFO 2025-03-25 05:53:40,857 instructlab.sdg.utils.chunkers:123: Found the docling models
INFO 2025-03-25 05:53:41,019 instructlab.sdg.utils.chunkers:271: Successfully loaded tokenizer from: /root/.cache/instructlab/models/mixtral-8x7b-instruct-v0-1
INFO 2025-03-25 05:53:41,264 instructlab.sdg.utils.chunkers:534: Processed 1 docs, of which 0 failed
INFO 2025-03-25 05:53:41,264 instructlab.sdg.utils.chunkers:184: Processing parsed docling json file: /root/.local/share/instructlab/datasets/2025-03-25_055144/preprocessed_2025-03-25T05_53_31/documents/docling
-artifacts/swifties.json
INFO 2025-03-25 05:53:41,385 instructlab.sdg.utils.chunkers:184: Processing parsed docling json file: /root/.local/share/instructlab/datasets/2025-03-25_055144/preprocessed_2025-03-25T05_53_31/documents/docling
-artifacts/chickadee.json
INFO 2025-03-25 05:53:41,512 instructlab.sdg.utils.chunkers:184: Processing parsed docling json file: /root/.local/share/instructlab/datasets/2025-03-25_055144/preprocessed_2025-03-25T05_53_31/documents/docling
-artifacts/phoenix_constellation.json
INFO 2025-03-25 05:53:41,515 instructlab.sdg.utils.chunkers:184: Processing parsed docling json file: /root/.local/share/instructlab/datasets/2025-03-25_055144/preprocessed_2025-03-25T05_53_31/documents/docling-artifacts/phoenix.json
INFO 2025-03-25 05:53:41,649 instructlab.sdg.generate_data:401: Taxonomy converted to samples and written to /root/.local/share/instructlab/datasets/2025-03-25_055144/preprocessed_2025-03-25T05_53_31
INFO 2025-03-25 05:53:41,668 instructlab.sdg.generate_data:437: Synthesizing new instructions. If you aren't satisfied with the generated instructions, interrupt training (Ctrl-C) and try adjusting your YAML files. Adding more examples may help.
^MGenerating train split: 0 examples [00:00, ? examples/s]^MGenerating train split: 14 examples [00:00, 557.36 examples/s]INFO 2025-03-25 05:53:42,455 instructlab.sdg.checkpointing:64: Loading existing checkpoints from /root/.local/share/instructlab/datasets/checkpoints/compositional_skills_grounded_linguistics_inclusion, with 14 rows
INFO 2025-03-25 05:53:42,465 instructlab.sdg.checkpointing:68: Found 0 missing rows in the dataset
INFO 2025-03-25 05:53:42,465 instructlab.sdg.pipeline:164: Running pipeline with multi-threaded batching. Using 32 workers for batches of size 8
INFO 2025-03-25 05:53:42,470 instructlab.sdg.generate_data:474: Generated 14 samples
INFO 2025-03-25 05:53:43,093 instructlab.sdg.checkpointing:64: Loading existing checkpoints from /root/.local/share/instructlab/datasets/checkpoints/compositional_skills_grounded_linguistics_writing_rewriting, with 9 rows
INFO 2025-03-25 05:53:43,100 instructlab.sdg.checkpointing:68: Found 0 missing rows in the dataset
INFO 2025-03-25 05:53:43,100 instructlab.sdg.pipeline:164: Running pipeline with multi-threaded batching. Using 32 workers for batches of size 8
INFO 2025-03-25 05:53:43,104 instructlab.sdg.generate_data:474: Generated 9 samples

^MGenerating train split: 0 examples [00:00, ? examples/s]^MGenerating train split: 57 examples [00:00, 7489.12 examples/s]INFO 2025-03-25 05:53:43,737 instructlab.sdg.checkpointing:64: Loading existing checkpoints from /root/.local/share/instructlab/datasets/checkpoints/compositional_skills_linguistics_synonyms, with 57 rows
INFO 2025-03-25 05:53:43,744 instructlab.sdg.checkpointing:68: Found 0 missing rows in the dataset
INFO 2025-03-25 05:53:43,744 instructlab.sdg.pipeline:164: Running pipeline with multi-threaded batching. Using 32 workers for batches of size 8
INFO 2025-03-25 05:53:43,753 instructlab.sdg.generate_data:474: Generated 57 samples
INFO 2025-03-25 05:53:44,395 instructlab.sdg.checkpointing:64: Loading existing checkpoints from /root/.local/share/instructlab/datasets/checkpoints/knowledge_arts_music_fandom_swifties, with 2189 rows
INFO 2025-03-25 05:53:44,416 instructlab.sdg.checkpointing:68: Found 31 missing rows in the dataset
INFO 2025-03-25 05:53:44,416 instructlab.sdg.pipeline:164: Running pipeline with multi-threaded batching. Using 32 workers for batches of size 8
INFO 2025-03-25 05:53:46,026 instructlab.sdg.blocks.llmblock:55: LLM server supports batched inputs: True
INFO 2025-03-25 05:53:46,026 instructlab.sdg.pipeline:202: Running block: router
INFO 2025-03-25 05:53:46,033 instructlab.sdg.blocks.llmblock:55: LLM server supports batched inputs: True
INFO 2025-03-25 05:53:46,033 instructlab.sdg.pipeline:202: Running block: router
INFO 2025-03-25 05:53:46,038 instructlab.sdg.blocks.llmblock:55: LLM server supports batched inputs: True
INFO 2025-03-25 05:53:46,038 instructlab.sdg.pipeline:202: Running block: router
INFO 2025-03-25 05:53:46,043 instructlab.sdg.blocks.llmblock:55: LLM server supports batched inputs: True
INFO 2025-03-25 05:53:46,043 instructlab.sdg.pipeline:202: Running block: router
INFO 2025-03-25 05:53:48,571 instructlab.sdg.pipeline:202: Running block: SetClassifierValue
INFO 2025-03-25 05:53:48,582 instructlab.sdg.pipeline:202: Running block: SetClassifierValue
INFO 2025-03-25 05:53:48,594 instructlab.sdg.pipeline:202: Running block: SetClassifierValue
INFO 2025-03-25 05:53:48,605 instructlab.sdg.pipeline:202: Running block: SetClassifierValue
INFO 2025-03-25 05:53:48,668 instructlab.sdg.pipeline:202: Running block: duplicate_document_col
INFO 2025-03-25 05:53:48,670 instructlab.sdg.pipeline:202: Running block: duplicate_document_col
INFO 2025-03-25 05:53:48,675 instructlab.sdg.pipeline:202: Running block: duplicate_document_col
INFO 2025-03-25 05:53:48,680 instructlab.sdg.pipeline:202: Running block: duplicate_document_col
INFO 2025-03-25 05:53:48,707 instructlab.sdg.pipeline:202: Running block: gen_detailed_summary
INFO 2025-03-25 05:53:48,722 instructlab.sdg.pipeline:202: Running block: gen_detailed_summary
INFO 2025-03-25 05:53:48,725 instructlab.sdg.pipeline:202: Running block: gen_detailed_summary
INFO 2025-03-25 05:53:48,735 instructlab.sdg.pipeline:202: Running block: gen_detailed_summary
INFO 2025-03-25 05:53:54,511 instructlab.sdg.pipeline:202: Running block: gen_atomic_facts
INFO 2025-03-25 05:53:54,762 instructlab.sdg.pipeline:202: Running block: gen_atomic_facts
INFO 2025-03-25 05:53:55,206 instructlab.sdg.pipeline:202: Running block: gen_atomic_facts
INFO 2025-03-25 05:53:55,502 instructlab.sdg.pipeline:202: Running block: gen_atomic_facts
INFO 2025-03-25 05:54:01,348 instructlab.sdg.pipeline:202: Running block: gen_extractive_summary
INFO 2025-03-25 05:54:01,498 instructlab.sdg.pipeline:202: Running block: gen_extractive_summary
INFO 2025-03-25 05:54:01,793 instructlab.sdg.pipeline:202: Running block: gen_extractive_summary
INFO 2025-03-25 05:54:02,270 instructlab.sdg.pipeline:202: Running block: gen_extractive_summary
INFO 2025-03-25 05:54:05,475 instructlab.sdg.pipeline:202: Running block: flatten_summary_columns
INFO 2025-03-25 05:54:05,490 instructlab.sdg.pipeline:202: Running block: rename_to_document_column
INFO 2025-03-25 05:54:05,506 instructlab.sdg.pipeline:202: Running block: knowledge generation
INFO 2025-03-25 05:54:05,761 instructlab.sdg.pipeline:202: Running block: flatten_summary_columns
INFO 2025-03-25 05:54:05,777 instructlab.sdg.pipeline:202: Running block: rename_to_document_column
INFO 2025-03-25 05:54:05,793 instructlab.sdg.pipeline:202: Running block: knowledge generation
INFO 2025-03-25 05:54:06,437 instructlab.sdg.pipeline:202: Running block: flatten_summary_columns
INFO 2025-03-25 05:54:06,452 instructlab.sdg.pipeline:202: Running block: rename_to_document_column
INFO 2025-03-25 05:54:06,468 instructlab.sdg.pipeline:202: Running block: knowledge generation
INFO 2025-03-25 05:54:06,886 instructlab.sdg.pipeline:202: Running block: flatten_summary_columns
INFO 2025-03-25 05:54:06,902 instructlab.sdg.pipeline:202: Running block: rename_to_document_column
INFO 2025-03-25 05:54:06,918 instructlab.sdg.pipeline:202: Running block: knowledge generation
INFO 2025-03-25 05:55:47,026 instructlab.sdg.pipeline:202: Running block: eval_faithfulness_qa_pair
INFO 2025-03-25 05:55:47,347 instructlab.sdg.pipeline:202: Running block: eval_faithfulness_qa_pair
INFO 2025-03-25 05:55:48,029 instructlab.sdg.pipeline:202: Running block: eval_faithfulness_qa_pair
INFO 2025-03-25 05:55:48,482 instructlab.sdg.pipeline:202: Running block: eval_faithfulness_qa_pair
INFO 2025-03-25 05:57:18,135 instructlab.sdg.pipeline:202: Running block: filter_faithfulness

^MMap (num_proc=8):   0%|          | 0/8 [00:00<?, ? examples/s]^MMap (num_proc=8):  25%|##5       | 2/8 [00:00<00:00, 16.27 examples/s]^MMap (num_proc=8):  75%|#######5  | 6/8 [00:00<00:00, 26.81 examples/s]^M^MMap (num_proc=8): 100%|##########| 8/8 [00:00<00:00, 23.70 examples/s]
^MFilter (num_proc=8):   0%|          | 0/8 [00:00<?, ? examples/s]^MFilter (num_proc=8):  38%|###7      | 3/8 [00:00<00:00, 29.05 examples/s]^MFilter (num_proc=8): 100%|##########| 8/8 [00:00<00:00, 39.03 examples/s]

...<snip>...

392/392 [00:13<00:00, 28.71ba/s]INFO 2025-03-25 07:40:55,883 instructlab.sdg.datamixing:215: Mixed Dataset saved to /root/.local/share/instructlab/datasets/2025-03-25_055144/skills_train_msgs_2025-03-25T05_53_31.jsonl
INFO 2025-03-25 07:40:55,936 instructlab.sdg.datamixing:138: Loading dataset from /root/.local/share/instructlab/datasets/2025-03-25_055144/node_datasets_2025-03-25T05_53_31/knowledge_arts_music_fandom_swifties_p07.jsonl ...

^MGenerating train split: 0 examples [00:00, ? examples/s]^MGenerating train split: 3145 examples [00:00, 59930.06 examples/s]INFO 2025-03-25 07:40:56,600 instructlab.sdg.datamixing:140: Dataset columns: ['messages', 'metadata', 'id']
INFO 2025-03-25 07:40:56,600 instructlab.sdg.datamixing:141: Dataset loaded with 3145 samples

^MMap (num_proc=8):   0%|          | 0/3145 [00:00<?, ? examples/s]^MMap (num_proc=8):  12%|#2        | 386/3145 [00:00<00:01, 1411.63 examples/s]^MMap (num_proc=8):  99%|#########9| 3118/3145 [00:00<00:00, 10179.18 examples/s]^MMap (num_proc=8): 100%|##########| 3145/3145 [00:00<00:00, 6694.98 examples/s] INFO 2025-03-25 07:40:57,464 instructlab.sdg.datamixing:138: Loading dataset from /root/.local/share/instructlab/datasets/2025-03-25_055144/node_datasets_2025-03-25T05_53_31/knowledge_science_animals_birds_black_capped_chickadee_p07.jsonl ...

^MGenerating train split: 0 examples [00:00, ? examples/s]^MGenerating train split: 4700 examples [00:00, 57283.75 examples/s]INFO 2025-03-25 07:40:58,149 instructlab.sdg.datamixing:140: Dataset columns: ['messages', 'metadata', 'id']
INFO 2025-03-25 07:40:58,149 instructlab.sdg.datamixing:141: Dataset loaded with 4700 samples

^MMap (num_proc=8):   0%|          | 0/4700 [00:00<?, ? examples/s]^MMap (num_proc=8):   8%|7         | 372/4700 [00:00<00:03, 1359.72 examples/s]^MMap (num_proc=8):  54%|#####4    | 2549/4700 [00:00<00:00, 8320.62 examples/s]^MMap (num_proc=8): 100%|##########| 4700/4700 [00:00<00:00, 12586.64 examples/s]^MMap (num_proc=8): 100%|##########| 4700/4700 [00:00<00:00, 8277.95 examples/s] INFO 2025-03-25 07:40:59,106 instructlab.sdg.datamixing:138: Loading dataset from /root/.local/share/instructlab/datasets/2025-03-25_055144/node_datasets_2025-03-25T05_53_31/knowledge_science_astronomy_constellations_phoenix_p07.jsonl ...

^MGenerating train split: 0 examples [00:00, ? examples/s]^MGenerating train split: 5533 examples [00:00, 60634.55 examples/s]INFO 2025-03-25 07:40:59,879 instructlab.sdg.datamixing:140: Dataset columns: ['messages', 'metadata', 'id']
INFO 2025-03-25 07:40:59,879 instructlab.sdg.datamixing:141: Dataset loaded with 5533 samples

^MMap (num_proc=8):   0%|          | 0/5533 [00:00<?, ? examples/s]^MMap (num_proc=8):   7%|7         | 402/5533 [00:00<00:03, 1508.80 examples/s]^MMap (num_proc=8):  41%|####      | 2265/5533 [00:00<00:00, 7267.00 examples/s]^MMap (num_proc=8):  91%|######### | 5014/5533 [00:00<00:00, 13035.44 examples/s]^MMap (num_proc=8): 100%|##########| 5533/5533 [00:00<00:00, 8855.12 examples/s] INFO 2025-03-25 07:41:00,902 instructlab.sdg.datamixing:138: Loading dataset from /root/.local/share/instructlab/datasets/2025-03-25_055144/node_datasets_2025-03-25T05_53_31/knowledge_science_astronomy_constellations_phoenix_eng_p07.jsonl ...

^MGenerating train split: 0 examples [00:00, ? examples/s]^MGenerating train split: 6658 examples [00:00, 56973.04 examples/s]^MGenerating train split: 6658 examples [00:00, 56557.19 examples/s]INFO 2025-03-25 07:41:01,632 instructlab.sdg.datamixing:140: Dataset columns: ['messages', 'metadata', 'id']
INFO 2025-03-25 07:41:01,633 instructlab.sdg.datamixing:141: Dataset loaded with 6658 samples

^MMap (num_proc=8):   0%|          | 0/6658 [00:00<?, ? examples/s]^MMap (num_proc=8):   6%|5         | 388/6658 [00:00<00:04, 1476.49 examples/s]^MMap (num_proc=8):  36%|###5      | 2387/6658 [00:00<00:00, 7795.27 examples/s]^MMap (num_proc=8):  71%|#######1  | 4745/6658 [00:00<00:00, 12620.40 examples/s]^MMap (num_proc=8):  98%|#########7| 6518/6658 [00:00<00:00, 14113.17 examples/s]^MMap (num_proc=8): 100%|##########| 6658/6658 [00:00<00:00, 9633.48 examples/s] 
^MMap (num_proc=8):   0%|          | 0/20036 [00:00<?, ? examples/s]^MMap (num_proc=8):   4%|3         | 768/20036 [00:00<00:06, 2924.38 examples/s]^MMap (num_proc=8):  15%|#4        | 2965/20036 [00:00<00:01, 9376.61 examples/s]^MMap (num_proc=8):  29%|##8       | 5800/20036 [00:00<00:00, 15484.45 examples/s]^MMap (num_proc=8):  41%|####      | 8162/20036 [00:00<00:00, 17415.79 examples/s]^MMap (num_proc=8):  60%|######    | 12111/20036 [00:00<00:00, 23275.16 examples/s]^MMap (num_proc=8):  77%|#######6  | 15338/20036 [00:00<00:00, 25483.94 examples/s]^MMap (num_proc=8):  91%|#########1| 18325/20036 [00:00<00:00, 23149.17 examples/s]^MMap (num_proc=8): 100%|##########| 20036/20036 [00:01<00:00, 17945.16 examples/s]
^MCreating json from Arrow format:   0%|          | 0/21 [00:00<?, ?ba/s]^MCreating json from Arrow format:  14%|#4        | 3/21 [00:00<00:00, 27.00ba/s]^MCreating json from Arrow format:  29%|##8       | 6/21 [00:00<00:00, 28.01ba/s]^MCreating json from Arrow format:  48%|####7     | 10/21 [00:00<00:00, 28.84ba/s]^MCreating json from Arrow format:  67%|######6   | 14/21 [00:00<00:00, 29.50ba/s]^MCreating json from Arrow format:  86%|########5 | 18/21 [00:00<00:00, 29.89ba/s]^MCreating json from Arrow format: 100%|##########| 21/21 [00:00<00:00, 30.86ba/s]INFO 2025-03-25 07:41:04,869 instructlab.sdg.datamixing:215: Mixed Dataset saved to /root/.local/share/instructlab/datasets/2025-03-25_055144/knowledge_train_msgs_2025-03-25T05_53_31.jsonl
INFO 2025-03-25 07:41:04,871 instructlab.sdg.generate_data:732: Generation took 6453.51s
INFO 2025-03-25 07:41:17,413 instructlab.model.backends.vllm:494: Waiting for GPU VRAM reclamation...

[root@rhel_ai ~]# 
```
* 합성 데이터 생성 시간: 6453.51초 (1시간 47분 34초)

#### 5.2.3 생성된 합성 데이터 디렉터리 확인

실행 명령어
```bash
cd ~/datasets/2025-03-25_055144/
ls -lht
tree -F -L 3

```

실행 결과
```log
[root@rhel_ai ~]# cd ~/datasets/2025-03-25_055144/

[root@rhel_ai 2025-03-25_055144]# ls -lht
total 2.1G
-rw-r--r--. 1 root root 109M Mar 25 07:41 knowledge_train_msgs_2025-03-25T05_53_31.jsonl
-rw-r--r--. 1 root root 1.9G Mar 25 07:40 skills_train_msgs_2025-03-25T05_53_31.jsonl
-rw-r--r--. 1 root root 1.2K Mar 25 07:39 skills_recipe_2025-03-25T05_53_31.yaml
-rw-r--r--. 1 root root  723 Mar 25 07:39 knowledge_recipe_2025-03-25T05_53_31.yaml
-rw-r--r--. 1 root root  12M Mar 25 07:39 messages_2025-03-25T05_53_31.jsonl
-rw-r--r--. 1 root root 9.7M Mar 25 07:39 train_2025-03-25T05_53_31.jsonl
drwxr-xr-x. 2 root root 4.0K Mar 25 07:39 node_datasets_2025-03-25T05_53_31
drwxr-xr-x. 2 root root 4.0K Mar 25 07:38 generated_2025-03-25T05_53_31
-rw-r--r--. 1 root root 2.6M Mar 25 05:53 test_2025-03-25T05_53_31.jsonl
drwxr-xr-x. 3 root root 4.0K Mar 25 05:53 preprocessed_2025-03-25T05_53_31

[root@rhel_ai 2025-03-25_055144]#  tree -F -L 3
.
├── generated_2025-03-25T05_53_31/
│   ├── compositional_skills_grounded_linguistics_inclusion.jsonl
│   ├── compositional_skills_grounded_linguistics_writing_rewriting.jsonl
│   ├── compositional_skills_linguistics_synonyms.jsonl
│   ├── knowledge_arts_music_fandom_swifties.jsonl
│   ├── knowledge_science_animals_birds_black_capped_chickadee.jsonl
│   ├── knowledge_science_astronomy_constellations_phoenix.jsonl
│   └── knowledge_science_astronomy_constellations_phoenix_eng.jsonl
├── knowledge_recipe_2025-03-25T05_53_31.yaml
├── knowledge_train_msgs_2025-03-25T05_53_31.jsonl
├── messages_2025-03-25T05_53_31.jsonl
├── node_datasets_2025-03-25T05_53_31/
│   ├── compositional_skills_grounded_linguistics_inclusion.jsonl
│   ├── compositional_skills_grounded_linguistics_writing_rewriting.jsonl
│   ├── compositional_skills_linguistics_synonyms.jsonl
│   ├── knowledge_arts_music_fandom_swifties_p07.jsonl
│   ├── knowledge_arts_music_fandom_swifties_p10.jsonl
│   ├── knowledge_arts_music_fandom_swifties_task.yaml
│   ├── knowledge_science_animals_birds_black_capped_chickadee_p07.jsonl
│   ├── knowledge_science_animals_birds_black_capped_chickadee_p10.jsonl
│   ├── knowledge_science_animals_birds_black_capped_chickadee_task.yaml
│   ├── knowledge_science_astronomy_constellations_phoenix_eng_p07.jsonl
│   ├── knowledge_science_astronomy_constellations_phoenix_eng_p10.jsonl
│   ├── knowledge_science_astronomy_constellations_phoenix_eng_task.yaml
│   ├── knowledge_science_astronomy_constellations_phoenix_p07.jsonl
│   ├── knowledge_science_astronomy_constellations_phoenix_p10.jsonl
│   ├── knowledge_science_astronomy_constellations_phoenix_task.yaml
│   ├── mmlubench_knowledge_arts_music_fandom_swifties.jsonl
│   ├── mmlubench_knowledge_science_animals_birds_black_capped_chickadee.jsonl
│   ├── mmlubench_knowledge_science_astronomy_constellations_phoenix.jsonl
│   └── mmlubench_knowledge_science_astronomy_constellations_phoenix_eng.jsonl
├── preprocessed_2025-03-25T05_53_31/
│   ├── compositional_skills_grounded_linguistics_inclusion.jsonl
│   ├── compositional_skills_grounded_linguistics_writing_rewriting.jsonl
│   ├── compositional_skills_linguistics_synonyms.jsonl
│   ├── documents/
│   │   ├── docling-artifacts/
│   │   ├── knowledge_arts_music_fandom_swifties_ej6u86bu/
│   │   ├── knowledge_science_animals_birds_black_capped_chickadee_40xwivz6/
│   │   ├── knowledge_science_astronomy_constellations_phoenix__n63d5jo/
│   │   └── knowledge_science_astronomy_constellations_phoenix_eng_ix6mqmov/
│   ├── knowledge_arts_music_fandom_swifties.jsonl
│   ├── knowledge_science_animals_birds_black_capped_chickadee.jsonl
│   ├── knowledge_science_astronomy_constellations_phoenix.jsonl
│   └── knowledge_science_astronomy_constellations_phoenix_eng.jsonl
├── skills_recipe_2025-03-25T05_53_31.yaml
├── skills_train_msgs_2025-03-25T05_53_31.jsonl
├── test_2025-03-25T05_53_31.jsonl
└── train_2025-03-25T05_53_31.jsonl

9 directories, 40 files

[root@rhel_ai 2025-03-25_055144]# tree -F -sh preprocessed_2025-03-25T05_53_31/documents/docling-artifacts/
preprocessed_2025-03-25T05_53_31/documents/docling-artifacts/
├── [  52K]  chickadee.json
├── [  24K]  chickadee.md
├── [  30K]  phoenix.json
├── [  12K]  phoenix.md
├── [ 9.3K]  phoenix_constellation.json
├── [ 4.5K]  phoenix_constellation.md
├── [  52K]  swifties.json
└── [  25K]  swifties.md

0 directories, 8 files

[root@rhel_ai 2025-03-25_055144]# 
```

#### 5.2.4 합성 데이터의 전처리(preprocessed) 디렉터리 확인

실행 명령어
```bash
cd ~/datasets/2025-03-25_055144/
ls -lh
```

실행 결과
```log
[root@rhel_ai 2025-03-25_055144]# ls -lh preprocessed_2025-03-25T05_53_31/
total 2.3M
-rw-r--r--. 1 root root 3.8K Mar 25 05:53 compositional_skills_grounded_linguistics_inclusion.jsonl
-rw-r--r--. 1 root root 2.7K Mar 25 05:53 compositional_skills_grounded_linguistics_writing_rewriting.jsonl
-rw-r--r--. 1 root root 2.2K Mar 25 05:53 compositional_skills_linguistics_synonyms.jsonl
drwxr-xr-x. 7 root root 4.0K Mar 26 12:31 documents
-rw-r--r--. 1 root root 270K Mar 25 05:53 knowledge_arts_music_fandom_swifties.jsonl
-rw-r--r--. 1 root root 554K Mar 25 05:53 knowledge_science_animals_birds_black_capped_chickadee.jsonl
-rw-r--r--. 1 root root 604K Mar 25 05:53 knowledge_science_astronomy_constellations_phoenix.jsonl
-rw-r--r--. 1 root root 805K Mar 25 05:53 knowledge_science_astronomy_constellations_phoenix_eng.jsonl

[root@rhel_ai 2025-03-25_055144]# ls -lh preprocessed_2025-03-25T05_53_31/documents/
total 8.0K
drwxr-xr-x. 2 root root  192 Mar 26 12:32 docling-artifacts
drwx------. 3 root root 4.0K Mar 25 05:53 knowledge_arts_music_fandom_swifties_ej6u86bu
drwx------. 3 root root 4.0K Mar 25 05:53 knowledge_science_animals_birds_black_capped_chickadee_40xwivz6
drwx------. 3 root root  149 Mar 25 05:53 knowledge_science_astronomy_constellations_phoenix__n63d5jo
drwx------. 3 root root   53 Mar 25 05:53 knowledge_science_astronomy_constellations_phoenix_eng_ix6mqmov

[root@rhel_ai 2025-03-25_055144]# ls -lh preprocessed_2025-03-25T05_53_31/documents/docling-artifacts/
total 228K
-rw-r--r--. 1 root root  53K Mar 25 05:53 chickadee.json
-rw-r--r--. 1 root root  24K Mar 25 05:53 chickadee.md
-rw-r--r--. 1 root root  30K Mar 25 05:53 phoenix.json
-rw-r--r--. 1 root root  13K Mar 25 05:53 phoenix.md
-rw-r--r--. 1 root root 9.4K Mar 25 05:53 phoenix_constellation.json
-rw-r--r--. 1 root root 4.5K Mar 25 05:53 phoenix_constellation.md
-rw-r--r--. 1 root root  52K Mar 25 05:53 swifties.json
-rw-r--r--. 1 root root  26K Mar 25 05:53 swifties.md

[root@rhel_ai 2025-03-25_055144]#
```
* 택소트리의 지식 관련 ***qna.yaml***이 있는 경우에 *knownldge_<file_path>.jsonl* 생성
* 택소트리의 복합 기술이 해당하는 *compositional_skills_<file_path>.jsonl* 생성
* 지식 관련에 ***qna.yaml***에 마크다운 문서 관련된 데이터가 *documents* 디렉터리에 생성됨
  + knowledge_\*로 시작하는 디렉터리는 ***qna.yaml***에서 지정한 마크다운의 깃허브 리포지토리를 복제한 디렉터리
  + docling-artifacts 디렉터리에는 ***qna.yaml***에서 지정한 마크다운 문서 원본과 JSON으로 변환한 파일이 있음
    - git에 있는 PDF를 읽고 처리하여, 마크다운 문서로 만들고, 이를 기반으로 JSON으로 변환
    - phoenix_constellation.json 파일
      ```json
      {
        "_name": "",
        "type": "pdf-document",
        "description": {
          "logs": []
        },
        "file-info": {
          "filename": "phoenix_constellation.md",
          "document-hash": "7f8332b5e40e7d0a1fb271ee6e0b17bab0458d5aa8369d4f52e47aece4e7e729",
          "#-pages": 0,
          "page-hashes": []
        },
        "main-text": [
          {
            "prov": [],
            "text": "불사조(별자리)",
            "type": "title",
            "name": "Title"
          },
          {
            "prov": [],
            "text": "불사조는 남쪽 하늘의 작은 별자리입니다. 신화 속 불사조의 이름을 따서 지어졌으며, 요한 바이어가 1603년 우라노메트리아에서 처음으로 천체 지도에 묘사했습니다. 프랑스의 탐험가이자 천문학자인 니콜라 루이 드 라카유는 1756년에 더 밝은 별을 지도에 표시하고 바이어 명칭을 부여했습니다. 이 별자리는 약 -39도에서 -57도의 적위와 23.5h에서 2.5h의 적경으로 뻗어 있습니다. 불사조, 두루미, 공작, 투카나 별자리는 남부의 새라고 불립니다.",
            "type": "paragraph",
            "name": "paragraph"
          },
          {
            "prov": [],
            "text": "가장 밝은 별인 알파 포에니시스는 아랍어로 '불사조'를 의미하는 안카아라는 이름이 붙었습니다. 겉보기 등급이 2.4인 주황색 거성입니다. 다음은 베타 포에니시스로, 실제로는 두 개의 노란색 거성으로 구성된 이진계로, 겉보기 등급이 3.3입니다. Nu 포에니시스는 먼지 원반을 가지고 있는 반면, 이 별자리에는 알려진 행성과 최근에 발견된 은하계 클러스터인 엘 고르도와 피닉스 클러스터가 있는 10개의 항성계가 있습니다. 각각 72억 광년과 57억 광년 떨어져 있으며, 가시 우주에서 가장 큰 두 천체입니다. 불사조는 두 개의 연간 유성우, 12월의 포에니시드와 7월의 포에니시드의 방사점입니다.",
            "type": "paragraph",
            "name": "paragraph"
          },
          {
            "prov": [],
            "text": "역사",
            "type": "subtitle-level-1",
            "name": "Section-header"
          },
          {
            "prov": [],
            "text": "피닉스는 피터 디르크스존 카이저와 프레데릭 드 호우트만의 관측을 통해 페트루스 플란시우스가 확립한 12개 별자리 중 가장 큰 별자리였습니다. 처음에는 플란시우스와 요도쿠스 혼디우스가 1597년(또는 1598년) 암스테르담에서 출판한 직경 35cm의 천구에 처음 등장했습니다. 천체 지도에 이 별자리가 처음 묘사된 것은 1603년 요한 바이어의 우라노메트리아에 나와 있습니다. 드 호우트만은 같은 해에 네덜란드어 이름인 덴 보겔 페닉스, \"불사조\"라는 이름으로 남방 별자리 카탈로그에 포함시켰는데, 이는 고전 신화의 불사조를 상징합니다. 가장 밝은 별인 알파 페니키스의 이름 중 하나인 안카는 아랍어: العنقاء, 로마자: al-‘anqā’, 문자 그대로 '피닉스'라는 별은 1800년 이후 별자리와 관련하여 만들어졌습니다.",
            "type": "paragraph",
            "name": "paragraph"
          },
          {
            "prov": [],
            "text": "천체 역사가 리차드 앨런은 플랑시우스와 라 카유가 도입한 다른 별자리와 달리 피닉스는 고대 천문학에서 실제 선례가 있다고 언급했습니다. 아랍인들은 이 별자리를 어린 타조 알 리알 또는 그리핀이나 독수리로 보았습니다. 또한, 아랍인들은 때때로 같은 별 무리를 근처 에리다누스 강에 있는 배 알 자우락으로 생각했습니다. 그는 \"피닉스가 현대 천문학에 도입된 것은 어느 정도 발명이 아니라 채택을 통해서였다\"고 말했습니다.",
            "type": "paragraph",
            "name": "paragraph"
          },
          {
            "prov": [],
            "text": "중국인들은 피닉스의 가장 밝은 별인 안카(알파 포에니시스)와 인접한 별자리 조각가의 별을 통합하여 새를 잡는 그물인 바쿠이를 묘사했습니다. 피닉스와 인접한 별자리인 그루스는 율리우스 쉴러가 함께 대제사장 아론을 묘사하는 것으로 보았습니다. 이 두 별자리는 근처의 공작자리와 큰부리자리와 함께 남쪽의 새라고 불립니다.",
            "type": "paragraph",
            "name": "paragraph"
          },
          {
            "prov": [],
            "text": "특징",
            "type": "subtitle-level-1",
            "name": "Section-header"
          },
          {
            "prov": [],
            "text": "피닉스는 북쪽으로 포르낙스와 조각가자리, 서쪽으로 그루스자리, 남쪽으로 투카나자리, 남쪽으로 히드루스자리 모서리에 접하고, 동쪽과 남동쪽으로 에리다누스자리로 둘러싸인 작은 별자리입니다. 밝은 별 아케르나르가 근처에 있습니다. 국제 천문학 연맹에서 1922년에 채택한 별자리의 세 글자 약어는 \"페\"입니다. 벨기에 천문학자 유진 델포르트가 1930년에 정한 공식 별자리 경계는 10개의 세그먼트로 구성된 다각형으로 정의됩니다. 적도 좌표계에서 이 경계의 적경 좌표는 23h 26.5m와 02h 25.0m 사이에 있고, 적위 좌표는 −39.31°와 −57.84° 사이에 있습니다. 즉, 북반구에서 40도선 이북에 사는 사람에게는 지평선 아래에 있고, 적도 이북에 사는 사람에게는 하늘 낮은 곳에 있습니다. 남반구 늦은 봄에 호주와 남아프리카와 같은 곳에서 가장 잘 보입니다. 별자리의 대부분은 내부에 있으며, 밝은 별 Achernar, Fomalhaut 및 Beta Ceti의 삼각형을 형성하여 찾을 수 있습니다. Ankaa는 대략 이 삼각형의 중앙에 있습니다.",
            "type": "paragraph",
            "name": "paragraph"
          }
        ],
        "figures": [],
        "tables": [],
        "equations": [],
        "footnotes": [],
        "page-dimensions": [],
        "page-footers": [],
        "page-headers": []
      }
      ```

#### 5.2.5 지식 관련 훈련을 위한 합성 데이터 레시피 

실행 명령어
```bash
ls -lh knowledge_*
```

실행 결과
```
[root@rhel_ai 2025-03-25_055144]# ls -lh knowledge_*
-rw-r--r--. 1 root root  723 Mar 25 07:39 knowledge_recipe_2025-03-25T05_53_31.yaml
-rw-r--r--. 1 root root 109M Mar 25 07:41 knowledge_train_msgs_2025-03-25T05_53_31.jsonl

[root@rhel_ai 2025-03-25_055144]#
```

실행 명령어
```bash
cat knowledge_recipe_2025-03-25T05_53_31.yaml 
```

```yaml
datasets:
- path: node_datasets_2025-03-25T05_53_31/knowledge_arts_music_fandom_swifties_p07.jsonl
  sampling_size: 1.0
- path: node_datasets_2025-03-25T05_53_31/knowledge_science_animals_birds_black_capped_chickadee_p07.jsonl
  sampling_size: 1.0
- path: node_datasets_2025-03-25T05_53_31/knowledge_science_astronomy_constellations_phoenix_p07.jsonl
  sampling_size: 1.0
- path: node_datasets_2025-03-25T05_53_31/knowledge_science_astronomy_constellations_phoenix_eng_p07.jsonl
  sampling_size: 1.0
metadata:
  sys_prompt: "I am a Red Hat\xAE Instruct Model, an AI language model developed by\
    \ Red Hat and IBM Research based on the granite-3.1-8b-base model. My primary\
    \ role is to serve as a chat assistant."
```

#### 5.2.6 기술 관련 훈련을 위한 합성 데이터 레시피 

실행 명령어
```bash
ls -lh skills_*
```

실행 결과
```
[root@rhel_ai 2025-03-25_055144]# ls -lh skills_*
-rw-r--r--. 1 root root 1.2K Mar 25 07:39 skills_recipe_2025-03-25T05_53_31.yaml
-rw-r--r--. 1 root root 1.9G Mar 25 07:40 skills_train_msgs_2025-03-25T05_53_31.jsonl

[root@rhel_ai 2025-03-25_055144]# 
```

실행 명령어
```bash
cat skills_recipe_2025-03-25T05_53_31.yaml
```

```yaml
datasets:
- path: /usr/share/instructlab/sdg/datasets/skills.jsonl
  sampling_size: 1.0
- path: node_datasets_2025-03-25T05_53_31/compositional_skills_grounded_linguistics_inclusion.jsonl
  sampling_size: 30
- path: node_datasets_2025-03-25T05_53_31/compositional_skills_grounded_linguistics_writing_rewriting.jsonl
  sampling_size: 30
- path: node_datasets_2025-03-25T05_53_31/compositional_skills_linguistics_synonyms.jsonl
  sampling_size: 30
- path: node_datasets_2025-03-25T05_53_31/knowledge_arts_music_fandom_swifties_p10.jsonl
  sampling_size: 10392
- path: node_datasets_2025-03-25T05_53_31/knowledge_science_animals_birds_black_capped_chickadee_p10.jsonl
  sampling_size: 10392
- path: node_datasets_2025-03-25T05_53_31/knowledge_science_astronomy_constellations_phoenix_p10.jsonl
  sampling_size: 1.0
- path: node_datasets_2025-03-25T05_53_31/knowledge_science_astronomy_constellations_phoenix_eng_p10.jsonl
  sampling_size: 1.0
metadata:
  sys_prompt: "I am a Red Hat\xAE Instruct Model, an AI language model developed by\
    \ Red Hat and IBM Research based on the granite-3.1-8b-base model. My primary\
    \ role is to serve as a chat assistant."
```

#### 5.2.7 합성 데이터의 generated_* 디렉터리 확인

실행 명령어
```bash
ls -lh generated_2025-03-25T05_53_31/
```

실행 결과
```
[root@rhel_ai 2025-03-25_055144]# ls -lh generated_2025-03-25T05_53_31/
total 108M
-rw-r--r--. 1 root root 134K Mar 25 05:53 compositional_skills_grounded_linguistics_inclusion.jsonl
-rw-r--r--. 1 root root  67K Mar 25 05:53 compositional_skills_grounded_linguistics_writing_rewriting.jsonl
-rw-r--r--. 1 root root 226K Mar 25 05:53 compositional_skills_linguistics_synonyms.jsonl
-rw-r--r--. 1 root root  17M Mar 25 06:05 knowledge_arts_music_fandom_swifties.jsonl
-rw-r--r--. 1 root root  26M Mar 25 06:12 knowledge_science_animals_birds_black_capped_chickadee.jsonl
-rw-r--r--. 1 root root  29M Mar 25 06:22 knowledge_science_astronomy_constellations_phoenix.jsonl
-rw-r--r--. 1 root root  37M Mar 25 07:38 knowledge_science_astronomy_constellations_phoenix_eng.jsonl

[root@rhel_ai 2025-03-25_055144]#
```

#### 5.2.8 합성 데이터의 node_datasets_* 디렉터리 확인

실행 명령어
```bash
ls -lh node_datasets_2025-03-25T05_53_31/
```

실행 결과
```
[root@rhel_ai 2025-03-25_055144]# ls -lh node_datasets_2025-03-25T05_53_31/
total 403M
-rw-r--r--. 1 root root 154K Mar 25 07:39 compositional_skills_grounded_linguistics_inclusion.jsonl
-rw-r--r--. 1 root root  74K Mar 25 07:39 compositional_skills_grounded_linguistics_writing_rewriting.jsonl
-rw-r--r--. 1 root root 250K Mar 25 07:39 compositional_skills_linguistics_synonyms.jsonl
-rw-r--r--. 1 root root  17M Mar 25 07:39 knowledge_arts_music_fandom_swifties_p07.jsonl
-rw-r--r--. 1 root root  46M Mar 25 07:39 knowledge_arts_music_fandom_swifties_p10.jsonl
-rw-r--r--. 1 root root  628 Mar 25 07:38 knowledge_arts_music_fandom_swifties_task.yaml
-rw-r--r--. 1 root root  25M Mar 25 07:39 knowledge_science_animals_birds_black_capped_chickadee_p07.jsonl
-rw-r--r--. 1 root root  68M Mar 25 07:39 knowledge_science_animals_birds_black_capped_chickadee_p10.jsonl
-rw-r--r--. 1 root root  664 Mar 25 07:38 knowledge_science_animals_birds_black_capped_chickadee_task.yaml
-rw-r--r--. 1 root root  35M Mar 25 07:39 knowledge_science_astronomy_constellations_phoenix_eng_p07.jsonl
-rw-r--r--. 1 root root  95M Mar 25 07:39 knowledge_science_astronomy_constellations_phoenix_eng_p10.jsonl
-rw-r--r--. 1 root root  664 Mar 25 07:39 knowledge_science_astronomy_constellations_phoenix_eng_task.yaml
-rw-r--r--. 1 root root  29M Mar 25 07:39 knowledge_science_astronomy_constellations_phoenix_p07.jsonl
-rw-r--r--. 1 root root  79M Mar 25 07:39 knowledge_science_astronomy_constellations_phoenix_p10.jsonl
-rw-r--r--. 1 root root  656 Mar 25 07:38 knowledge_science_astronomy_constellations_phoenix_task.yaml
-rw-r--r--. 1 root root 1.2M Mar 25 07:38 mmlubench_knowledge_arts_music_fandom_swifties.jsonl
-rw-r--r--. 1 root root 2.5M Mar 25 07:38 mmlubench_knowledge_science_animals_birds_black_capped_chickadee.jsonl
-rw-r--r--. 1 root root 3.9M Mar 25 07:38 mmlubench_knowledge_science_astronomy_constellations_phoenix.jsonl
-rw-r--r--. 1 root root 3.9M Mar 25 07:39 mmlubench_knowledge_science_astronomy_constellations_phoenix_eng.jsonl

[root@rhel_ai 2025-03-25_055144]#
```
* knowledge_science_astronomy_constellations_phoenix_task.yaml 파일 확인
  ```yaml
  dataset_kwargs:
    data_files:
      test: /root/.local/share/instructlab/datasets/2025-03-25_055144/node_datasets_2025-03-25T05_53_31/mmlubench_knowledge_science_astronomy_constellations_phoenix.jsonl
  dataset_name: null
  dataset_path: json
  doc_to_choice: '{{[choices[0], choices[1], choices[2], choices[3]]}}'
  doc_to_target: '{{answer}}'
  doc_to_text: '{{question.strip()}}
  
    A. {{choices[0]}}
  
    B. {{choices[1]}}
  
    C. {{choices[2]}}
  
    D. {{choices[3]}}
  
    Answer:'
  metric_list:
  - aggregation: mean
    higher_is_better: 'true'
    metric: acc
  output_type: multiple_choice
  tag: mmlu_pr
  task: knowledge_science_astronomy_constellations_phoenix
  test_split: test  
  ```
<br>

### 5.3 Phase1 훈련

#### 5.3.1 Phase1 디렉터리 확인

실행 명령어
```bash
cd ~/phased
tree -F -sh phase1
```

실행 결과
```
[root@rhel_ai ~]# cd ~/phased

[root@rhel_ai phased]# tree -F -sh phase1
phase1
├── [  139]  checkpoints/
│   ├── [ 2.3M]  full_logs_global0.log
│   ├── [  143]  full_state/
│   │   ├── [ 4.0K]  epoch_0/
│   │   │   ├── [  30G]  optimizer.bin
│   │   │   ├── [  15G]  pytorch_model_fsdp.bin
│   │   │   ├── [  16K]  random_states_0.pkl
│   │   │   ├── [  16K]  random_states_1.pkl
│   │   │   ├── [  16K]  random_states_2.pkl
│   │   │   ├── [  16K]  random_states_3.pkl
│   │   │   ├── [  16K]  random_states_4.pkl
│   │   │   ├── [  16K]  random_states_5.pkl
│   │   │   ├── [  16K]  random_states_6.pkl
│   │   │   ├── [  16K]  random_states_7.pkl
│   │   │   ├── [ 1000]  scheduler.bin
│   │   │   └── [  968]  training_metadata.json
│   │   ├── [ 4.0K]  epoch_1/
│   │   │   ├── [  30G]  optimizer.bin
│   │   │   ├── [  15G]  pytorch_model_fsdp.bin
│   │   │   ├── [  16K]  random_states_0.pkl
│   │   │   ├── [  16K]  random_states_1.pkl
│   │   │   ├── [  16K]  random_states_2.pkl
│   │   │   ├── [  16K]  random_states_3.pkl
│   │   │   ├── [  16K]  random_states_4.pkl
│   │   │   ├── [  16K]  random_states_5.pkl
│   │   │   ├── [  16K]  random_states_6.pkl
│   │   │   ├── [  16K]  random_states_7.pkl
│   │   │   ├── [ 1000]  scheduler.bin
│   │   │   └── [  968]  training_metadata.json
│   │   ├── [ 4.0K]  epoch_2/
│   │   │   ├── [  30G]  optimizer.bin
│   │   │   ├── [  15G]  pytorch_model_fsdp.bin
│   │   │   ├── [  16K]  random_states_0.pkl
│   │   │   ├── [  16K]  random_states_1.pkl
│   │   │   ├── [  16K]  random_states_2.pkl
│   │   │   ├── [  16K]  random_states_3.pkl
│   │   │   ├── [  16K]  random_states_4.pkl
│   │   │   ├── [  16K]  random_states_5.pkl
│   │   │   ├── [  16K]  random_states_6.pkl
│   │   │   ├── [  16K]  random_states_7.pkl
│   │   │   ├── [ 1000]  scheduler.bin
│   │   │   └── [  968]  training_metadata.json
│   │   ├── [ 4.0K]  epoch_3/
│   │   │   ├── [  30G]  optimizer.bin
│   │   │   ├── [  15G]  pytorch_model_fsdp.bin
│   │   │   ├── [  16K]  random_states_0.pkl
│   │   │   ├── [  16K]  random_states_1.pkl
│   │   │   ├── [  16K]  random_states_2.pkl
│   │   │   ├── [  16K]  random_states_3.pkl
│   │   │   ├── [  16K]  random_states_4.pkl
│   │   │   ├── [  16K]  random_states_5.pkl
│   │   │   ├── [  16K]  random_states_6.pkl
│   │   │   ├── [  16K]  random_states_7.pkl
│   │   │   ├── [ 1000]  scheduler.bin
│   │   │   └── [  968]  training_metadata.json
│   │   ├── [ 4.0K]  epoch_4/
│   │   │   ├── [  30G]  optimizer.bin
│   │   │   ├── [  15G]  pytorch_model_fsdp.bin
│   │   │   ├── [  16K]  random_states_0.pkl
│   │   │   ├── [  16K]  random_states_1.pkl
│   │   │   ├── [  16K]  random_states_2.pkl
│   │   │   ├── [  16K]  random_states_3.pkl
│   │   │   ├── [  16K]  random_states_4.pkl
│   │   │   ├── [  16K]  random_states_5.pkl
│   │   │   ├── [  16K]  random_states_6.pkl
│   │   │   ├── [  16K]  random_states_7.pkl
│   │   │   ├── [ 1000]  scheduler.bin
│   │   │   └── [  968]  training_metadata.json
│   │   ├── [ 4.0K]  epoch_5/
│   │   │   ├── [  30G]  optimizer.bin
│   │   │   ├── [  15G]  pytorch_model_fsdp.bin
│   │   │   ├── [  16K]  random_states_0.pkl
│   │   │   ├── [  16K]  random_states_1.pkl
│   │   │   ├── [  16K]  random_states_2.pkl
│   │   │   ├── [  16K]  random_states_3.pkl
│   │   │   ├── [  16K]  random_states_4.pkl
│   │   │   ├── [  16K]  random_states_5.pkl
│   │   │   ├── [  16K]  random_states_6.pkl
│   │   │   ├── [  16K]  random_states_7.pkl
│   │   │   ├── [ 1000]  scheduler.bin
│   │   │   └── [  968]  training_metadata.json
│   │   └── [ 4.0K]  epoch_6/
│   │       ├── [  30G]  optimizer.bin
│   │       ├── [  15G]  pytorch_model_fsdp.bin
│   │       ├── [  16K]  random_states_0.pkl
│   │       ├── [  16K]  random_states_1.pkl
│   │       ├── [  16K]  random_states_2.pkl
│   │       ├── [  16K]  random_states_3.pkl
│   │       ├── [  16K]  random_states_4.pkl
│   │       ├── [  16K]  random_states_5.pkl
│   │       ├── [  16K]  random_states_6.pkl
│   │       ├── [  16K]  random_states_7.pkl
│   │       ├── [ 1000]  scheduler.bin
│   │       └── [  968]  training_metadata.json
│   ├── [  188]  hf_format/
│   │   ├── [ 4.0K]  samples_100077/
│   │   │   ├── [  769]  config.json
│   │   │   ├── [  140]  generation_config.json
│   │   │   ├── [ 4.7G]  model-00001-of-00004.safetensors
│   │   │   ├── [ 4.6G]  model-00002-of-00004.safetensors
│   │   │   ├── [ 4.6G]  model-00003-of-00004.safetensors
│   │   │   ├── [ 1.3G]  model-00004-of-00004.safetensors
│   │   │   ├── [  29K]  model.safetensors.index.json
│   │   │   ├── [  742]  special_tokens_map.json
│   │   │   ├── [ 3.3M]  tokenizer.json
│   │   │   └── [ 5.2K]  tokenizer_config.json
│   │   ├── [ 4.0K]  samples_120101/
│   │   │   ├── [  769]  config.json
│   │   │   ├── [  140]  generation_config.json
│   │   │   ├── [ 4.7G]  model-00001-of-00004.safetensors
│   │   │   ├── [ 4.6G]  model-00002-of-00004.safetensors
│   │   │   ├── [ 4.6G]  model-00003-of-00004.safetensors
│   │   │   ├── [ 1.3G]  model-00004-of-00004.safetensors
│   │   │   ├── [  29K]  model.safetensors.index.json
│   │   │   ├── [  742]  special_tokens_map.json
│   │   │   ├── [ 3.3M]  tokenizer.json
│   │   │   └── [ 5.2K]  tokenizer_config.json
│   │   ├── [ 4.0K]  samples_140119/
│   │   │   ├── [  769]  config.json
│   │   │   ├── [  140]  generation_config.json
│   │   │   ├── [ 4.7G]  model-00001-of-00004.safetensors
│   │   │   ├── [ 4.6G]  model-00002-of-00004.safetensors
│   │   │   ├── [ 4.6G]  model-00003-of-00004.safetensors
│   │   │   ├── [ 1.3G]  model-00004-of-00004.safetensors
│   │   │   ├── [  29K]  model.safetensors.index.json
│   │   │   ├── [  742]  special_tokens_map.json
│   │   │   ├── [ 3.3M]  tokenizer.json
│   │   │   └── [ 5.2K]  tokenizer_config.json
│   │   ├── [ 4.0K]  samples_20016/
│   │   │   ├── [  769]  config.json
│   │   │   ├── [  140]  generation_config.json
│   │   │   ├── [ 4.7G]  model-00001-of-00004.safetensors
│   │   │   ├── [ 4.6G]  model-00002-of-00004.safetensors
│   │   │   ├── [ 4.6G]  model-00003-of-00004.safetensors
│   │   │   ├── [ 1.3G]  model-00004-of-00004.safetensors
│   │   │   ├── [  29K]  model.safetensors.index.json
│   │   │   ├── [  742]  special_tokens_map.json
│   │   │   ├── [ 3.3M]  tokenizer.json
│   │   │   └── [ 5.2K]  tokenizer_config.json
│   │   ├── [ 4.0K]  samples_40034/
│   │   │   ├── [  769]  config.json
│   │   │   ├── [  140]  generation_config.json
│   │   │   ├── [ 4.7G]  model-00001-of-00004.safetensors
│   │   │   ├── [ 4.6G]  model-00002-of-00004.safetensors
│   │   │   ├── [ 4.6G]  model-00003-of-00004.safetensors
│   │   │   ├── [ 1.3G]  model-00004-of-00004.safetensors
│   │   │   ├── [  29K]  model.safetensors.index.json
│   │   │   ├── [  742]  special_tokens_map.json
│   │   │   ├── [ 3.3M]  tokenizer.json
│   │   │   └── [ 5.2K]  tokenizer_config.json
│   │   ├── [ 4.0K]  samples_60048/
│   │   │   ├── [  769]  config.json
│   │   │   ├── [  140]  generation_config.json
│   │   │   ├── [ 4.7G]  model-00001-of-00004.safetensors
│   │   │   ├── [ 4.6G]  model-00002-of-00004.safetensors
│   │   │   ├── [ 4.6G]  model-00003-of-00004.safetensors
│   │   │   ├── [ 1.3G]  model-00004-of-00004.safetensors
│   │   │   ├── [  29K]  model.safetensors.index.json
│   │   │   ├── [  742]  special_tokens_map.json
│   │   │   ├── [ 3.3M]  tokenizer.json
│   │   │   └── [ 5.2K]  tokenizer_config.json
│   │   └── [ 4.0K]  samples_80070/
│   │       ├── [  769]  config.json
│   │       ├── [  140]  generation_config.json
│   │       ├── [ 4.7G]  model-00001-of-00004.safetensors
│   │       ├── [ 4.6G]  model-00002-of-00004.safetensors
│   │       ├── [ 4.6G]  model-00003-of-00004.safetensors
│   │       ├── [ 1.3G]  model-00004-of-00004.safetensors
│   │       ├── [  29K]  model.safetensors.index.json
│   │       ├── [  742]  special_tokens_map.json
│   │       ├── [ 3.3M]  tokenizer.json
│   │       └── [ 5.2K]  tokenizer_config.json
│   └── [ 408K]  training_params_and_metrics_global0.jsonl
└── [   10]  eval_cache/

18 directories, 156 files

[root@rhel_ai phased]# 
```
* *eval_cache* 디렉터리가 비어 있음

#### 5.3.2 훈련 패러미티 및 스텝 확인

실행 명령어
```bash
cd ~/phase/phase1/checkpoints/
cat training_params_and_metrics_global0.jsonl | jq '.'
```

```json
{
  "script_params": {
    "model_name_or_path": "/root/.cache/instructlab/models/granite-3.1-8b-starter-v1",
    "data_path": "/root/.local/share/instructlab/internal/data.jsonl",
    "output_dir": "/root/.local/share/instructlab/phased/phase1/checkpoints",
    "num_epochs": 7,
    "current_epoch": 0,
    "last_step": 0,
    "effective_batch_size": 128,
    "learning_rate": 0.00002,
    "lr_scheduler": "cosine",
    "num_warmup_steps": 25,
    "save_samples": 0,
    "save_samples_ds": null,
    "save_last": false,
    "checkpoint_at_epoch": true,
    "accelerate_full_state_at_epoch": true,
    "log_level": "INFO",
    "seed": 42,
    "mock_data": false,
    "mock_len": 2600,
    "distributed_training_framework": "fsdp",
    "fsdp_sharding_strategy": "SHARD_GRAD_OP",
    "use_dolomite": true,
    "lora_r": 0,
    "lora_alpha": 32,
    "lora_dropout": 0.1,
    "lora_quant_bits": null,
    "lora_target_modules": [
      "q_proj",
      "k_proj",
      "v_proj",
      "o_proj"
    ],
    "max_batch_len": 60000,
    "cpu_offload_optimizer": false,
    "cpu_offload_params_fsdp": false,
    "cpu_offload_optimizer_pin_memory": false,
    "cpu_offload_optimizer_ratio": 1.0,
    "NEFTune_alpha": null,
    "chat_tmpl_path": "/opt/app-root/lib64/python3.11/site-packages/instructlab/training/chat_templates/ibm_legacy_tmpl.py",
    "disable_flash_attn": false,
    "keep_last_checkpoint_only": false
  },
  "timestamp": "2025-03-25T07:58:36.498258"
}
{
  "num_gpus": 8,
  "avg_sample_len": 538.6827211020163,
  "effective_batch_size": 128,
  "max_batch_len_per_gpu": 60000,
  "packing_max_batch_len": 8618,
  "grad_accum": 1,
  "num_batches": 158,
  "avg_samples_per_batch": 126.81012658227849,
  "samples_per_gpu": 16,
  "total_samples": 20036,
  "timestamp": "2025-03-25T07:58:55.449679"
}
{
  "epoch": 0,
  "step": 1,
  "rank": 0,
  "overall_throughput": 45.367698713089744,
  "lr": 8.000000000000001E-7,
  "cuda_mem_allocated": 6.639644622802734,
  "cuda_malloc_retries": 0,
  "num_loss_counted_tokens": 61591,
  "batch_size": 130,
  "total_loss": 2.5375135977659076,
  "samples_seen": 130,
  "gradnorm": 55.0,
  "total_samples": 20036,
  "timestamp": "2025-03-25T07:59:36.050337"
}
{
  "epoch": 0,
  "step": 2,
  "rank": 0,
  "overall_throughput": 56.3167630278514,
  "lr": 0.0000016000000000000001,
  "cuda_mem_allocated": 6.645055770874023,
  "cuda_malloc_retries": 0,
  "num_loss_counted_tokens": 61941,
  "batch_size": 125,
  "total_loss": 2.473579696808253,
  "samples_seen": 255,
  "gradnorm": 53.5,
  "total_samples": 20036,
  "timestamp": "2025-03-25T07:59:38.524983"
}

...<snip>...

{
  "epoch": 0,
  "step": 158,
  "rank": 0,
  "overall_throughput": 89.29456828751714,
  "lr": 0.00001926225221073686,
  "cuda_mem_allocated": 6.628194808959961,
  "cuda_malloc_retries": 0,
  "num_loss_counted_tokens": 61582,
  "batch_size": 130,
  "total_loss": 0.07830210126335617,
  "samples_seen": 20016,
  "gradnorm": 0.6640625,
  "total_samples": 20036,
  "timestamp": "2025-03-25T08:05:02.184999"
}
{
  "epoch": 1,
  "step": 159,
  "rank": 0,
  "overall_throughput": 67.79459788326449,
  "lr": 0.000019251257625399494,
  "cuda_mem_allocated": 6.644915580749512,
  "cuda_malloc_retries": 0,
  "num_loss_counted_tokens": 61388,
  "batch_size": 127,
  "total_loss": 0.06962272756890597,
  "samples_seen": 20143,
  "gradnorm": 0.40234375,
  "total_samples": 20036,
  "timestamp": "2025-03-25T08:06:54.664700"
}

...<snip>...

{
  "epoch": 6,
  "step": 1106,
  "rank": 0,
  "overall_throughput": 89.160686924904,
  "lr": 0.0,
  "cuda_mem_allocated": 6.644039630889893,
  "cuda_malloc_retries": 0,
  "num_loss_counted_tokens": 61829,
  "batch_size": 128,
  "total_loss": 0.04219702728493102,
  "samples_seen": 140119,
  "gradnorm": 0.361328125,
  "total_samples": 20036,
  "timestamp": "2025-03-25T08:48:02.022545"
}
```
* epoch 0 ~ 6

#### 5.3.3 로그 파일 확인

실행 명령어
```bash
less full_logs_global0.log 
```

실행 결과
```
[root@rhel_ai checkpoints]# less full_logs_global0.log 
W0325 07:58:27.489000 905 torch/distributed/run.py:793] 
W0325 07:58:27.489000 905 torch/distributed/run.py:793] *****************************************
W0325 07:58:27.489000 905 torch/distributed/run.py:793] Setting OMP_NUM_THREADS environment variable for each process to be 1 in default, to avoid your system being overloaded, please further tune the variable for optimal performance in your application as needed. 
W0325 07:58:27.489000 905 torch/distributed/run.py:793] *****************************************
[2025-03-25 07:58:32,399] [INFO] [real_accelerator.py:219:get_accelerator] Setting ds_accelerator to cuda (auto detect)
[2025-03-25 07:58:33,332] [INFO] [real_accelerator.py:219:get_accelerator] Setting ds_accelerator to cuda (auto detect)
[2025-03-25 07:58:33,491] [INFO] [real_accelerator.py:219:get_accelerator] Setting ds_accelerator to cuda (auto detect)
[2025-03-25 07:58:33,746] [INFO] [real_accelerator.py:219:get_accelerator] Setting ds_accelerator to cuda (auto detect)
[2025-03-25 07:58:33,767] [INFO] [real_accelerator.py:219:get_accelerator] Setting ds_accelerator to cuda (auto detect)
[2025-03-25 07:58:33,984] [INFO] [real_accelerator.py:219:get_accelerator] Setting ds_accelerator to cuda (auto detect)
[2025-03-25 07:58:33,994] [INFO] [real_accelerator.py:219:get_accelerator] Setting ds_accelerator to cuda (auto detect)
[2025-03-25 07:58:34,020] [INFO] [real_accelerator.py:219:get_accelerator] Setting ds_accelerator to cuda (auto detect)
ESC[38;5;120mmodel_name_or_path: /root/.cache/instructlab/models/granite-3.1-8b-starter-v1
data_path: /root/.local/share/instructlab/internal/data.jsonl
output_dir: /root/.local/share/instructlab/phased/phase1/checkpoints
num_epochs: 7
current_epoch: 0
last_step: 0
effective_batch_size: 128
learning_rate: 2.0e-05
lr_scheduler: cosine
num_warmup_steps: 25
save_samples: 0
save_samples_ds: null
save_last: false
checkpoint_at_epoch: true
accelerate_full_state_at_epoch: true
log_level: INFO
seed: 42
mock_data: false
mock_len: 2600
distributed_training_framework: fsdp
fsdp_sharding_strategy: SHARD_GRAD_OP
use_dolomite: true
lora_r: 0
lora_alpha: 32
lora_dropout: 0.1
lora_quant_bits: null
lora_target_modules:
- q_proj
- k_proj
- v_proj
- o_proj
max_batch_len: 60000
cpu_offload_optimizer: false
cpu_offload_params_fsdp: false
cpu_offload_optimizer_pin_memory: false
cpu_offload_optimizer_ratio: 1.0
NEFTune_alpha: null
chat_tmpl_path: /opt/app-root/lib64/python3.11/site-packages/instructlab/training/chat_templates/ibm_legacy_tmpl.py
disable_flash_attn: false
keep_last_checkpoint_only: false
ESC[0m
ESC[92m{
    "script_params": {
        "model_name_or_path": "/root/.cache/instructlab/models/granite-3.1-8b-starter-v1",
        "data_path": "/root/.local/share/instructlab/internal/data.jsonl",
        "output_dir": "/root/.local/share/instructlab/phased/phase1/checkpoints",
        "num_epochs": 7,
        "current_epoch": 0,
        "last_step": 0,
        "effective_batch_size": 128,
        "learning_rate": 2e-05,
        "lr_scheduler": "cosine",
        "num_warmup_steps": 25,
        "save_samples": 0,
        "save_samples_ds": null,
        "save_last": false,
        "checkpoint_at_epoch": true,
        "accelerate_full_state_at_epoch": true,
        "log_level": "INFO",
        "seed": 42,
        "mock_data": false,
        "mock_len": 2600,
        "distributed_training_framework": "fsdp",
        "fsdp_sharding_strategy": "SHARD_GRAD_OP",
        "use_dolomite": true,
        "lora_r": 0,
        "lora_alpha": 32,
        "lora_dropout": 0.1,
        "lora_quant_bits": null,
        "lora_target_modules": [
            "q_proj",
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj"
        ],
        "max_batch_len": 60000,
        "cpu_offload_optimizer": false,
        "cpu_offload_params_fsdp": false,
        "cpu_offload_optimizer_pin_memory": false,
        "cpu_offload_optimizer_ratio": 1.0,
        "NEFTune_alpha": null,
        "chat_tmpl_path": "/opt/app-root/lib64/python3.11/site-packages/instructlab/training/chat_templates/ibm_legacy_tmpl.py",
        "disable_flash_attn": false,
        "keep_last_checkpoint_only": false
    },
    "timestamp": "2025-03-25T07:58:36.498258"
}ESC[0m
^MGenerating train split: 0 examples [00:00, ? examples/s]^MGenerating train split: 2162 examples [00:00, 14669.34 examples/s]^MGenerating
 train split: 4297 examples [00:00, 15431.36 examples/s]^MGenerating train split: 6408 examples [00:00, 15759.60 examples/s]^MGenerating t
rain split: 8499 examples [00:00, 15893.58 examples/s]^MGenerating train split: 10696 examples [00:00, 16302.48 examples/s]^MGenerating tr
ain split: 12862 examples [00:00, 16541.23 examples/s]^MGenerating train split: 14941 examples [00:00, 16362.09 examples/s]^MGenerating tr
ain split: 20036 examples [00:01, 16283.98 examples/s]
You are using a model of type granite to instantiate a model of type gpt_dolomite. This is not supported for all configurations of models 
and can yield errors.
You are using a model of type granite to instantiate a model of type gpt_dolomite. This is not supported for all configurations of models 
and can yield errors.
You are using a model of type granite to instantiate a model of type gpt_dolomite. This is not supported for all configurations of models 
and can yield errors.
ESC[93mModel saved in /root/.cache/instructlab/models/granite-3.1-8b-starter-v1 requires conversion ESC[0m
ESC[92m{
    "num_gpus": 8,
    "avg_sample_len": 538.6827211020163,
    "effective_batch_size": 128,
    "max_batch_len_per_gpu": 60000,
    "packing_max_batch_len": 8618,
    "grad_accum": 1,
    "num_batches": 158,
    "avg_samples_per_batch": 126.81012658227849,
    "samples_per_gpu": 16,
    "total_samples": 20036,
    "timestamp": "2025-03-25T07:58:55.449679"
}ESC[0m
You are using a model of type granite to instantiate a model of type gpt_dolomite. This is not supported for all configurations of models 
and can yield errors.

...<snip>...

Epoch: 0, Step: 1, Rank: 3, loss = 2.421875Epoch: 0, Step: 1, Rank: 2, loss = 2.765625Epoch: 0, Step: 1, Rank: 6, loss = 2.5625

Epoch: 0, Step: 1, Rank: 1, loss = 2.484375
Epoch: 0, Step: 1, Rank: 7, loss = 2.59375
Epoch: 0, Step: 1, Rank: 0, loss = 2.21875
Epoch: 0, Step: 1, Rank: 4, loss = 2.5625
Epoch: 0, Step: 1, Rank: 5, loss = 2.703125
^MEpoch 0:   1%|          | 1/158 [00:03<08:13,  3.14s/it]ESC[92m{
    "epoch": 0,
    "step": 1,
    "rank": 0,
    "overall_throughput": 45.367698713089744,
    "lr": 8.000000000000001e-07,
    "cuda_mem_allocated": 6.639644622802734,
    "cuda_malloc_retries": 0,
    "num_loss_counted_tokens": 61591,
    "batch_size": 130,
    "total_loss": 2.5375135977659076,
    "samples_seen": 130,
    "gradnorm": 55.0,
    "total_samples": 20036,
    "timestamp": "2025-03-25T07:59:36.050337"
}ESC[0m

...<snip>...

Epoch: 0, Step: 2, Rank: 1, loss = 2.4375
Epoch: 0, Step: 2, Rank: 5, loss = 2.5625
Epoch: 0, Step: 2, Rank: 6, loss = 2.5625Epoch: 0, Step: 2, Rank: 3, loss = 2.484375Epoch: 0, Step: 2, Rank: 0, loss = 2.359375Epoch: 0, Step: 2, Rank: 2, loss = 2.40625
Epoch: 0, Step: 2, Rank: 7, loss = 2.375

Epoch: 0, Step: 2, Rank: 4, loss = 2.59375
^MEpoch 0:   1%|▏         | 2/158 [00:05<07:08,  2.75s/it]ESC[92m{
    "epoch": 0,
    "step": 2,
    "rank": 0,
    "overall_throughput": 56.3167630278514,
    "lr": 1.6000000000000001e-06,
    "cuda_mem_allocated": 6.645055770874023,
    "cuda_malloc_retries": 0,
    "num_loss_counted_tokens": 61941,
    "batch_size": 125,
    "total_loss": 2.473579696808253,
    "samples_seen": 255,
    "gradnorm": 53.5,
    "total_samples": 20036,
    "timestamp": "2025-03-25T07:59:38.524983"
}ESC[0m

...<snip>...

Epoch: 0, Step: 158, Rank: 1, loss = 0.060791015625Epoch: 0, Step: 158, Rank: 3, loss = 0.0537109375
Epoch: 0, Step: 158, Rank: 7, loss = 0.10791015625
Epoch: 0, Step: 158, Rank: 5, loss = 0.08251953125Epoch: 0, Step: 158, Rank: 4, loss = 0.08251953125Epoch: 0, Step: 158, Rank: 2, loss = 0.0771484375

Epoch: 0, Step: 158, Rank: 0, loss = 0.0888671875
Epoch: 0, Step: 158, Rank: 6, loss = 0.07275390625
^MEpoch 0: 100%|██████████| 158/158 [05:29<00:00,  1.96s/it]^[[92m{
    "epoch": 0,
    "step": 158,
    "rank": 0,
    "overall_throughput": 89.29456828751714,
    "lr": 1.926225221073686e-05,
    "cuda_mem_allocated": 6.628194808959961,
    "cuda_malloc_retries": 0,
    "num_loss_counted_tokens": 61582,
    "batch_size": 130,
    "total_loss": 0.07830210126335617,
    "samples_seen": 20016,
    "gradnorm": 0.6640625,
    "total_samples": 20036,
    "timestamp": "2025-03-25T08:05:02.184999"
}^[[0m
^[[93mSaving model in huggingface format at: samples_20016^[[0m
/opt/app-root/lib64/python3.11/site-packages/instructlab/training/utils.py:990: UserWarning: Adding architectures to ckpt: ['GraniteForCausalLM']

...<snip>...

  warnings.warn(
[08:05:26] INFO     The model is bigger than the maximum size per checkpoint (5GB)    accelerator.py:2924
                    and is going to be split in 4 checkpoint shards. You can find
                    where each parameters has been saved in the index located at
                    /tmp/tmp1zvcok9yw/model.safetensors.index.json.
^[[93mModel saved in /root/.local/share/instructlab/phased/phase1/checkpoints/hf_format/samples_20016^[[0m
[08:05:38] INFO     saving took 35.727702617645264 seconds                                   utils.py:879
^[[93mSaving full model state in /root/.local/share/instructlab/phased/phase1/checkpoints/full_state/epoch_0^[[0m
           INFO     Saving current state to                                           accelerator.py:3030
                    /root/.local/share/instructlab/phased/phase1/checkpoints/full_sta
                    te/epoch_0
           INFO     Saving FSDP model                                                 accelerator.py:3040
/opt/app-root/lib64/python3.11/site-packages/torch/distributed/fsdp/fully_sharded_data_parallel.py:690: FutureWarning: FSDP.state_dict_type() and FSDP.set_state_dict_type() are being deprecated. Please use APIs, get_state_dict() and set_state_dict(), which can support different parallelisms, FSDP1, FSDP2, DDP. API doc: https://pytorch.org/docs/stable/distributed.checkpoint.html#torch.distributed.checkpoint.state_dict.get_state_dict .Tutorial: https://pytorch.org/tutorials/recipes/distributed_checkpoint_recipe.html .
  warnings.warn(
[08:05:56] INFO     Saving model to                                                      fsdp_utils.py:88
                    /root/.local/share/instructlab/phased/phase1/checkpoints/full_state/
                    epoch_0/pytorch_model_fsdp.bin
[08:06:09] INFO     Model saved to                                                       fsdp_utils.py:90
                    /root/.local/share/instructlab/phased/phase1/checkpoints/full_state/
                    epoch_0/pytorch_model_fsdp.bin
           INFO     FSDP Model saved to output dir                                    accelerator.py:3042
                    /root/.local/share/instructlab/phased/phase1/checkpoints/full_sta
                    te/epoch_0
           INFO     Saving FSDP Optimizer                                             accelerator.py:3059

...<snip>...

[08:06:31] INFO     Saving Optimizer state to                                           fsdp_utils.py:192
                    /root/.local/share/instructlab/phased/phase1/checkpoints/full_state
                    /epoch_0/optimizer.bin
[08:06:51] INFO     Optimizer state saved in                                            fsdp_utils.py:194
                    /root/.local/share/instructlab/phased/phase1/checkpoints/full_state
                    /epoch_0/optimizer.bin
[08:06:52] INFO     FSDP Optimizer saved to output dir                                accelerator.py:3061
                    /root/.local/share/instructlab/phased/phase1/checkpoints/full_sta
                    te/epoch_0
           INFO     Scheduler state saved in                                         checkpointing.py:118
                    /root/.local/share/instructlab/phased/phase1/checkpoints/full_st
                    ate/epoch_0/scheduler.bin
           INFO     Sampler state for dataloader 0 saved in                          checkpointing.py:135
                    /root/.local/share/instructlab/phased/phase1/checkpoints/full_st
                    ate/epoch_0/sampler.bin
           INFO     Random states saved in                                           checkpointing.py:160
                    /root/.local/share/instructlab/phased/phase1/checkpoints/full_st
                    ate/epoch_0/random_states_0.pkl
^[[93mSaving training state: {'current_epoch': 0, 'samples_seen': 20016}^[[0m
^[[93mModel state saved in: /root/.local/share/instructlab/phased/phase1/checkpoints/full_state/epoch_0^[[0m

^MEpoch 1:   0%|          | 0/158 [00:00<?, ?it/s]^[[A^MEpoch 0: 100%|██████████| 158/158 [07:19<00:00,  2.78s/it]

...<snip>...

^MEpoch 6: 100%|██████████| 158/158 [05:30<00:00,  2.11s/it]^[[92m{
    "epoch": 6,
    "step": 1106,
    "rank": 0,
    "overall_throughput": 89.160686924904,
    "lr": 0.0,
    "cuda_mem_allocated": 6.644039630889893,
    "cuda_malloc_retries": 0,
    "num_loss_counted_tokens": 61829,
    "batch_size": 128,
    "total_loss": 0.04219702728493102,
    "samples_seen": 140119,
    "gradnorm": 0.361328125,
    "total_samples": 20036,
    "timestamp": "2025-03-25T08:48:02.022545"
}^[[0m
^[[93mSaving model in huggingface format at: samples_140119^[[0m
[08:48:29] INFO     The model is bigger than the maximum size per checkpoint (5GB)    accelerator.py:2924
                    and is going to be split in 4 checkpoint shards. You can find
                    where each parameters has been saved in the index located at
                    /tmp/tmpp75gs134w/model.safetensors.index.json.
^[[93mModel saved in /root/.local/share/instructlab/phased/phase1/checkpoints/hf_format/samples_140119^[[0m
[08:48:41] INFO     saving took 39.14725184440613 seconds                                    utils.py:879
^[[93mSaving full model state in /root/.local/share/instructlab/phased/phase1/checkpoints/full_state/epoch_6^[[0m
           INFO     Saving current state to                                           accelerator.py:3030
                    /root/.local/share/instructlab/phased/phase1/checkpoints/full_sta
                    te/epoch_6
           INFO     Saving FSDP model                                                 accelerator.py:3040
/opt/app-root/lib64/python3.11/site-packages/torch/distributed/fsdp/fully_sharded_data_parallel.py:690: FutureWarning: FSDP.state_dict_type() and FSDP.set_state_dict_type() are being deprecated. Please use APIs, get_state_dict() and set_state_dict(), which can support different parallelisms, FSDP1, FSDP2, DDP. API doc: https://pytorch.org/docs/stable/distributed.checkpoint.html#torch.distributed.checkpoint.state_dict.get_state_dict .Tutorial: https://pytorch.org/tutorials/recipes/distributed_checkpoint_recipe.html .
  warnings.warn(
[08:48:54] INFO     Saving model to                                                      fsdp_utils.py:88
                    /root/.local/share/instructlab/phased/phase1/checkpoints/full_state/
                    epoch_6/pytorch_model_fsdp.bin
[08:49:04] INFO     Model saved to                                                       fsdp_utils.py:90
                    /root/.local/share/instructlab/phased/phase1/checkpoints/full_state/
                    epoch_6/pytorch_model_fsdp.bin
           INFO     FSDP Model saved to output dir                                    accelerator.py:3042
                    /root/.local/share/instructlab/phased/phase1/checkpoints/full_sta
                    te/epoch_6
           INFO     Saving FSDP Optimizer                                             accelerator.py:3059
[08:49:17] INFO     Saving Optimizer state to                                           fsdp_utils.py:192
                    /root/.local/share/instructlab/phased/phase1/checkpoints/full_state
                    /epoch_6/optimizer.bin
[08:49:39] INFO     Optimizer state saved in                                            fsdp_utils.py:194
                    /root/.local/share/instructlab/phased/phase1/checkpoints/full_state
                    /epoch_6/optimizer.bin
           INFO     FSDP Optimizer saved to output dir                                accelerator.py:3061
                    /root/.local/share/instructlab/phased/phase1/checkpoints/full_sta
                    te/epoch_6
           INFO     Scheduler state saved in                                         checkpointing.py:118
                    /root/.local/share/instructlab/phased/phase1/checkpoints/full_st
                    ate/epoch_6/scheduler.bin
           INFO     Sampler state for dataloader 0 saved in                          checkpointing.py:135
                    /root/.local/share/instructlab/phased/phase1/checkpoints/full_st
                    ate/epoch_6/sampler.bin
           INFO     Random states saved in                                           checkpointing.py:160
                    /root/.local/share/instructlab/phased/phase1/checkpoints/full_st
                    ate/epoch_6/random_states_0.pkl
^[[93mSaving training state: {'current_epoch': 6, 'samples_seen': 140119}^[[0m
^[[93mModel state saved in: /root/.local/share/instructlab/phased/phase1/checkpoints/full_state/epoch_6^[[0m
^MEpoch 6: 100%|██████████| 158/158 [07:08<00:00,  2.71s/it]

[root@rhel_ai checkpoints]#
```
* 설정 값에 따라 7번의 Epoch을 실행
* 허깅 페이스 형식의 모델 저장시의 크기가 체크포인트 별 최대 크기인 5GB보다 커서 hf_format/samples_*에 나누어서 저장됨
* 전체 모델 상태는 full_state/epoch_#에 저장됨
  + FSDP 모델은 pytorch_model_fsdp.bin
  + FSDP 최적화 상태는 optimizer.bin
  + 스케줄러 상태는 scheduler.bin
  + 데이터 로더를 위한 샘플러 상태는 scheduler.bin
  + 랜덤 상태는 random_states_#.pkl

#### 5.3.4 전체 모델로 저장된 디렉터리

```bash
ls -lh full_state/epoch_6/
```

실행 결과
```
[root@rhel_ai checkpoints]# ls -lh full_state/epoch_6/
total 46G
-rw-r--r--. 1 root root  31G Mar 25 08:49 optimizer.bin
-rw-r--r--. 1 root root  16G Mar 25 08:49 pytorch_model_fsdp.bin
-rw-r--r--. 1 root root  16K Mar 25 08:49 random_states_0.pkl
-rw-r--r--. 1 root root  16K Mar 25 08:49 random_states_1.pkl
-rw-r--r--. 1 root root  16K Mar 25 08:49 random_states_2.pkl
-rw-r--r--. 1 root root  16K Mar 25 08:49 random_states_3.pkl
-rw-r--r--. 1 root root  16K Mar 25 08:49 random_states_4.pkl
-rw-r--r--. 1 root root  16K Mar 25 08:49 random_states_5.pkl
-rw-r--r--. 1 root root  16K Mar 25 08:49 random_states_6.pkl
-rw-r--r--. 1 root root  16K Mar 25 08:49 random_states_7.pkl
-rw-r--r--. 1 root root 1000 Mar 25 08:49 scheduler.bin
-rw-r--r--. 1 root root  968 Mar 25 08:49 training_metadata.json

[root@rhel_ai checkpoints]#
```

#### 5.3.5 허깅 페이스 형식으로 저장된 모델 디렉터리

```bash
ls -lh hf_format/samples_140119/
```

실행 결과
```
[root@rhel_ai checkpoints]# ls -lh hf_format/samples_140119/
total 16G
-rw-r--r--. 1 root root  769 Mar 25 08:48 config.json
-rw-r--r--. 1 root root  140 Mar 25 08:48 generation_config.json
-rw-r--r--. 1 root root 4.7G Mar 25 08:48 model-00001-of-00004.safetensors
-rw-r--r--. 1 root root 4.7G Mar 25 08:48 model-00002-of-00004.safetensors
-rw-r--r--. 1 root root 4.7G Mar 25 08:48 model-00003-of-00004.safetensors
-rw-r--r--. 1 root root 1.3G Mar 25 08:48 model-00004-of-00004.safetensors
-rw-r--r--. 1 root root  30K Mar 25 08:48 model.safetensors.index.json
-rw-r--r--. 1 root root  742 Mar 25 08:48 special_tokens_map.json
-rw-r--r--. 1 root root 3.4M Mar 25 08:48 tokenizer.json
-rw-r--r--. 1 root root 5.3K Mar 25 08:48 tokenizer_config.json

[root@rhel_ai checkpoints]# 
```

#### 5.3.6 모델의 레이어 구성 확인

```bash
jq '.' hf_format/samples_140119/model.safetensors.index.json 
```

실행 결과
```json
{
  "metadata": {
    "total_size": 16341737472
  },
  "weight_map": {
    "model.embed_tokens.weight": "model-00001-of-00004.safetensors",
    "model.norm.weight": "model-00001-of-00004.safetensors",
    "model.layers.0.input_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.0.post_attention_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.0.mlp.up_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.0.mlp.down_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.0.self_attn.q_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.0.self_attn.k_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.0.self_attn.v_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.0.self_attn.o_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.1.input_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.1.post_attention_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.1.mlp.up_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.1.mlp.down_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.1.self_attn.q_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.1.self_attn.k_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.1.self_attn.v_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.1.self_attn.o_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.2.input_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.2.post_attention_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.2.mlp.up_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.2.mlp.down_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.2.self_attn.q_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.2.self_attn.k_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.2.self_attn.v_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.2.self_attn.o_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.3.input_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.3.post_attention_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.3.mlp.up_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.3.mlp.down_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.3.self_attn.q_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.3.self_attn.k_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.3.self_attn.v_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.3.self_attn.o_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.4.input_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.4.post_attention_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.4.mlp.up_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.4.mlp.down_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.4.self_attn.q_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.4.self_attn.k_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.4.self_attn.v_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.4.self_attn.o_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.5.input_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.5.post_attention_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.5.mlp.up_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.5.mlp.down_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.5.self_attn.q_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.5.self_attn.k_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.5.self_attn.v_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.5.self_attn.o_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.6.input_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.6.post_attention_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.6.mlp.up_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.6.mlp.down_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.6.self_attn.q_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.6.self_attn.k_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.6.self_attn.v_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.6.self_attn.o_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.7.input_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.7.post_attention_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.7.mlp.up_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.7.mlp.down_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.7.self_attn.q_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.7.self_attn.k_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.7.self_attn.v_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.7.self_attn.o_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.8.input_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.8.post_attention_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.8.mlp.up_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.8.mlp.down_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.8.self_attn.q_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.8.self_attn.k_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.8.self_attn.v_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.8.self_attn.o_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.9.input_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.9.post_attention_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.9.mlp.up_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.9.mlp.down_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.9.self_attn.q_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.9.self_attn.k_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.9.self_attn.v_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.9.self_attn.o_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.10.input_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.10.post_attention_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.10.mlp.up_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.10.mlp.down_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.10.self_attn.q_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.10.self_attn.k_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.10.self_attn.v_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.10.self_attn.o_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.11.input_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.11.post_attention_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.11.mlp.up_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.0.mlp.gate_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.1.mlp.gate_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.2.mlp.gate_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.3.mlp.gate_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.4.mlp.gate_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.5.mlp.gate_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.6.mlp.gate_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.7.mlp.gate_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.8.mlp.gate_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.9.mlp.gate_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.10.mlp.gate_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.11.mlp.gate_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.11.mlp.down_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.11.self_attn.q_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.11.self_attn.k_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.11.self_attn.v_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.11.self_attn.o_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.12.input_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.12.post_attention_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.12.mlp.up_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.12.mlp.down_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.12.self_attn.q_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.12.self_attn.k_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.12.self_attn.v_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.12.self_attn.o_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.13.input_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.13.post_attention_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.13.mlp.up_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.13.mlp.down_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.13.self_attn.q_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.13.self_attn.k_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.13.self_attn.v_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.13.self_attn.o_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.14.input_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.14.post_attention_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.14.mlp.up_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.14.mlp.down_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.14.self_attn.q_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.14.self_attn.k_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.14.self_attn.v_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.14.self_attn.o_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.15.input_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.15.post_attention_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.15.mlp.up_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.15.mlp.down_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.15.self_attn.q_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.15.self_attn.k_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.15.self_attn.v_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.15.self_attn.o_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.16.input_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.16.post_attention_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.16.mlp.up_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.16.mlp.down_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.16.self_attn.q_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.16.self_attn.k_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.16.self_attn.v_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.16.self_attn.o_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.17.input_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.17.post_attention_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.17.mlp.up_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.17.mlp.down_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.17.self_attn.q_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.17.self_attn.k_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.17.self_attn.v_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.17.self_attn.o_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.18.input_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.18.post_attention_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.18.mlp.up_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.18.mlp.down_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.18.self_attn.q_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.18.self_attn.k_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.18.self_attn.v_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.18.self_attn.o_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.19.input_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.19.post_attention_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.19.mlp.up_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.19.mlp.down_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.19.self_attn.q_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.19.self_attn.k_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.19.self_attn.v_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.19.self_attn.o_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.20.input_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.20.post_attention_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.20.mlp.up_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.20.mlp.down_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.20.self_attn.q_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.20.self_attn.k_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.20.self_attn.v_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.20.self_attn.o_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.21.input_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.21.post_attention_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.21.mlp.up_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.21.mlp.down_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.21.self_attn.q_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.21.self_attn.k_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.21.self_attn.v_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.21.self_attn.o_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.22.input_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.22.post_attention_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.22.mlp.up_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.22.mlp.down_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.22.self_attn.q_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.22.self_attn.k_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.22.self_attn.v_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.22.self_attn.o_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.23.input_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.23.post_attention_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.23.mlp.up_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.23.mlp.down_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.23.self_attn.q_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.23.self_attn.k_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.23.self_attn.v_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.23.self_attn.o_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.24.input_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.24.post_attention_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.12.mlp.gate_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.13.mlp.gate_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.14.mlp.gate_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.15.mlp.gate_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.16.mlp.gate_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.17.mlp.gate_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.18.mlp.gate_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.19.mlp.gate_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.20.mlp.gate_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.21.mlp.gate_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.22.mlp.gate_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.23.mlp.gate_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.24.mlp.up_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.24.mlp.down_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.24.self_attn.q_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.24.self_attn.k_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.24.self_attn.v_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.24.self_attn.o_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.25.input_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.25.post_attention_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.25.mlp.up_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.25.mlp.down_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.25.self_attn.q_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.25.self_attn.k_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.25.self_attn.v_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.25.self_attn.o_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.26.input_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.26.post_attention_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.26.mlp.up_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.26.mlp.down_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.26.self_attn.q_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.26.self_attn.k_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.26.self_attn.v_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.26.self_attn.o_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.27.input_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.27.post_attention_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.27.mlp.up_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.27.mlp.down_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.27.self_attn.q_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.27.self_attn.k_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.27.self_attn.v_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.27.self_attn.o_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.28.input_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.28.post_attention_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.28.mlp.up_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.28.mlp.down_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.28.self_attn.q_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.28.self_attn.k_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.28.self_attn.v_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.28.self_attn.o_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.29.input_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.29.post_attention_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.29.mlp.up_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.29.mlp.down_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.29.self_attn.q_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.29.self_attn.k_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.29.self_attn.v_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.29.self_attn.o_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.30.input_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.30.post_attention_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.30.mlp.up_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.30.mlp.down_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.30.self_attn.q_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.30.self_attn.k_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.30.self_attn.v_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.30.self_attn.o_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.31.input_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.31.post_attention_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.31.mlp.up_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.31.mlp.down_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.31.self_attn.q_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.31.self_attn.k_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.31.self_attn.v_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.31.self_attn.o_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.32.input_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.32.post_attention_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.32.mlp.up_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.32.mlp.down_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.32.self_attn.q_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.32.self_attn.k_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.32.self_attn.v_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.32.self_attn.o_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.33.input_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.33.post_attention_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.33.mlp.up_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.33.mlp.down_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.33.self_attn.q_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.33.self_attn.k_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.33.self_attn.v_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.33.self_attn.o_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.34.input_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.34.post_attention_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.34.mlp.up_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.34.mlp.down_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.34.self_attn.q_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.34.self_attn.k_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.34.self_attn.v_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.34.self_attn.o_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.35.input_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.35.post_attention_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.35.mlp.up_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.35.mlp.down_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.35.self_attn.q_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.35.self_attn.k_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.35.self_attn.v_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.35.self_attn.o_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.36.input_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.36.post_attention_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.36.mlp.up_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.24.mlp.gate_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.25.mlp.gate_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.26.mlp.gate_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.27.mlp.gate_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.28.mlp.gate_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.29.mlp.gate_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.30.mlp.gate_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.31.mlp.gate_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.32.mlp.gate_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.33.mlp.gate_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.34.mlp.gate_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.35.mlp.gate_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.36.mlp.gate_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.36.mlp.down_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.36.self_attn.q_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.36.self_attn.k_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.36.self_attn.v_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.36.self_attn.o_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.37.input_layernorm.weight": "model-00004-of-00004.safetensors",
    "model.layers.37.post_attention_layernorm.weight": "model-00004-of-00004.safetensors",
    "model.layers.37.mlp.up_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.37.mlp.down_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.37.self_attn.q_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.37.self_attn.k_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.37.self_attn.v_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.37.self_attn.o_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.38.input_layernorm.weight": "model-00004-of-00004.safetensors",
    "model.layers.38.post_attention_layernorm.weight": "model-00004-of-00004.safetensors",
    "model.layers.38.mlp.up_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.38.mlp.down_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.38.self_attn.q_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.38.self_attn.k_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.38.self_attn.v_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.38.self_attn.o_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.39.input_layernorm.weight": "model-00004-of-00004.safetensors",
    "model.layers.39.post_attention_layernorm.weight": "model-00004-of-00004.safetensors",
    "model.layers.39.mlp.up_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.39.mlp.down_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.39.self_attn.q_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.39.self_attn.k_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.39.self_attn.v_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.39.self_attn.o_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.37.mlp.gate_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.38.mlp.gate_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.39.mlp.gate_proj.weight": "model-00004-of-00004.safetensors"
  }
}
```
* 모델의 레이어는 0 ~ 39 (총 40)
<br>

### 5.4 Phase2 훈련

#### 5.4.1 Phase2 디렉터리 확인

```bash
cd ~/phased
tree -F -sh phase2
```

실행 결과
```
[root@rhel_ai phased]# tree -F -sh phase2
phase2
├── [  139]  checkpoints/
│   ├── [  21M]  full_logs_global0.log
│   ├── [ 4.0K]  full_state/
│   │   ├── [ 4.0K]  epoch_0/
│   │   │   ├── [  30G]  optimizer.bin
│   │   │   ├── [  15G]  pytorch_model_fsdp.bin
│   │   │   ├── [  16K]  random_states_0.pkl
│   │   │   ├── [  16K]  random_states_1.pkl
│   │   │   ├── [  16K]  random_states_2.pkl
│   │   │   ├── [  16K]  random_states_3.pkl
│   │   │   ├── [  16K]  random_states_4.pkl
│   │   │   ├── [  16K]  random_states_5.pkl
│   │   │   ├── [  16K]  random_states_6.pkl
│   │   │   ├── [  16K]  random_states_7.pkl
│   │   │   ├── [ 1000]  scheduler.bin
│   │   │   └── [  968]  training_metadata.json
│   │   ├── [ 4.0K]  epoch_1/
│   │   │   ├── [  30G]  optimizer.bin
│   │   │   ├── [  15G]  pytorch_model_fsdp.bin
│   │   │   ├── [  16K]  random_states_0.pkl
│   │   │   ├── [  16K]  random_states_1.pkl
│   │   │   ├── [  16K]  random_states_2.pkl
│   │   │   ├── [  16K]  random_states_3.pkl
│   │   │   ├── [  16K]  random_states_4.pkl
│   │   │   ├── [  16K]  random_states_5.pkl
│   │   │   ├── [  16K]  random_states_6.pkl
│   │   │   ├── [  16K]  random_states_7.pkl
│   │   │   ├── [ 1000]  scheduler.bin
│   │   │   └── [  968]  training_metadata.json
│   │   ├── [ 4.0K]  epoch_2/
│   │   │   ├── [  30G]  optimizer.bin
│   │   │   ├── [  15G]  pytorch_model_fsdp.bin
│   │   │   ├── [  16K]  random_states_0.pkl
│   │   │   ├── [  16K]  random_states_1.pkl
│   │   │   ├── [  16K]  random_states_2.pkl
│   │   │   ├── [  16K]  random_states_3.pkl
│   │   │   ├── [  16K]  random_states_4.pkl
│   │   │   ├── [  16K]  random_states_5.pkl
│   │   │   ├── [  16K]  random_states_6.pkl
│   │   │   ├── [  16K]  random_states_7.pkl
│   │   │   ├── [ 1000]  scheduler.bin
│   │   │   └── [  968]  training_metadata.json
│   │   ├── [ 4.0K]  epoch_3/
│   │   │   ├── [  30G]  optimizer.bin
│   │   │   ├── [  15G]  pytorch_model_fsdp.bin
│   │   │   ├── [  16K]  random_states_0.pkl
│   │   │   ├── [  16K]  random_states_1.pkl
│   │   │   ├── [  16K]  random_states_2.pkl
│   │   │   ├── [  16K]  random_states_3.pkl
│   │   │   ├── [  16K]  random_states_4.pkl
│   │   │   ├── [  16K]  random_states_5.pkl
│   │   │   ├── [  16K]  random_states_6.pkl
│   │   │   ├── [  16K]  random_states_7.pkl
│   │   │   ├── [ 1000]  scheduler.bin
│   │   │   └── [  968]  training_metadata.json
│   │   ├── [ 4.0K]  epoch_4/
│   │   │   ├── [  30G]  optimizer.bin
│   │   │   ├── [  15G]  pytorch_model_fsdp.bin
│   │   │   ├── [  16K]  random_states_0.pkl
│   │   │   ├── [  16K]  random_states_1.pkl
│   │   │   ├── [  16K]  random_states_2.pkl
│   │   │   ├── [  16K]  random_states_3.pkl
│   │   │   ├── [  16K]  random_states_4.pkl
│   │   │   ├── [  16K]  random_states_5.pkl
│   │   │   ├── [  16K]  random_states_6.pkl
│   │   │   ├── [  16K]  random_states_7.pkl
│   │   │   ├── [ 1000]  scheduler.bin
│   │   │   └── [  968]  training_metadata.json
│   │   ├── [ 4.0K]  epoch_5/
│   │   │   ├── [  30G]  optimizer.bin
│   │   │   ├── [  15G]  pytorch_model_fsdp.bin
│   │   │   ├── [  16K]  random_states_0.pkl
│   │   │   ├── [  16K]  random_states_1.pkl
│   │   │   ├── [  16K]  random_states_2.pkl
│   │   │   ├── [  16K]  random_states_3.pkl
│   │   │   ├── [  16K]  random_states_4.pkl
│   │   │   ├── [  16K]  random_states_5.pkl
│   │   │   ├── [  16K]  random_states_6.pkl
│   │   │   ├── [  16K]  random_states_7.pkl
│   │   │   ├── [ 1000]  scheduler.bin
│   │   │   └── [  968]  training_metadata.json
│   │   ├── [ 4.0K]  epoch_6/
│   │   │   ├── [  30G]  optimizer.bin
│   │   │   ├── [  15G]  pytorch_model_fsdp.bin
│   │   │   ├── [  16K]  random_states_0.pkl
│   │   │   ├── [  16K]  random_states_1.pkl
│   │   │   ├── [  16K]  random_states_2.pkl
│   │   │   ├── [  16K]  random_states_3.pkl
│   │   │   ├── [  16K]  random_states_4.pkl
│   │   │   ├── [  16K]  random_states_5.pkl
│   │   │   ├── [  16K]  random_states_6.pkl
│   │   │   ├── [  16K]  random_states_7.pkl
│   │   │   ├── [ 1000]  scheduler.bin
│   │   │   └── [  968]  training_metadata.json
│   │   ├── [ 4.0K]  epoch_7/
│   │   │   ├── [  30G]  optimizer.bin
│   │   │   ├── [  15G]  pytorch_model_fsdp.bin
│   │   │   ├── [  16K]  random_states_0.pkl
│   │   │   ├── [  16K]  random_states_1.pkl
│   │   │   ├── [  16K]  random_states_2.pkl
│   │   │   ├── [  16K]  random_states_3.pkl
│   │   │   ├── [  16K]  random_states_4.pkl
│   │   │   ├── [  16K]  random_states_5.pkl
│   │   │   ├── [  16K]  random_states_6.pkl
│   │   │   ├── [  16K]  random_states_7.pkl
│   │   │   ├── [ 1000]  scheduler.bin
│   │   │   └── [  968]  training_metadata.json
│   │   ├── [ 4.0K]  epoch_8/
│   │   │   ├── [  30G]  optimizer.bin
│   │   │   ├── [  15G]  pytorch_model_fsdp.bin
│   │   │   ├── [  16K]  random_states_0.pkl
│   │   │   ├── [  16K]  random_states_1.pkl
│   │   │   ├── [  16K]  random_states_2.pkl
│   │   │   ├── [  16K]  random_states_3.pkl
│   │   │   ├── [  16K]  random_states_4.pkl
│   │   │   ├── [  16K]  random_states_5.pkl
│   │   │   ├── [  16K]  random_states_6.pkl
│   │   │   ├── [  16K]  random_states_7.pkl
│   │   │   ├── [ 1000]  scheduler.bin
│   │   │   └── [  968]  training_metadata.json
│   │   └── [ 4.0K]  epoch_9/
│   │       ├── [  30G]  optimizer.bin
│   │       ├── [  15G]  pytorch_model_fsdp.bin
│   │       ├── [  16K]  random_states_0.pkl
│   │       ├── [  16K]  random_states_1.pkl
│   │       ├── [  16K]  random_states_2.pkl
│   │       ├── [  16K]  random_states_3.pkl
│   │       ├── [  16K]  random_states_4.pkl
│   │       ├── [  16K]  random_states_5.pkl
│   │       ├── [  16K]  random_states_6.pkl
│   │       ├── [  16K]  random_states_7.pkl
│   │       ├── [ 1000]  scheduler.bin
│   │       └── [  968]  training_metadata.json
│   ├── [ 4.0K]  hf_format/
│   │   ├── [ 4.0K]  samples_1173515/
│   │   │   ├── [  769]  config.json
│   │   │   ├── [  140]  generation_config.json
│   │   │   ├── [ 4.7G]  model-00001-of-00004.safetensors
│   │   │   ├── [ 4.6G]  model-00002-of-00004.safetensors
│   │   │   ├── [ 4.6G]  model-00003-of-00004.safetensors
│   │   │   ├── [ 1.3G]  model-00004-of-00004.safetensors
│   │   │   ├── [  29K]  model.safetensors.index.json
│   │   │   ├── [  742]  special_tokens_map.json
│   │   │   ├── [ 3.3M]  tokenizer.json
│   │   │   └── [ 5.2K]  tokenizer_config.json
│   │   ├── [ 4.0K]  samples_1564696/
│   │   │   ├── [  769]  config.json
│   │   │   ├── [  140]  generation_config.json
│   │   │   ├── [ 4.7G]  model-00001-of-00004.safetensors
│   │   │   ├── [ 4.6G]  model-00002-of-00004.safetensors
│   │   │   ├── [ 4.6G]  model-00003-of-00004.safetensors
│   │   │   ├── [ 1.3G]  model-00004-of-00004.safetensors
│   │   │   ├── [  29K]  model.safetensors.index.json
│   │   │   ├── [  742]  special_tokens_map.json
│   │   │   ├── [ 3.3M]  tokenizer.json
│   │   │   └── [ 5.2K]  tokenizer_config.json
│   │   ├── [ 4.0K]  samples_1955887/
│   │   │   ├── [  769]  config.json
│   │   │   ├── [  140]  generation_config.json
│   │   │   ├── [ 4.7G]  model-00001-of-00004.safetensors
│   │   │   ├── [ 4.6G]  model-00002-of-00004.safetensors
│   │   │   ├── [ 4.6G]  model-00003-of-00004.safetensors
│   │   │   ├── [ 1.3G]  model-00004-of-00004.safetensors
│   │   │   ├── [  29K]  model.safetensors.index.json
│   │   │   ├── [  742]  special_tokens_map.json
│   │   │   ├── [ 3.3M]  tokenizer.json
│   │   │   └── [ 5.2K]  tokenizer_config.json
│   │   ├── [ 4.0K]  samples_2347073/
│   │   │   ├── [  769]  config.json
│   │   │   ├── [  140]  generation_config.json
│   │   │   ├── [ 4.7G]  model-00001-of-00004.safetensors
│   │   │   ├── [ 4.6G]  model-00002-of-00004.safetensors
│   │   │   ├── [ 4.6G]  model-00003-of-00004.safetensors
│   │   │   ├── [ 1.3G]  model-00004-of-00004.safetensors
│   │   │   ├── [  29K]  model.safetensors.index.json
│   │   │   ├── [  742]  special_tokens_map.json
│   │   │   ├── [ 3.3M]  tokenizer.json
│   │   │   └── [ 5.2K]  tokenizer_config.json
│   │   ├── [ 4.0K]  samples_2738215/
│   │   │   ├── [  769]  config.json
│   │   │   ├── [  140]  generation_config.json
│   │   │   ├── [ 4.7G]  model-00001-of-00004.safetensors
│   │   │   ├── [ 4.6G]  model-00002-of-00004.safetensors
│   │   │   ├── [ 4.6G]  model-00003-of-00004.safetensors
│   │   │   ├── [ 1.3G]  model-00004-of-00004.safetensors
│   │   │   ├── [  29K]  model.safetensors.index.json
│   │   │   ├── [  742]  special_tokens_map.json
│   │   │   ├── [ 3.3M]  tokenizer.json
│   │   │   └── [ 5.2K]  tokenizer_config.json
│   │   ├── [ 4.0K]  samples_3129385/
│   │   │   ├── [  769]  config.json
│   │   │   ├── [  140]  generation_config.json
│   │   │   ├── [ 4.7G]  model-00001-of-00004.safetensors
│   │   │   ├── [ 4.6G]  model-00002-of-00004.safetensors
│   │   │   ├── [ 4.6G]  model-00003-of-00004.safetensors
│   │   │   ├── [ 1.3G]  model-00004-of-00004.safetensors
│   │   │   ├── [  29K]  model.safetensors.index.json
│   │   │   ├── [  742]  special_tokens_map.json
│   │   │   ├── [ 3.3M]  tokenizer.json
│   │   │   └── [ 5.2K]  tokenizer_config.json
│   │   ├── [ 4.0K]  samples_3520587/
│   │   │   ├── [  769]  config.json
│   │   │   ├── [  140]  generation_config.json
│   │   │   ├── [ 4.7G]  model-00001-of-00004.safetensors
│   │   │   ├── [ 4.6G]  model-00002-of-00004.safetensors
│   │   │   ├── [ 4.6G]  model-00003-of-00004.safetensors
│   │   │   ├── [ 1.3G]  model-00004-of-00004.safetensors
│   │   │   ├── [  29K]  model.safetensors.index.json
│   │   │   ├── [  742]  special_tokens_map.json
│   │   │   ├── [ 3.3M]  tokenizer.json
│   │   │   └── [ 5.2K]  tokenizer_config.json
│   │   ├── [ 4.0K]  samples_391127/
│   │   │   ├── [  769]  config.json
│   │   │   ├── [  140]  generation_config.json
│   │   │   ├── [ 4.7G]  model-00001-of-00004.safetensors
│   │   │   ├── [ 4.6G]  model-00002-of-00004.safetensors
│   │   │   ├── [ 4.6G]  model-00003-of-00004.safetensors
│   │   │   ├── [ 1.3G]  model-00004-of-00004.safetensors
│   │   │   ├── [  29K]  model.safetensors.index.json
│   │   │   ├── [  742]  special_tokens_map.json
│   │   │   ├── [ 3.3M]  tokenizer.json
│   │   │   └── [ 5.2K]  tokenizer_config.json
│   │   ├── [ 4.0K]  samples_3911788/
│   │   │   ├── [  769]  config.json
│   │   │   ├── [  140]  generation_config.json
│   │   │   ├── [ 4.7G]  model-00001-of-00004.safetensors
│   │   │   ├── [ 4.6G]  model-00002-of-00004.safetensors
│   │   │   ├── [ 4.6G]  model-00003-of-00004.safetensors
│   │   │   ├── [ 1.3G]  model-00004-of-00004.safetensors
│   │   │   ├── [  29K]  model.safetensors.index.json
│   │   │   ├── [  742]  special_tokens_map.json
│   │   │   ├── [ 3.3M]  tokenizer.json
│   │   │   └── [ 5.2K]  tokenizer_config.json
│   │   └── [ 4.0K]  samples_782290/
│   │       ├── [  769]  config.json
│   │       ├── [  140]  generation_config.json
│   │       ├── [ 4.7G]  model-00001-of-00004.safetensors
│   │       ├── [ 4.6G]  model-00002-of-00004.safetensors
│   │       ├── [ 4.6G]  model-00003-of-00004.safetensors
│   │       ├── [ 1.3G]  model-00004-of-00004.safetensors
│   │       ├── [  29K]  model.safetensors.index.json
│   │       ├── [  742]  special_tokens_map.json
│   │       ├── [ 3.3M]  tokenizer.json
│   │       └── [ 5.2K]  tokenizer_config.json
│   └── [ 3.7M]  training_params_and_metrics_global0.jsonl
└── [   30]  eval_cache/
    └── [   60]  mt_bench/
        ├── [ 4.0K]  model_answer/
        │   ├── [ 217K]  samples_1173515.jsonl
        │   ├── [ 210K]  samples_1564696.jsonl
        │   ├── [ 220K]  samples_1955887.jsonl
        │   ├── [ 206K]  samples_2347073.jsonl
        │   ├── [ 201K]  samples_2738215.jsonl
        │   ├── [ 208K]  samples_3129385.jsonl
        │   ├── [ 211K]  samples_3520587.jsonl
        │   ├── [ 207K]  samples_391127.jsonl
        │   ├── [ 211K]  samples_3911788.jsonl
        │   └── [ 216K]  samples_782290.jsonl
        └── [   55]  model_judgment/
            └── [ 684K]  prometheus-8x7b-v2-0_single.jsonl

27 directories, 233 files

[root@rhel_ai phased]# 
```

#### 5.4.2 훈련 패러미티 및 스텝 확인

```bash
cd phase2/checkpoints/
cat training_params_and_metrics_global0.jsonl | jq '.'
```

실행 결과
```json
{
  "script_params": {
    "model_name_or_path": "/root/.local/share/instructlab/phased/phase1/checkpoints/hf_format/samples_140119",
    "data_path": "/root/.local/share/instructlab/internal/data.jsonl",
    "output_dir": "/root/.local/share/instructlab/phased/phase2/checkpoints",
    "num_epochs": 10,
    "current_epoch": 0,
    "last_step": 0,
    "effective_batch_size": 3840,
    "learning_rate": 0.000006,
    "lr_scheduler": "cosine",
    "num_warmup_steps": 25,
    "save_samples": 0,
    "save_samples_ds": null,
    "save_last": false,
    "checkpoint_at_epoch": true,
    "accelerate_full_state_at_epoch": true,
    "log_level": "INFO",
    "seed": 42,
    "mock_data": false,
    "mock_len": 2600,
    "distributed_training_framework": "fsdp",
    "fsdp_sharding_strategy": "SHARD_GRAD_OP",
    "use_dolomite": true,
    "lora_r": 0,
    "lora_alpha": 32,
    "lora_dropout": 0.1,
    "lora_quant_bits": null,
    "lora_target_modules": [
      "q_proj",
      "k_proj",
      "v_proj",
      "o_proj"
    ],
    "max_batch_len": 60000,
    "cpu_offload_optimizer": false,
    "cpu_offload_params_fsdp": false,
    "cpu_offload_optimizer_pin_memory": false,
    "cpu_offload_optimizer_ratio": 1.0,
    "NEFTune_alpha": null,
    "chat_tmpl_path": "/opt/app-root/lib64/python3.11/site-packages/instructlab/training/chat_templates/ibm_legacy_tmpl.py",
    "disable_flash_attn": false,
    "keep_last_checkpoint_only": false
  },
  "timestamp": "2025-03-25T09:38:53.176772"
}
{
  "num_gpus": 8,
  "avg_sample_len": 1155.4535006426127,
  "effective_batch_size": 3840,
  "max_batch_len_per_gpu": 60000,
  "packing_max_batch_len": 55461,
  "grad_accum": 10,
  "num_batches": 1021,
  "avg_samples_per_batch": 383.3212536728697,
  "samples_per_gpu": 48,
  "total_samples": 391371,
  "timestamp": "2025-03-25T09:40:02.485388"
}
{
  "epoch": 0,
  "step": 1,
  "rank": 0,
  "overall_throughput": 32.91541084242962,
  "lr": 0.0,
  "cuda_mem_allocated": 9.073336601257324,
  "cuda_malloc_retries": 0,
  "num_loss_counted_tokens": 210365,
  "batch_size": 369,
  "total_loss": 0.9117866565255627,
  "samples_seen": 369,
  "gradnorm": null,
  "total_samples": 391371,
  "timestamp": "2025-03-25T09:40:38.702848"
}
{
  "epoch": 0,
  "step": 2,
  "rank": 0,
  "overall_throughput": 38.11014131803494,
  "lr": 0.0,
  "cuda_mem_allocated": 9.073464393615723,
  "cuda_malloc_retries": 0,
  "num_loss_counted_tokens": 232979,
  "batch_size": 395,
  "total_loss": 0.9488237137252714,
  "samples_seen": 764,
  "gradnorm": null,
  "total_samples": 391371,
  "timestamp": "2025-03-25T09:40:49.584257"
}

...<snip>...

{
  "epoch": 0,
  "step": 1021,
  "rank": 0,
  "overall_throughput": 34.92594247309498,
  "lr": 0.000005911952326238353,
  "cuda_mem_allocated": 12.878506183624268,
  "cuda_malloc_retries": 313,
  "num_loss_counted_tokens": 207005,
  "batch_size": 395,
  "total_loss": 0.593299678751721,
  "samples_seen": 391127,
  "gradnorm": 4.59375,
  "total_samples": 391371,
  "timestamp": "2025-03-25T12:44:01.864138"
}
{
  "epoch": 1,
  "step": 1022,
  "rank": 0,
  "overall_throughput": 38.69958262880635,
  "lr": 0.000005911952326238353,
  "cuda_mem_allocated": 12.878322124481201,
  "cuda_malloc_retries": 313,
  "num_loss_counted_tokens": 208591,
  "batch_size": 384,
  "total_loss": 0.5814248936914824,
  "samples_seen": 391511,
  "gradnorm": 4.59375,
  "total_samples": 391371,
  "timestamp": "2025-03-25T12:46:39.256442"
}

...<snip>...

{
  "epoch": 9,
  "step": 10210,
  "rank": 0,
  "overall_throughput": 39.02504585636813,
  "lr": 0.0,
  "cuda_mem_allocated": 10.956313133239746,
  "cuda_malloc_retries": 3137,
  "num_loss_counted_tokens": 196255,
  "batch_size": 389,
  "total_loss": 0.5550329927899926,
  "samples_seen": 3911788,
  "gradnorm": 5.40625,
  "total_samples": 391371,
  "timestamp": "2025-03-26T15:34:53.960374"
}
```

#### 5.4.3 로그 파일 확인

```bash
less full_logs_global0.log
```

실행 결과
```log
[root@rhel_ai checkpoints]# less full_logs_global0.log
W0325 09:38:41.087000 31326 torch/distributed/run.py:793]
W0325 09:38:41.087000 31326 torch/distributed/run.py:793] *****************************************
W0325 09:38:41.087000 31326 torch/distributed/run.py:793] Setting OMP_NUM_THREADS environment variable for each process to be 1 in default, to avoid your system being overloaded, please further tune the variable for optimal performance in your application as needed.
W0325 09:38:41.087000 31326 torch/distributed/run.py:793] *****************************************
[2025-03-25 09:38:47,464] [INFO] [real_accelerator.py:219:get_accelerator] Setting ds_accelerator to cuda (auto detect)
[2025-03-25 09:38:47,608] [INFO] [real_accelerator.py:219:get_accelerator] Setting ds_accelerator to cuda (auto detect)
[2025-03-25 09:38:47,788] [INFO] [real_accelerator.py:219:get_accelerator] Setting ds_accelerator to cuda (auto detect)
[2025-03-25 09:38:47,868] [INFO] [real_accelerator.py:219:get_accelerator] Setting ds_accelerator to cuda (auto detect)
[2025-03-25 09:38:48,079] [INFO] [real_accelerator.py:219:get_accelerator] Setting ds_accelerator to cuda (auto detect)
[2025-03-25 09:38:48,191] [INFO] [real_accelerator.py:219:get_accelerator] Setting ds_accelerator to cuda (auto detect)
[2025-03-25 09:38:48,230] [INFO] [real_accelerator.py:219:get_accelerator] Setting ds_accelerator to cuda (auto detect)
[2025-03-25 09:38:48,301] [INFO] [real_accelerator.py:219:get_accelerator] Setting ds_accelerator to cuda (auto detect)
^[[38;5;120mmodel_name_or_path: /root/.local/share/instructlab/phased/phase1/checkpoints/hf_format/samples_140119
data_path: /root/.local/share/instructlab/internal/data.jsonl
output_dir: /root/.local/share/instructlab/phased/phase2/checkpoints
num_epochs: 10
current_epoch: 0
last_step: 0
effective_batch_size: 3840
learning_rate: 6.0e-06
lr_scheduler: cosine
num_warmup_steps: 25
save_samples: 0
save_samples_ds: null
save_last: false
checkpoint_at_epoch: true
accelerate_full_state_at_epoch: true
log_level: INFO
seed: 42
mock_data: false
mock_len: 2600
distributed_training_framework: fsdp
fsdp_sharding_strategy: SHARD_GRAD_OP
use_dolomite: true
lora_r: 0
lora_alpha: 32
lora_dropout: 0.1
lora_quant_bits: null
lora_target_modules:
- q_proj
- k_proj
- v_proj
- o_proj

max_batch_len: 60000
cpu_offload_optimizer: false
cpu_offload_params_fsdp: false
cpu_offload_optimizer_pin_memory: false
cpu_offload_optimizer_ratio: 1.0
NEFTune_alpha: null
chat_tmpl_path: /opt/app-root/lib64/python3.11/site-packages/instructlab/training/chat_templates/ibm_legacy_tmpl.py
disable_flash_attn: false
keep_last_checkpoint_only: false
^[[0m
^[[92m{
    "script_params": {
        "model_name_or_path": "/root/.local/share/instructlab/phased/phase1/checkpoints/hf_format/samples_140119",
        "data_path": "/root/.local/share/instructlab/internal/data.jsonl",
        "output_dir": "/root/.local/share/instructlab/phased/phase2/checkpoints",
        "num_epochs": 10,
        "current_epoch": 0,
        "last_step": 0,
        "effective_batch_size": 3840,
        "learning_rate": 6e-06,
        "lr_scheduler": "cosine",
        "num_warmup_steps": 25,
        "save_samples": 0,
        "save_samples_ds": null,
        "save_last": false,
        "checkpoint_at_epoch": true,
        "accelerate_full_state_at_epoch": true,
        "log_level": "INFO",
        "seed": 42,
        "mock_data": false,
        "mock_len": 2600,
        "distributed_training_framework": "fsdp",
        "fsdp_sharding_strategy": "SHARD_GRAD_OP",
        "use_dolomite": true,
        "lora_r": 0,
        "lora_alpha": 32,
        "lora_dropout": 0.1,
        "lora_quant_bits": null,
        "lora_target_modules": [
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj"
        ],
        "max_batch_len": 60000,
        "cpu_offload_optimizer": false,
        "cpu_offload_params_fsdp": false,
        "cpu_offload_optimizer_pin_memory": false,
        "cpu_offload_optimizer_ratio": 1.0,
        "NEFTune_alpha": null,
        "chat_tmpl_path": "/opt/app-root/lib64/python3.11/site-packages/instructlab/training/chat_templates/ibm_legacy_tmpl.py",
        "disable_flash_attn": false,
        "keep_last_checkpoint_only": false
    },
    "timestamp": "2025-03-25T09:38:53.176772"
}^[[0m
^MGenerating train split: 0 examples [00:00, ? examples/s]^MGenerating train split: 962 examples [00:00, 6672.68 examples/s]^MGenerating train split: 1929 examples [00:00, 6935.26 examples/s]^MGenerating train split: 2940 examples [00:00, 7259.60 examples/s]^MGenerating train split: 3921 examples [00:00, 7375.47 examples/s]^MGenerating train split: 4881 examples [00:00, 7334.51 examples/s]^MGenerating train split: 5860 examples [00:00, 7403.86 examples/s]^M

...<snip>...

^[[92m{
    "num_gpus": 8,
    "avg_sample_len": 1155.4535006426127,
    "effective_batch_size": 3840,
    "max_batch_len_per_gpu": 60000,
    "packing_max_batch_len": 55461,
    "grad_accum": 10,
    "num_batches": 1021,
    "avg_samples_per_batch": 383.3212536728697,
    "samples_per_gpu": 48,
    "total_samples": 391371,
    "timestamp": "2025-03-25T09:40:02.485388"
}^[[0m

...<snip>...

Epoch: 0, Step: 1, Rank: 2, loss = 1.0625Epoch: 0, Step: 1, Rank: 5, loss = 0.8828125Epoch: 0, Step: 1, Rank: 3, loss = 0.7265625Epoch: 0, Step: 1, Rank: 1, loss = 0.75

Epoch: 0, Step: 1, Rank: 7, loss = 1.1015625

Epoch: 0, Step: 1, Rank: 0, loss = 1.015625

Epoch: 0, Step: 1, Rank: 4, loss = 0.54296875
Epoch: 0, Step: 1, Rank: 6, loss = 1.2109375
^MEpoch 0:   0%|          | 1/1021 [00:12<3:29:15, 12.31s/it]^[[92m{
    "epoch": 0,
    "step": 1,
    "rank": 0,
    "overall_throughput": 32.91541084242962,
    "lr": 0.0,
    "cuda_mem_allocated": 9.073336601257324,
    "cuda_malloc_retries": 0,
    "num_loss_counted_tokens": 210365,
    "batch_size": 369,
    "total_loss": 0.9117866565255627,
    "samples_seen": 369,
    "gradnorm": null,
    "total_samples": 391371,
    "timestamp": "2025-03-25T09:40:38.702848"
}^[[0m

...<snip>...

Epoch: 0, Step: 1021, Rank: 3, loss = 0.46484375Epoch: 0, Step: 1021, Rank: 1, loss = 0.318359375Epoch: 0, Step: 1021, Rank: 0, loss = 0.68359375Epoch: 0, Step: 1021, Rank: 5, loss = 0.81640625
Epoch: 0, Step: 1021, Rank: 4, loss = 0.322265625


Epoch: 0, Step: 1021, Rank: 2, loss = 0.4609375
Epoch: 0, Step: 1021, Rank: 7, loss = 0.74609375

Epoch: 0, Step: 1021, Rank: 6, loss = 0.93359375
^MEpoch 0: 100%|██████████| 1021/1021 [3:03:35<00:00, 10.88s/it]^[[92m{
    "epoch": 0,
    "step": 1021,
    "rank": 0,
    "overall_throughput": 34.92594247309498,
    "lr": 5.911952326238353e-06,
    "cuda_mem_allocated": 12.878506183624268,
    "cuda_malloc_retries": 313,
    "num_loss_counted_tokens": 207005,
    "batch_size": 395,
    "total_loss": 0.593299678751721,
    "samples_seen": 391127,
    "gradnorm": 4.59375,
    "total_samples": 391371,
    "timestamp": "2025-03-25T12:44:01.864138"
}^[[0m

...<snip>...

  warnings.warn(
[12:44:46] INFO     The model is bigger than the maximum size per checkpoint (5GB)    accelerator.py:2924
                    and is going to be split in 4 checkpoint shards. You can find                        
                    where each parameters has been saved in the index located at                         
                    /tmp/tmp5kd3b0llw/model.safetensors.index.json.                                      
^[[93mModel saved in /root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_391127^[[0m
[12:45:06] INFO     saving took 64.23659133911133 seconds                                    utils.py:879
^[[93mSaving full model state in /root/.local/share/instructlab/phased/phase2/checkpoints/full_state/epoch_0^[[0m
           INFO     Saving current state to                                           accelerator.py:3030
                    /root/.local/share/instructlab/phased/phase2/checkpoints/full_sta                    
                    te/epoch_0                                                                           
           INFO     Saving FSDP model                                                 accelerator.py:3040

...<snip>...

  warnings.warn(
[12:45:25] INFO     Saving model to                                                      fsdp_utils.py:88
                    /root/.local/share/instructlab/phased/phase2/checkpoints/full_state/                 
                    epoch_0/pytorch_model_fsdp.bin                                                       
[12:45:37] INFO     Model saved to                                                       fsdp_utils.py:90
                    /root/.local/share/instructlab/phased/phase2/checkpoints/full_state/                 
                    epoch_0/pytorch_model_fsdp.bin                                                       
           INFO     FSDP Model saved to output dir                                    accelerator.py:3042
                    /root/.local/share/instructlab/phased/phase2/checkpoints/full_sta                    
                    te/epoch_0                                                                           
           INFO     Saving FSDP Optimizer                                             accelerator.py:3059

...<snip>...

[12:46:01] INFO     Saving Optimizer state to                                           fsdp_utils.py:192
                    /root/.local/share/instructlab/phased/phase2/checkpoints/full_state                  
                    /epoch_0/optimizer.bin                                                               
[12:46:26] INFO     Optimizer state saved in                                            fsdp_utils.py:194
                    /root/.local/share/instructlab/phased/phase2/checkpoints/full_state                  
                    /epoch_0/optimizer.bin                                                               
[12:46:27] INFO     FSDP Optimizer saved to output dir                                accelerator.py:3061
                    /root/.local/share/instructlab/phased/phase2/checkpoints/full_sta                    
                    te/epoch_0                                                                           
           INFO     Scheduler state saved in                                         checkpointing.py:118
                    /root/.local/share/instructlab/phased/phase2/checkpoints/full_st                     
                    ate/epoch_0/scheduler.bin                                                            
           INFO     Sampler state for dataloader 0 saved in                          checkpointing.py:135
                    /root/.local/share/instructlab/phased/phase2/checkpoints/full_st                     
                    ate/epoch_0/sampler.bin                                                              
           INFO     Random states saved in                                           checkpointing.py:160
                    /root/.local/share/instructlab/phased/phase2/checkpoints/full_st                     
                    ate/epoch_0/random_states_0.pkl                                                      
 
^[[93mSaving training state: {'current_epoch': 0, 'samples_seen': 391127}^[[0m
^[[93mModel state saved in: /root/.local/share/instructlab/phased/phase2/checkpoints/full_state/epoch_0^[[0m

^MEpoch 1:   0%|          | 0/1021 [00:00<?, ?it/s]^[[A^MEpoch 0: 100%|██████████| 1021/1021 [3:06:01<00:00, 10.93s/it]

...<snip>...

Epoch: 1, Step: 1022, Rank: 1, loss = 0.267578125Epoch: 1, Step: 1022, Rank: 3, loss = 0.447265625Epoch: 1, Step: 1022, Rank: 4, loss = 0.392578125


Epoch: 1, Step: 1022, Rank: 6, loss = 0.84765625
Epoch: 1, Step: 1022, Rank: 5, loss = 0.7109375Epoch: 1, Step: 1022, Rank: 2, loss = 0.5390625

Epoch: 1, Step: 1022, Rank: 0, loss = 0.7109375
Epoch: 1, Step: 1022, Rank: 7, loss = 0.73046875

^MEpoch 1:   0%|          | 1/1021 [00:11<3:14:52, 11.46s/it]^[[A^[[92m{
    "epoch": 1,
    "step": 1022,
    "rank": 0,
    "overall_throughput": 38.69958262880635,
    "lr": 5.911952326238353e-06,
    "cuda_mem_allocated": 12.878322124481201,
    "cuda_malloc_retries": 313,
    "num_loss_counted_tokens": 208591,
    "batch_size": 384,
    "total_loss": 0.5814248936914824,
    "samples_seen": 391511,
    "gradnorm": 4.59375,
    "total_samples": 391371,
    "timestamp": "2025-03-25T12:46:39.256442"
}^[[0m

...<snip>...

Epoch: 2, Step: 3063, Rank: 2, loss = 0.3046875
^MEpoch 2: 100%|██████████| 1021/1021 [3:04:36<00:00, 10.90s/it]^[[92m{
    "epoch": 2,
    "step": 3063,
    "rank": 0,
    "overall_throughput": 36.48562641696131,
    "lr": 4.896772240253655e-06,
    "cuda_mem_allocated": 12.876306056976318,
    "cuda_malloc_retries": 949,
    "num_loss_counted_tokens": 196845,
    "batch_size": 377,
    "total_loss": 0.561822753943458,
    "samples_seen": 1173515,
    "gradnorm": 21.0,
    "total_samples": 391371,
    "timestamp": "2025-03-25T18:57:09.430483"
}^[[0m
^[[93mSaving model in huggingface format at: samples_1173515^[[0m
[18:57:52] INFO     The model is bigger than the maximum size per checkpoint (5GB)    accelerator.py:2924
                    and is going to be split in 4 checkpoint shards. You can find                        
                    where each parameters has been saved in the index located at                         
                    /tmp/tmpee9aof25w/model.safetensors.index.json.                                      
^[[93mModel saved in /root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_1173515^[[0m
[18:58:15] INFO     saving took 65.1960723400116 seconds                                     utils.py:879
^[[93mSaving full model state in /root/.local/share/instructlab/phased/phase2/checkpoints/full_state/epoch_2^[[0m
           INFO     Saving current state to                                           accelerator.py:3030
                    /root/.local/share/instructlab/phased/phase2/checkpoints/full_sta                    
                    te/epoch_2                                                                                    
           INFO     Saving FSDP model                             

...<snip>...

  warnings.warn(
[18:58:36] INFO     Saving model to                                                      fsdp_utils.py:88
                    /root/.local/share/instructlab/phased/phase2/checkpoints/full_state/                 
                    epoch_2/pytorch_model_fsdp.bin                                                       
[18:58:49] INFO     Model saved to                                                       fsdp_utils.py:90
                    /root/.local/share/instructlab/phased/phase2/checkpoints/full_state/                 
                    epoch_2/pytorch_model_fsdp.bin                                                       
[18:58:50] INFO     FSDP Model saved to output dir                                    accelerator.py:3042
                    /root/.local/share/instructlab/phased/phase2/checkpoints/full_sta                    
                    te/epoch_2                                                                           
           INFO     Saving FSDP Optimizer                                             accelerator.py:3059

...<snip>...

[18:59:14] INFO     Saving Optimizer state to                                           fsdp_utils.py:192
                    /root/.local/share/instructlab/phased/phase2/checkpoints/full_state                  
                    /epoch_2/optimizer.bin                                                               
[18:59:39] INFO     Optimizer state saved in                                            fsdp_utils.py:194
                    /root/.local/share/instructlab/phased/phase2/checkpoints/full_state                  
                    /epoch_2/optimizer.bin                                                               
[18:59:40] INFO     FSDP Optimizer saved to output dir                                accelerator.py:3061
                    /root/.local/share/instructlab/phased/phase2/checkpoints/full_sta                    
                    te/epoch_2                                                                           
           INFO     Scheduler state saved in                                         checkpointing.py:118
                    /root/.local/share/instructlab/phased/phase2/checkpoints/full_st                     
                    ate/epoch_2/scheduler.bin                                                            
           INFO     Sampler state for dataloader 0 saved in                          checkpointing.py:135
                    /root/.local/share/instructlab/phased/phase2/checkpoints/full_st                     
                    ate/epoch_2/sampler.bin                                                              
           INFO     Random states saved in                                           checkpointing.py:160
                    /root/.local/share/instructlab/phased/phase2/checkpoints/full_st                     
                    ate/epoch_2/random_states_0.pkl                                                      
^[[93mSaving training state: {'current_epoch': 2, 'samples_seen': 1173515}^[[0m
^[[93mModel state saved in: /root/.local/share/instructlab/phased/phase2/checkpoints/full_state/epoch_2^[[0m

...<snip>...

^MEpoch 9: 100%|██████████| 1021/1021 [2:51:04<00:00, 10.07s/it]^[[A^[[92m{
    "epoch": 9,
    "step": 10210,
    "rank": 0,
    "overall_throughput": 39.02504585636813,
    "lr": 0.0,
    "cuda_mem_allocated": 10.956313133239746,
    "cuda_malloc_retries": 3137,
    "num_loss_counted_tokens": 196255,
    "batch_size": 389,
    "total_loss": 0.5550329927899926,
    "samples_seen": 3911788,
    "gradnorm": 5.40625,
    "total_samples": 391371,
    "timestamp": "2025-03-26T15:34:53.960374"
}^[[0m
^[[93mSaving model in huggingface format at: samples_3911788^[[0m
[15:35:23] INFO     The model is bigger than the maximum size per checkpoint (5GB)    accelerator.py:2924
                    and is going to be split in 4 checkpoint shards. You can find                        
                    where each parameters has been saved in the index located at                         
                    /tmp/tmpeuunbc_qw/model.safetensors.index.json.                                      
^[[93mModel saved in /root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_3911788^[[0m
[15:35:39] INFO     saving took 44.86404585838318 seconds                                    utils.py:879
^[[93mSaving full model state in /root/.local/share/instructlab/phased/phase2/checkpoints/full_state/epoch_9^[[0m
           INFO     Saving current state to                                           accelerator.py:3030
                    /root/.local/share/instructlab/phased/phase2/checkpoints/full_sta                    
                    te/epoch_9                                                                           
           INFO     Saving FSDP model                                                 accelerator.py:3040

...<snip>...

  warnings.warn(
[15:35:54] INFO     Saving model to                                                      fsdp_utils.py:88
                    /root/.local/share/instructlab/phased/phase2/checkpoints/full_state/                 
                    epoch_9/pytorch_model_fsdp.bin                                                       
[15:36:05] INFO     Model saved to                                                       fsdp_utils.py:90
                    /root/.local/share/instructlab/phased/phase2/checkpoints/full_state/                 
                    epoch_9/pytorch_model_fsdp.bin                                                       
           INFO     FSDP Model saved to output dir                                    accelerator.py:3042
                    /root/.local/share/instructlab/phased/phase2/checkpoints/full_sta                    
                    te/epoch_9                                                                           
           INFO     Saving FSDP Optimizer                                             accelerator.py:3059
[15:36:21] INFO     Saving Optimizer state to                                           fsdp_utils.py:192
                    /root/.local/share/instructlab/phased/phase2/checkpoints/full_state                  
                    /epoch_9/optimizer.bin                                                               
[15:36:42] INFO     Optimizer state saved in                                            fsdp_utils.py:194
                    /root/.local/share/instructlab/phased/phase2/checkpoints/full_state                  
                    /epoch_9/optimizer.bin                                                               
[15:36:43] INFO     FSDP Optimizer saved to output dir                                accelerator.py:3061
                    /root/.local/share/instructlab/phased/phase2/checkpoints/full_sta                    
                    te/epoch_9                                                                           
           INFO     Scheduler state saved in                                         checkpointing.py:118
                    /root/.local/share/instructlab/phased/phase2/checkpoints/full_st                     
                    ate/epoch_9/scheduler.bin                                                         
           INFO     Sampler state for dataloader 0 saved in                          checkpointing.py:135
                    /root/.local/share/instructlab/phased/phase2/checkpoints/full_st                     
                    ate/epoch_9/sampler.bin                                                              
           INFO     Random states saved in                                           checkpointing.py:160
                    /root/.local/share/instructlab/phased/phase2/checkpoints/full_st                     
                    ate/epoch_9/random_states_0.pkl                                                      
^[[93mSaving training state: {'current_epoch': 9, 'samples_seen': 3911788}^[[0m
^[[93mModel state saved in: /root/.local/share/instructlab/phased/phase2/checkpoints/full_state/epoch_9^[[0m
^MEpoch 9: 100%|██████████| 1021/1021 [2:52:54<00:00, 10.16s/it]

[root@rhel_ai checkpoints]#
```
* 설정 값에 따라 10번의 Epoch을 실행
* 허깅 페이스 형식의 모델 저장시의 크기가 체크포인트 별 최대 크기인 5GB보다 커서 hf_format/samples_*에 나누어서 저장됨
* 전체 모델 상태는 full_state/epoch_#에 저장됨
  + FSDP 모델은 pytorch_model_fsdp.bin
  + FSDP 최적화 상태는 optimizer.bin
  + 스케줄러 상태는 scheduler.bin
  + 데이터 로더를 위한 샘플러 상태는 scheduler.bin
  + 랜덤 상태는 random_states_#.pkl

#### 5.4.4 전체 모델로 저장된 디렉터리

```bash
ls -lh full_state/epoch_2
```

실행 결과
```
[root@rhel_ai checkpoints]# ls -lh full_state/epoch_2/
total 46G
-rw-r--r--. 1 root root  31G Mar 25 18:59 optimizer.bin
-rw-r--r--. 1 root root  16G Mar 25 18:58 pytorch_model_fsdp.bin
-rw-r--r--. 1 root root  16K Mar 25 18:59 random_states_0.pkl
-rw-r--r--. 1 root root  16K Mar 25 18:59 random_states_1.pkl
-rw-r--r--. 1 root root  16K Mar 25 18:59 random_states_2.pkl
-rw-r--r--. 1 root root  16K Mar 25 18:59 random_states_3.pkl
-rw-r--r--. 1 root root  16K Mar 25 18:59 random_states_4.pkl
-rw-r--r--. 1 root root  16K Mar 25 18:59 random_states_5.pkl
-rw-r--r--. 1 root root  16K Mar 25 18:59 random_states_6.pkl
-rw-r--r--. 1 root root  16K Mar 25 18:59 random_states_7.pkl
-rw-r--r--. 1 root root 1000 Mar 25 18:59 scheduler.bin
-rw-r--r--. 1 root root  968 Mar 25 18:59 training_metadata.json

[root@rhel_ai checkpoints]#
```

#### 5.4.5 허깅 페이스 형식으로 저장된 모델 디렉터리

```bash
ls -lh hf_format/samples_1173515/
```

실행 결과
```
[root@rhel_ai checkpoints]# ls -lh hf_format/samples_1173515/
total 16G
-rw-r--r--. 1 root root  769 Mar 25 18:58 config.json
-rw-r--r--. 1 root root  140 Mar 25 18:58 generation_config.json
-rw-r--r--. 1 root root 4.7G Mar 25 18:58 model-00001-of-00004.safetensors
-rw-r--r--. 1 root root 4.7G Mar 25 18:58 model-00002-of-00004.safetensors
-rw-r--r--. 1 root root 4.7G Mar 25 18:58 model-00003-of-00004.safetensors
-rw-r--r--. 1 root root 1.3G Mar 25 18:58 model-00004-of-00004.safetensors
-rw-r--r--. 1 root root  30K Mar 25 18:58 model.safetensors.index.json
-rw-r--r--. 1 root root  742 Mar 25 18:58 special_tokens_map.json
-rw-r--r--. 1 root root 3.4M Mar 25 18:58 tokenizer.json
-rw-r--r--. 1 root root 5.3K Mar 25 18:58 tokenizer_config.json

[root@rhel_ai checkpoints]# 
```

#### 5.4.6 모델의 레이어 구성 확인

```bash
jq '.' hf_format/samples_1173515/model.safetensors.index.json
```

실행 결과
```json
{
  "metadata": {
    "total_size": 16341737472
  },
  "weight_map": {
    "model.embed_tokens.weight": "model-00001-of-00004.safetensors",
    "model.norm.weight": "model-00001-of-00004.safetensors",
    "model.layers.0.input_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.0.post_attention_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.0.mlp.up_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.0.mlp.down_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.0.self_attn.q_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.0.self_attn.k_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.0.self_attn.v_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.0.self_attn.o_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.1.input_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.1.post_attention_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.1.mlp.up_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.1.mlp.down_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.1.self_attn.q_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.1.self_attn.k_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.1.self_attn.v_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.1.self_attn.o_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.2.input_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.2.post_attention_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.2.mlp.up_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.2.mlp.down_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.2.self_attn.q_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.2.self_attn.k_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.2.self_attn.v_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.2.self_attn.o_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.3.input_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.3.post_attention_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.3.mlp.up_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.3.mlp.down_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.3.self_attn.q_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.3.self_attn.k_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.3.self_attn.v_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.3.self_attn.o_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.4.input_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.4.post_attention_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.4.mlp.up_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.4.mlp.down_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.4.self_attn.q_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.4.self_attn.k_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.4.self_attn.v_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.4.self_attn.o_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.5.input_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.5.post_attention_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.5.mlp.up_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.5.mlp.down_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.5.self_attn.q_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.5.self_attn.k_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.5.self_attn.v_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.5.self_attn.o_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.6.input_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.6.post_attention_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.6.mlp.up_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.6.mlp.down_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.6.self_attn.q_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.6.self_attn.k_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.6.self_attn.v_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.6.self_attn.o_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.7.input_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.7.post_attention_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.7.mlp.up_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.7.mlp.down_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.7.self_attn.q_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.7.self_attn.k_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.7.self_attn.v_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.7.self_attn.o_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.8.input_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.8.post_attention_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.8.mlp.up_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.8.mlp.down_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.8.self_attn.q_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.8.self_attn.k_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.8.self_attn.v_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.8.self_attn.o_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.9.input_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.9.post_attention_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.9.mlp.up_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.9.mlp.down_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.9.self_attn.q_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.9.self_attn.k_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.9.self_attn.v_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.9.self_attn.o_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.10.input_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.10.post_attention_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.10.mlp.up_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.10.mlp.down_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.10.self_attn.q_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.10.self_attn.k_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.10.self_attn.v_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.10.self_attn.o_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.11.input_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.11.post_attention_layernorm.weight": "model-00001-of-00004.safetensors",
    "model.layers.11.mlp.up_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.0.mlp.gate_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.1.mlp.gate_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.2.mlp.gate_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.3.mlp.gate_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.4.mlp.gate_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.5.mlp.gate_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.6.mlp.gate_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.7.mlp.gate_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.8.mlp.gate_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.9.mlp.gate_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.10.mlp.gate_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.11.mlp.gate_proj.weight": "model-00001-of-00004.safetensors",
    "model.layers.11.mlp.down_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.11.self_attn.q_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.11.self_attn.k_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.11.self_attn.v_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.11.self_attn.o_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.12.input_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.12.post_attention_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.12.mlp.up_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.12.mlp.down_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.12.self_attn.q_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.12.self_attn.k_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.12.self_attn.v_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.12.self_attn.o_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.13.input_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.13.post_attention_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.13.mlp.up_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.13.mlp.down_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.13.self_attn.q_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.13.self_attn.k_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.13.self_attn.v_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.13.self_attn.o_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.14.input_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.14.post_attention_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.14.mlp.up_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.14.mlp.down_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.14.self_attn.q_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.14.self_attn.k_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.14.self_attn.v_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.14.self_attn.o_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.15.input_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.15.post_attention_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.15.mlp.up_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.15.mlp.down_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.15.self_attn.q_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.15.self_attn.k_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.15.self_attn.v_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.15.self_attn.o_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.16.input_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.16.post_attention_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.16.mlp.up_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.16.mlp.down_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.16.self_attn.q_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.16.self_attn.k_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.16.self_attn.v_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.16.self_attn.o_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.17.input_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.17.post_attention_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.17.mlp.up_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.17.mlp.down_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.17.self_attn.q_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.17.self_attn.k_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.17.self_attn.v_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.17.self_attn.o_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.18.input_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.18.post_attention_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.18.mlp.up_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.18.mlp.down_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.18.self_attn.q_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.18.self_attn.k_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.18.self_attn.v_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.18.self_attn.o_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.19.input_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.19.post_attention_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.19.mlp.up_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.19.mlp.down_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.19.self_attn.q_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.19.self_attn.k_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.19.self_attn.v_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.19.self_attn.o_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.20.input_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.20.post_attention_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.20.mlp.up_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.20.mlp.down_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.20.self_attn.q_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.20.self_attn.k_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.20.self_attn.v_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.20.self_attn.o_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.21.input_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.21.post_attention_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.21.mlp.up_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.21.mlp.down_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.21.self_attn.q_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.21.self_attn.k_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.21.self_attn.v_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.21.self_attn.o_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.22.input_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.22.post_attention_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.22.mlp.up_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.22.mlp.down_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.22.self_attn.q_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.22.self_attn.k_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.22.self_attn.v_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.22.self_attn.o_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.23.input_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.23.post_attention_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.23.mlp.up_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.23.mlp.down_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.23.self_attn.q_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.23.self_attn.k_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.23.self_attn.v_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.23.self_attn.o_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.24.input_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.24.post_attention_layernorm.weight": "model-00002-of-00004.safetensors",
    "model.layers.12.mlp.gate_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.13.mlp.gate_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.14.mlp.gate_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.15.mlp.gate_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.16.mlp.gate_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.17.mlp.gate_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.18.mlp.gate_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.19.mlp.gate_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.20.mlp.gate_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.21.mlp.gate_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.22.mlp.gate_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.23.mlp.gate_proj.weight": "model-00002-of-00004.safetensors",
    "model.layers.24.mlp.up_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.24.mlp.down_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.24.self_attn.q_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.24.self_attn.k_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.24.self_attn.v_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.24.self_attn.o_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.25.input_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.25.post_attention_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.25.mlp.up_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.25.mlp.down_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.25.self_attn.q_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.25.self_attn.k_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.25.self_attn.v_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.25.self_attn.o_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.26.input_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.26.post_attention_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.26.mlp.up_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.26.mlp.down_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.26.self_attn.q_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.26.self_attn.k_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.26.self_attn.v_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.26.self_attn.o_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.27.input_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.27.post_attention_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.27.mlp.up_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.27.mlp.down_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.27.self_attn.q_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.27.self_attn.k_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.27.self_attn.v_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.27.self_attn.o_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.28.input_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.28.post_attention_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.28.mlp.up_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.28.mlp.down_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.28.self_attn.q_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.28.self_attn.k_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.28.self_attn.v_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.28.self_attn.o_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.29.input_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.29.post_attention_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.29.mlp.up_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.29.mlp.down_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.29.self_attn.q_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.29.self_attn.k_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.29.self_attn.v_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.29.self_attn.o_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.30.input_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.30.post_attention_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.30.mlp.up_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.30.mlp.down_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.30.self_attn.q_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.30.self_attn.k_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.30.self_attn.v_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.30.self_attn.o_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.31.input_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.31.post_attention_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.31.mlp.up_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.31.mlp.down_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.31.self_attn.q_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.31.self_attn.k_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.31.self_attn.v_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.31.self_attn.o_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.32.input_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.32.post_attention_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.32.mlp.up_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.32.mlp.down_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.32.self_attn.q_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.32.self_attn.k_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.32.self_attn.v_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.32.self_attn.o_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.33.input_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.33.post_attention_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.33.mlp.up_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.33.mlp.down_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.33.self_attn.q_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.33.self_attn.k_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.33.self_attn.v_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.33.self_attn.o_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.34.input_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.34.post_attention_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.34.mlp.up_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.34.mlp.down_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.34.self_attn.q_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.34.self_attn.k_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.34.self_attn.v_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.34.self_attn.o_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.35.input_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.35.post_attention_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.35.mlp.up_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.35.mlp.down_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.35.self_attn.q_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.35.self_attn.k_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.35.self_attn.v_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.35.self_attn.o_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.36.input_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.36.post_attention_layernorm.weight": "model-00003-of-00004.safetensors",
    "model.layers.36.mlp.up_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.24.mlp.gate_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.25.mlp.gate_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.26.mlp.gate_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.27.mlp.gate_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.28.mlp.gate_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.29.mlp.gate_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.30.mlp.gate_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.31.mlp.gate_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.32.mlp.gate_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.33.mlp.gate_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.34.mlp.gate_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.35.mlp.gate_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.36.mlp.gate_proj.weight": "model-00003-of-00004.safetensors",
    "model.layers.36.mlp.down_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.36.self_attn.q_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.36.self_attn.k_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.36.self_attn.v_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.36.self_attn.o_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.37.input_layernorm.weight": "model-00004-of-00004.safetensors",
    "model.layers.37.post_attention_layernorm.weight": "model-00004-of-00004.safetensors",
    "model.layers.37.mlp.up_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.37.mlp.down_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.37.self_attn.q_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.37.self_attn.k_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.37.self_attn.v_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.37.self_attn.o_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.38.input_layernorm.weight": "model-00004-of-00004.safetensors",
    "model.layers.38.post_attention_layernorm.weight": "model-00004-of-00004.safetensors",
    "model.layers.38.mlp.up_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.38.mlp.down_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.38.self_attn.q_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.38.self_attn.k_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.38.self_attn.v_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.38.self_attn.o_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.39.input_layernorm.weight": "model-00004-of-00004.safetensors",
    "model.layers.39.post_attention_layernorm.weight": "model-00004-of-00004.safetensors",
    "model.layers.39.mlp.up_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.39.mlp.down_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.39.self_attn.q_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.39.self_attn.k_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.39.self_attn.v_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.39.self_attn.o_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.37.mlp.gate_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.38.mlp.gate_proj.weight": "model-00004-of-00004.safetensors",
    "model.layers.39.mlp.gate_proj.weight": "model-00004-of-00004.safetensors"
  }
}
```
* 모델의 레이어는 0 ~ 39 (총 40)
<br>

### 5.5 모델 평가

#### 5.5.1 모델 평가 디렉터리 확인

실행 명령어
```bash
tree -F -sh eval_cache/
```

실행 결과
```
[root@rhel_ai phase2]# tree -F -sh eval_cache/
eval_cache/
└── [   60]  mt_bench/
    ├── [ 4.0K]  model_answer/
    │   ├── [ 217K]  samples_1173515.jsonl
    │   ├── [ 210K]  samples_1564696.jsonl
    │   ├── [ 220K]  samples_1955887.jsonl
    │   ├── [ 206K]  samples_2347073.jsonl
    │   ├── [ 201K]  samples_2738215.jsonl
    │   ├── [ 208K]  samples_3129385.jsonl
    │   ├── [ 211K]  samples_3520587.jsonl
    │   ├── [ 207K]  samples_391127.jsonl
    │   ├── [ 211K]  samples_3911788.jsonl
    │   └── [ 216K]  samples_782290.jsonl
    └── [   55]  model_judgment/
        └── [ 684K]  prometheus-8x7b-v2-0_single.jsonl

3 directories, 11 files

[root@rhel_ai phase2]# 
```

#### 5.5.2 모델 평가 데이터 확인

평가 항목 확인
```bash
cat eval_cache/mt_bench/model_judgment/prometheus-8x7b-v2-0_single.jsonl | jq -cs '.|first' | jq '.'
```

```json
{
  "question_id": 107,
  "model": "samples_3129385",
  "judge": [
    "prometheus-8x7b-v2-0",
    "single-math-v1"
  ],
  "user_prompt": "[Instruction]\nPlease act as an impartial judge and evaluate the quality of the response provided by an AI assistant to the user question displayed below. Your evaluation should consider correctness and helpfulness. You will be given a reference answer and the assistant's answer. Begin your evaluation by comparing the assistant's answer with the reference answer. Identify and correct any mistakes. Be as objective as possible. After providing your explanation, you must rate the response on a scale of 1 to 10 by strictly following this format: \"[[rating]]\", for example: \"Rating: [[5]]\".\n\n[Question]\nA is the father of B. B is the father of C. What is the relationship between A and C?\n\n[The Start of Reference Answer]\nA is the grandfather of C.\n[The End of Reference Answer]\n\n[The Start of Assistant's Answer]\nA is the grandfather of C.\n[The End of Assistant's Answer]",
  "judgment": " The assistant's answer is identical to the reference answer, and it correctly identifies the relationship between A and C as \"grandfather.\" The answer is accurate and helpful, providing the user with the information they need to understand the familial relationship in question. Therefore, the assistant's response is of high quality.\n\nRating: [[10]]",
  "score": 10,
  "turn": 1,
  "tstamp": 1743005961.5141597
}
```

평가를 위한 모델 확인
```bash
cat eval_cache/mt_bench/model_judgment/prometheus-8x7b-v2-0_single.jsonl | jq '.'
```

실행 결과
```
[root@rhel_ai phase2]# cat eval_cache/mt_bench/model_judgment/prometheus-8x7b-v2-0_single.jsonl | jq -r '.judge[]' | sort -u
prometheus-8x7b-v2-0
single-math-v1
single-math-v1-multi-turn
single-v1
single-v1-multi-turn

[root@rhel_ai phase2]#
```

#### 5.5.3 최고 점수를 받은 샘플의 평가 확인

실행 명령어 - 평가 리스트 확인
```bash
cat eval_cache/mt_bench/model_answer/samples_1173515.jsonl | jq -cs '.|length'
```

실행 결과
```
[root@rhel_ai phase2]# cat eval_cache/mt_bench/model_answer/samples_1173515.jsonl | jq -cs '.|length'
80

[root@rhel_ai phase2]#
```

평가 항목 확인

```bash
cat eval_cache/mt_bench/model_answer/samples_1173515.jsonl | jq -cs '.|first'| jq '.'
```

```json
{
  "question_id": 81,
  "answer_id": "ipBguoxd6A2xaoomDvLSYS",
  "model_id": "samples_1173515",
  "choices": [
    {
      "index": 0,
      "turns": [
        "Title: A Cultural Journey Through the Aloha State: My Recent Trip to Hawaii\n\nAs a travel enthusiast, I've had the privilege of exploring various corners of the globe, but there's something truly special about Hawaii. This tropical paradise offers more than just stunning beaches and crystal-clear waters; it's a melting pot of cultures that leaves a lasting impression on every visitor. Here's a glimpse into my recent trip to the Aloha State, focusing on cultural experiences and must-see attractions.\n\nMy journey began in Honolulu, the capital city of Hawaii. The historical significance of this place is evident from the moment you step off the plane. I was greeted by the warm smiles of local hula dancers, who welcomed me with a traditional song and dance. This vibrant cultural display set the tone for the entire trip.\n\nOne of the highlights of my visit was the Hawaiian National Museum of Natural History. This museum offers a comprehensive overview of Hawaii's rich history, from its geological formation to the arrival of Polynesian settlers. The museum's exhibits are engaging and informative, providing valuable insights into the unique biodiversity of the islands.\n\nAnother must-see attraction is the Pearl Harbor National Memorial. This historic site commemorates the events of December 7, 1941, and offers a poignant reminder of the sacrifices made by those who served in World War II. The museum's exhibits are well-curated, and the guided tour provides a deep understanding of the events that unfolded on that fateful day.\n\nNo trip to Hawaii would be complete without experiencing a traditional Hawaiian luau. I had the opportunity to attend a luau at the Polynesian Cultural Center, where I was treated to a feast of local dishes, including poi, kalua pork, and lomi lomi salmon. The show featured talented hula dancers and musicians, who performed traditional dances and songs that showcased the island's rich cultural heritage.\n\nI also had the chance to visit the Dole Plantation on Oahu. This historic site offers a fascinating glimpse into Hawaii's pineapple industry and provides a unique opportunity to learn about the island's agricultural history. The plantation's famous Pineapple Express train is a fun way to explore the grounds and learn about the history of Hawaii's pineapple industry.\n\nFinally, I made my way to the Big Island, where I visited the Mauna Kea Observatories. This world-renowned astronomical research facility offers stunning views of the night sky and provides a unique opportunity to learn about the universe from experts in the field. The observatories' tours are informative and engaging, and the view of the stars from the summit is truly breathtaking.\n\nIn conclusion, Hawaii is a destination that offers a rich cultural experience that goes beyond the beaches and the surf. From the historical sites and museums to the traditional luaus and astronomical research facilities, there's something for everyone in this tropical paradise. So, if you're looking for a unique and enriching travel experience, consider visiting Hawaii and immersing yourself in the rich cultural heritage of this beautiful island state.",
        "Aloha, fellow travelers! I recently embarked on a journey to the Aloha State, Hawaii, and I can't wait to share my cultural experiences and must-see attractions with you. Here's a glimpse into my recent trip, starting with the letter A:\n\nAloha! My journey began in Honolulu, the capital city of Hawaii, where I was greeted by the warm smiles of local hula dancers. Their traditional song and dance set the tone for the entire trip, showcasing the island's rich cultural heritage.\n\nAloha! The Hawaiian National Museum of Natural History was a highlight of my visit. The museum offers a comprehensive overview of Hawaii's rich history, from its geological formation to the arrival of Polynesian settlers. The exhibits are engaging and informative, providing valuable insights into the unique biodiversity of the islands.\n\nAloha! The Pearl Harbor National Memorial was another must-see attraction. This historic site commemorates the events of December 7, 1941, and offers a poignant reminder of the sacrifices made by those who served in World War II. The museum's exhibits are well-curated, and the guided tour provides a deep understanding of the events that unfolded on that fateful day.\n\nAloha! I had the opportunity to attend a traditional Hawaiian luau at the Polynesian Cultural Center. The feast of local dishes, including poi, kalua pork, and lomi lomi salmon, was delicious. The show featured talented hula dancers and musicians, who performed traditional dances and songs that showcased the island's rich cultural heritage.\n\nAloha! I visited the Dole Plantation on Oahu, where I learned about Hawaii's pineapple industry and agricultural history. The plantation's famous Pineapple Express train is a fun way to explore the grounds and learn about the history of Hawaii's pineapple industry.\n\nAloha! Finally, I made my way to the Big Island, where I visited the Mauna Kea Observatories. This world-renowned astronomical research facility offers stunning views of the night sky and provides a unique opportunity to learn about the universe from experts in the field. The observatories' tours are informative and engaging, and the view of the stars from the summit is truly breathtaking.\n\nIn conclusion, Hawaii is a destination that offers a rich cultural experience that goes beyond the beaches and the surf. From the historical sites and museums to the traditional luaus and astronomical research facilities, there's something for everyone in this tropical paradise. So, if you're looking for a unique and enriching travel experience, consider visiting Hawaii and immersing yourself in the rich cultural heritage of this beautiful island state."
      ]
    }
  ],
  "tstamp": 1743004596.2893703
}
```

### 5.6 모델 훈련 결과 확인

실행 명령어 
```bash
yq -y '.' ~/phased/journalfile.yaml
```

실행 결과
```yaml
current_phase: done
ended_at_utc: '2025-03-26 16:19:58.143636+00:00'
eval_1: null
eval_2:
  best_checkpoint:
    checkpoint: /root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_1173515
    ended_at_utc: '2025-03-26 15:59:09.897108+00:00'
    score: 7.064102564102564
  checkpoints:
    - /root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_391127
    - /root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_782290
    - /root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_1173515
    - /root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_1564696
    - /root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_1955887
    - /root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_2347073
    - /root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_2738215
    - /root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_3129385
    - /root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_3520587
    - /root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_3911788
  ended_at_utc: '2025-03-26 16:19:58.143616+00:00'
  finished_checkpoints:
    - /root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_2738215
    - /root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_3911788
    - /root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_782290
    - /root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_391127
    - /root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_1173515
    - /root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_3520587
    - /root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_1955887
    - /root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_1564696
    - /root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_2347073
    - /root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_3129385
  results:
    - checkpoint: /root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_2738215
      ended_at_utc: '2025-03-26 15:42:06.772060+00:00'
      score: 6.791139240506329
    - checkpoint: /root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_3911788
      ended_at_utc: '2025-03-26 15:46:22.504299+00:00'
      score: 6.886075949367089
    - checkpoint: /root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_782290
      ended_at_utc: '2025-03-26 15:50:37.523268+00:00'
      score: 7.0251572327044025
    - checkpoint: /root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_391127
      ended_at_utc: '2025-03-26 15:54:51.608370+00:00'
      score: 6.841772151898734
    - checkpoint: /root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_1173515
      ended_at_utc: '2025-03-26 15:59:09.897108+00:00'
      score: 7.064102564102564
    - checkpoint: /root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_3520587
      ended_at_utc: '2025-03-26 16:03:14.089601+00:00'
      score: 6.8544303797468356
    - checkpoint: /root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_1955887
      ended_at_utc: '2025-03-26 16:07:27.620742+00:00'
      score: 6.80379746835443
    - checkpoint: /root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_1564696
      ended_at_utc: '2025-03-26 16:11:36.988901+00:00'
      score: 6.86624203821656
    - checkpoint: /root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_2347073
      ended_at_utc: '2025-03-26 16:15:45.291855+00:00'
      score: 6.8354430379746836
    - checkpoint: /root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_3129385
      ended_at_utc: '2025-03-26 16:19:58.130182+00:00'
      score: 6.962264150943396
  started_at_utc: '2025-03-26 15:36:49.555424+00:00'
final_output:
  checkpoint: /root/.local/share/instructlab/phased/phase2/checkpoints/hf_format/samples_1173515
  ended_at_utc: '2025-03-26 15:59:09.897108+00:00'
  score: 7.064102564102564
run_id: 50b85752-9689-42c6-8030-4b79f3b6e723
started_at_utc: '2025-03-25 07:56:17.431994+00:00'
train_1:
  checkpoints: /root/.local/share/instructlab/phased/phase1/checkpoints
  ended_at_utc: '2025-03-25 08:49:46.310730+00:00'
  started_at_utc: '2025-03-25 07:56:17.448552+00:00'
train_2:
  checkpoints: /root/.local/share/instructlab/phased/phase2/checkpoints
  ended_at_utc: '2025-03-26 15:36:49.510390+00:00'
  started_at_utc: '2025-03-25 08:49:46.334131+00:00'
```
<br>

### 5.7 새 모델 제공 및 채팅

#### 5.7.1 새 모델로 서비스

실행 명령어
```bash
ilab model serve --model-path ~/phased/phase2/checkpoints/hf_format/samples_1173515/
```

실행 결과
```
[root@rhel_ai ~]# ilab model serve --model-path ~/phased/phase2/checkpoints/hf_format/samples_1173515/
...<snip>...

[root@rhel_ai ~]#
```

#### 5.7.2 모델과 채팅

실행 명령어 - 신규 모델로 테스트
```bash
ilab model chat --model-path ~/phased/phase2/checkpoints/hf_format/samples_1173515/
```

실행 결과
```
[root@rhel_ai ~]# ilab model chat --model-path ~/phased/phase2/checkpoints/hf_format/samples_1173515/

INFO 2025-03-27 04:13:50,500 instructlab.model.chat:775: Requested model /root/.cache/instructlab/models/granite-3.1-8b-lab-v1 is not served by the server. Proceeding to chat with served model: /root/phased/phase2/checkpoints/hf_format/samples_1173515
╭─────────────────────────────────────────────── system ───────────────────────────────────────────────╮
│ Welcome to InstructLab Chat w/ SAMPLES_1173515 (type /h for help)                                    │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────╯
>>> 불사조 별자리는 무엇입니까?                                                             [S][default]
╭────────────────────────────────────────── samples_1173515 ───────────────────────────────────────────╮
│ 불사조 별자리는 한국인들의 문화와 신화와 근처에 대한 연결을 나타냅니다. 불사조 별자리는 북쪽으로     │
│ 삼각형 형태로는 찾고, 혹은 다른 별자리로 통합될 수 있는 다른 별자리와 함께 핫스타 형태로 찾을 수     │
│ 있습니다. 불사조 별자리의 큰 별인 불사조 별은 강한 주인의 별입니다. 불사조 별자리는 지평선이 낮은    │
│ 곳에 있습니다.                                                                                       │
╰────────────────────────────────────────────────────────────────────────────── elapsed 0.714 seconds ─╯
>>> 불사조 자리는 누가 발견했나요?                                                          [S][default]
╭────────────────────────────────────────── samples_1173515 ───────────────────────────────────────────╮
│ 불사조 별자리는 처음 1603년에 처음으로 천체 지도에 묘사된 것으로 언급되는 별자리입니다. 그는         │
│ 암스테르담의 우라노메트리아과 유럽의 천문학자인 플랑시우스 드 라카유가 처음으로 천체 지도에          │
│ 묘사했습니다.                                                                                        │
╰────────────────────────────────────────────────────────────────────────────── elapsed 0.501 seconds ─╯
>>> "불사조 새"는 무엇을 상징합니까?                                                        [S][default]
╭────────────────────────────────────────── samples_1173515 ───────────────────────────────────────────╮
│ 불사조 새는 불사조 별자리와 계절의 전환에 관련하여 고대 동화에서 사용된 기억입니다. 불사조 별자리와  │
│ 같은 별자리는 델포르트, 북유럽과 북아프리카의 공작자리, 불사조, 이북 아프리카와 같은 곳에서 관측을   │
│ 통해 이름이 붙었습니다. 불사조 새는 불사조 별자리와 같은 별자리와 관련하여 지평선이 낮은 곳에 지어져 │
│ 있으며, 봄 역사, 기운 시작, 새끼 새의 탄생 등에 상징입니다. 불사조 새는 불사조 별자리와 함께 가지고  │
│ 있으며, 이 새는 불사조 별자리와 관련하여 새끼 새의 탄생을 상징합니다.                                │
╰────────────────────────────────────────────────────────────────────────────── elapsed 1.058 seconds ─╯
>>> 피닉스 별자리를 아시나요?                                                               [S][default]
╭────────────────────────────────────────── samples_1173515 ───────────────────────────────────────────╮
│ 피닉스 별자리는 남쪽으로 삼각형 형태로 보이는 별자리입니다. 피닉스 별자리는 피닉스, 세계             │
│ 최대DataRow노뎀의 하나인 피닉스 스위프트, 에리다누스 등과 같은 다른 별자리와 통합하여 핫스타 형태로  │
│ 보입니다. 피닉스 별자리는 피닉스 삼각형의 스펙트루어 라이트가 가장 밝은 별인 알파 피닉스의           │
│ 방사점으로 구성되었습니다. 피닉스 별자리는 일반적으로 가장 밝은 별인 알파 피닉스의 방사점으로        │
│ 구성되어 있습니다. 피닉스 별자리는 중국인들이 문화과 신화와 관련하여 풍부한 별자리입니다.            │
╰────────────────────────────────────────────────────────────────────────────── elapsed 1.086 seconds ─╯
>>> exit

[root@rhel_ai ~]#
```

#### 5.7.3 기존 모델고 비교 테스트

실행 명령어
```bash
ilab model chat
```

실행 결과
```
[root@rhelai-02 ~]# ilab model chat
INFO 2025-03-27 04:20:52,004 instructlab.model.chat:775: Requested model /root/.cache/instructlab/models/granite-3.1-8b-lab-v1 is not served by the server. Proceeding to chat with served model: /root/.cache/instructlab/models/granite-3.1-8b-starter-v1
╭─────────────────────────────────────────────── system ───────────────────────────────────────────────╮
│ Welcome to InstructLab Chat w/ GRANITE-3.1-8B-STARTER-V1 (type /h for help)                          │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────╯
>>> 불사조 자리를 아니?                                                                     [S][default]
╭───────────────────────────────────── granite-3.1-8b-starter-v1 ──────────────────────────────────────╮
│ 烀                                                                                                   │
│                                                                                                      │
│ ## **Annex 4: Examples of acceptable photo identification documents**                                │
│                                                                                                      │
│ The following list provides examples of acceptable government-issued photo                           │
│                                                                                                      │
│ identification documents from federal, provincial or territorial authorities. This is not an         │
│ exhaustive list.                                                                                     │
│                                                                                                      │
│ |-|-|                                                                                                │
│ | Type of card or document | Issuing province or state and country |                                 │
│ | Canadian passport | Canada |                                                                       │
│ | Permanent resident card | Canada |                                                                 │
│ | Citizenship card (issued prior to 2012) | Canada |                                                 │
│ | Secure Certificate of Indian Status | Canada |                                                     │
│ | Driver's licences | Driver's licences |                                                            │
│ | British Columbia Driver's Licence | British Columbia, Canada |                                     │
│ | Alberta Driver's Licence | Alberta, Canada |                                                       │
│ | Saskatchewan Driver's Licence | Saskatchewan, Canada |                                             │
│ | Manitoba Driver's Licence | Manitoba, Canada |                                                     │
│ | Ontario Driver's Licence | Ontario, Canada |                                                       │
│ | Québec Driver's Licence | Québec, Canada |                                                         │
│ | New Brunswick Driver's Licence | New Brunswick, Canada |                                           │
│ | Nova Scotia Driver's Licence | Nova Scotia, Canada |                                               │
│ | Prince Edward Island Driver's Licence | Prince Edward Island, Canada |                             │
│ | Newfoundland and Labrador Driver's Licence | Newfoundland and Labrador, Canada |                   │
│ | Yukon Driver's Licence | Yukon, Canada |                                                           │
│ | Northwest Territories Driver's Licence | Northwest Territories, Canada |                           │
│ | Nunavut Driver's Licence | Nunavut, Canada |                                                       │
│ | DND 404 Driver's Licence | Department of National Defence, Canada |                                │
│ | Provincial services cards | Provincial services cards |                                            │
│                                                                                                      │
│ Why are driver's licenses from all Canadian provinces and territories, as well as the DND 404        │
│ Driver's Licence, considered valid forms of government-issued photo identification for verifying     │
│ identity in Canada?                                                                                  │
│                                                                                                      │
│ Driver's licenses from all Canadian provinces and territories, as well as the DND 404 Driver's       │
│ Licence, are considered valid forms of government-issued photo identification because they display   │
│ the holder's photo, name, and address, allowing for effective identity verification in Canada.       │
╰────────────────────────────────────────────────────────────────────────────── elapsed 2.504 seconds ─╯
>>> 불사조 별자리는 무엇입니까?                                                             [S][default]
╭───────────────────────────────────── granite-3.1-8b-starter-v1 ──────────────────────────────────────╮
│ 불사조 별자리는 아니                                                                                 │
╰────────────────────────────────────────────────────────────────────────────── elapsed 0.054 seconds ─╯
>>> 불사조 자리는 누가 발견했나요?                                                          [S][default]
╭───────────────────────────────────── granite-3.1-8b-starter-v1 ──────────────────────────────────────╮
│ 불사조 자리가 2019년 8월 22일 발�lpVtbllage                                                          │
╰────────────────────────────────────────────────────────────────────────────── elapsed 0.115 seconds ─╯
>>> exit                                                                                    [S][default]

[root@rhel_ai ~]# 
```
<br>

### 5.8 모델 업로드 

실행 명령어
```bash
ilab model upload --model samples_1173515 --destination rhk-s3-bucket --dest-type s3
```

실행 결과
```
[root@rhel_ai ~]# ilab model upload --model samples_1173515 --destination rhk-s3-bucket --dest-type s3

[root@rhel_ai ~]#
```
<br>

### 5.9 모델 양자화

#### 5.9.1 파인썬 체크

실행 명령어
```bash
python --version
pip --version
```

실행 결과
```
[root@rhel_ai ~]# python --version
Python 3.9.18

[root@rhelai-02 ~]# pip3 --version
pip 25.0.1 from /root/.local/lib/python3.9/site-packages/pip (python 3.9)

[root@rhel_ai ~]#
```

파이썬 업그레이드
```bash
rpm-ostree install python3.11 pip3-11
```
* 최소한 3.11 이상으로 업그레이드

#### 5.9.2 ***llama.cpp*** 복제

실행 명령어
```bash
cd ~/.cache/instructlab/models/
git clone https://github.com/ggerganov/llama.cpp.git
```

실행 결과
```
[root@rhel_ai ~]# cd ~/.cache/instructlab/models/

[root@rhel_ai models]# git clone https://github.com/ggerganov/llama.cpp.git
...<snip>...

[root@rhel_ai models]#
```

#### 5.9.3 필요한 패키지 설치

실행 명령어
```bash
pip3.11 install -r llama.cpp/requirements.txt 
```

실행 결과
```
[root@rhel_ai models]# pip3.11 install -r llama.cpp/requirements.txt 
...<snip>...

[root@rhel_ai models]#
```

#### 5.9.4 전환 명령어 확인

실행 명령어
```bash
python3.11 llama.cpp/convert_hf_to_gguf.py --help
```

실행 결과
```
[root@rhel_ai models]# python3.11 llama.cpp/convert_hf_to_gguf.py --help
usage: convert_hf_to_gguf.py [-h] [--vocab-only] [--outfile OUTFILE]
                             [--outtype {f32,f16,bf16,q8_0,tq1_0,tq2_0,auto}] [--bigendian]
                             [--use-temp-file] [--no-lazy] [--model-name MODEL_NAME] [--verbose]
                             [--split-max-tensors SPLIT_MAX_TENSORS] [--split-max-size SPLIT_MAX_SIZE]
                             [--dry-run] [--no-tensor-first-split] [--metadata METADATA]
                             [--print-supported-models]
                             [model]

Convert a huggingface model to a GGML compatible file

positional arguments:
  model                 directory containing model file

...<snip>...

[root@rhel_ai models]#
```

#### 5.9.5 모델 양자화

실행 명령어
```bash
python3.11 llama.cpp/convert_hf_to_gguf.py ~/phased/phase2/checkpoints/hf_format/samples_1173515/ --outfile ./rhk_sa_3.1_8b_20251505.gguf
```

실행 결과
```
[root@rhel_ai models]# python3.11 llama.cpp/convert_hf_to_gguf.py ~/phased/phase2/checkpoints/hf_format/samples_1173515/ --outfile ./rhk_sa_3.1_8b_20251505.gguf
INFO:hf-to-gguf:Loading model: samples_1173515
INFO:gguf.gguf_writer:gguf: This GGUF file is for Little Endian only
INFO:hf-to-gguf:Exporting model...
INFO:hf-to-gguf:gguf: loading model weight map from 'model.safetensors.index.json'
INFO:hf-to-gguf:gguf: loading model part 'model-00001-of-00004.safetensors'
INFO:hf-to-gguf:token_embd.weight,         torch.bfloat16 --> F16, shape = {4096, 49160}
INFO:hf-to-gguf:blk.0.attn_norm.weight,    torch.bfloat16 --> F32, shape = {4096}
INFO:hf-to-gguf:blk.0.ffn_down.weight,     torch.bfloat16 --> F16, shape = {12800, 4096}
INFO:hf-to-gguf:blk.0.ffn_gate.weight,     torch.bfloat16 --> F16, shape = {4096, 12800}
INFO:hf-to-gguf:blk.0.ffn_up.weight,       torch.bfloat16 --> F16, shape = {4096, 12800}
INFO:hf-to-gguf:blk.0.ffn_norm.weight,     torch.bfloat16 --> F32, shape = {4096}
INFO:hf-to-gguf:blk.0.attn_k.weight,       torch.bfloat16 --> F16, shape = {4096, 1024}
INFO:hf-to-gguf:blk.0.attn_output.weight,  torch.bfloat16 --> F16, shape = {4096, 4096}
INFO:hf-to-gguf:blk.0.attn_q.weight,       torch.bfloat16 --> F16, shape = {4096, 4096}
INFO:hf-to-gguf:blk.0.attn_v.weight,       torch.bfloat16 --> F16, shape = {4096, 1024}
INFO:hf-to-gguf:blk.1.attn_norm.weight,    torch.bfloat16 --> F32, shape = {4096}
INFO:hf-to-gguf:blk.1.ffn_down.weight,     torch.bfloat16 --> F16, shape = {12800, 4096}
INFO:hf-to-gguf:blk.1.ffn_gate.weight,     torch.bfloat16 --> F16, shape = {4096, 12800}
INFO:hf-to-gguf:blk.1.ffn_up.weight,       torch.bfloat16 --> F16, shape = {4096, 12800}
INFO:hf-to-gguf:blk.1.ffn_norm.weight,     torch.bfloat16 --> F32, shape = {4096}
INFO:hf-to-gguf:blk.1.attn_k.weight,       torch.bfloat16 --> F16, shape = {4096, 1024}
INFO:hf-to-gguf:blk.1.attn_output.weight,  torch.bfloat16 --> F16, shape = {4096, 4096}
INFO:hf-to-gguf:blk.1.attn_q.weight,       torch.bfloat16 --> F16, shape = {4096, 4096}
INFO:hf-to-gguf:blk.1.attn_v.weight,       torch.bfloat16 --> F16, shape = {4096, 1024}

...<snip>...

INFO:hf-to-gguf:blk.39.attn_norm.weight,   torch.bfloat16 --> F32, shape = {4096}
INFO:hf-to-gguf:blk.39.ffn_down.weight,    torch.bfloat16 --> F16, shape = {12800, 4096}
INFO:hf-to-gguf:blk.39.ffn_gate.weight,    torch.bfloat16 --> F16, shape = {4096, 12800}
INFO:hf-to-gguf:blk.39.ffn_up.weight,      torch.bfloat16 --> F16, shape = {4096, 12800}
INFO:hf-to-gguf:blk.39.ffn_norm.weight,    torch.bfloat16 --> F32, shape = {4096}
INFO:hf-to-gguf:blk.39.attn_k.weight,      torch.bfloat16 --> F16, shape = {4096, 1024}
INFO:hf-to-gguf:blk.39.attn_output.weight, torch.bfloat16 --> F16, shape = {4096, 4096}
INFO:hf-to-gguf:blk.39.attn_q.weight,      torch.bfloat16 --> F16, shape = {4096, 4096}
INFO:hf-to-gguf:blk.39.attn_v.weight,      torch.bfloat16 --> F16, shape = {4096, 1024}
INFO:hf-to-gguf:Set meta model
INFO:hf-to-gguf:Set model parameters
INFO:hf-to-gguf:gguf: context length = 131072
INFO:hf-to-gguf:gguf: embedding length = 4096
INFO:hf-to-gguf:gguf: feed forward length = 12800
INFO:hf-to-gguf:gguf: head count = 32
INFO:hf-to-gguf:gguf: key-value head count = 8
INFO:hf-to-gguf:gguf: rope theta = 10000000.0
INFO:hf-to-gguf:gguf: rms norm epsilon = 1e-05
INFO:hf-to-gguf:gguf: file type = 1
INFO:hf-to-gguf:gguf: (granite) attention_scale = 0.0078125
INFO:hf-to-gguf:gguf: (granite) embedding_scale = 12.0
INFO:hf-to-gguf:gguf: (granite) residual_scale = 0.22
INFO:hf-to-gguf:gguf: (granite) logits_scale = 16.0
INFO:hf-to-gguf:Set model tokenizer
INFO:gguf.vocab:Adding 48891 merge(s).
INFO:gguf.vocab:Setting special token type bos to 49152
INFO:gguf.vocab:Setting special token type eos to 0
INFO:gguf.vocab:Setting special token type unk to 0
INFO:gguf.vocab:Setting special token type pad to 49153
INFO:gguf.vocab:Setting chat_template to {% for message in messages %}{% if message['role'] == 'pretraining' %}{{'<|pretrain|>' + message['content'] + '<|endoftext|>' + '<|/pretrain|>' }}{% elif message['role'] == 'system' %}{{'<|system|>'+ '
' + message['content'] + '
'}}{% elif message['role'] == 'user' %}{{'<|user|>' + '
' + message['content'] + '
'}}{% elif message['role'] == 'assistant' %}{{'<|assistant|>' + '
' + message['content'] + '<|endoftext|>' + ('' if loop.last else '
')}}{% endif %}{% if loop.last and add_generation_prompt %}{{ '<|assistant|>' + '
' }}{% endif %}{% endfor %}
INFO:hf-to-gguf:Set model quantization version
INFO:gguf.gguf_writer:Writing the following files:
INFO:gguf.gguf_writer:rhk_sa_3.1_8b_20251505.gguf: n_tensors = 362, total_size = 16.3G
Writing: 100%|███████████████████████████████████████████████████| 16.3G/16.3G [00:34<00:00, 479Mbyte/s]
INFO:hf-to-gguf:Model successfully exported to rhk_sa_3.1_8b_20251505.gguf

[root@rhel_ai models]# ls -lh *.gguf
-rw-r--r--. 1 root root 16G Mar 27 06:06 rhk_sa_3.1_8b_20251505.gguf

[root@rhel_ai models]#
```
<br>
<br>

------
[차례](../README.md)