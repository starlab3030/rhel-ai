# 오픈시프트 상에서 Kubeflow Trainer를 사용하여 LLM Fine-Tuning

**목차**
1. []()<br>
2. []()<br>
3. []()<br>
4. []()<br>

## 1. 개요

### 1.1 LLM과 레드햇 오픈시프트 AI

대규모 언어 모델(LLM)은 여전히 ​​집중적인 연구 분야이며, 새로운 산업으로 빠르게 확산되고 있습니다. 여러 기업에서 매주 새로운 학술 논문과 업데이트된 오픈 모델이 발표되면서 기존 폐쇄형 소스 모델과의 격차를 줄이고 있습니다. 오픈 소스 커뮤니티 덕분에 인기 프로젝트에 새로운 모델과 혁신이 지속적으로 통합되어 도입 장벽을 낮추고 최첨단 기술을 따라잡는 데 필요한 마찰을 해소하고 있습니다.

하지만 심층 신경망(소프트웨어 2.0이라고도 함) 기반 애플리케이션은 모델을 학습하고 제공하기 위해 강력한 가속기를 필요로 하며, 인프라를 상호 연결하고 사용자에게 소프트웨어와 하드웨어 간의 호환성과 유연성을 보장하는 통합 플랫폼은 경쟁 우위를 확보하는 데 중요한 요소입니다.

레드햇 오픈시프트 AI는 PyTorch, Kubeflow, vLLM과 같은 오픈 소스 프로젝트를 오픈시프트 상에 구축합니다. 

**레드햇 오픈시프트 AI**
* 다양한 가속기를 지원
* Kueue와 같은 워크로드 오케스트레이션 도구를 활용
* 벤더-록인 최소화 / 활용도 극대화 / 투자 수익률(ROI)을 높임
* Kubeflow Training 오퍼레이터 & SDK
  + PyTorch 및 HuggingFace Transformers와 같은 인기 라이브러리를 사용
  + 오프시프트에서 모델을 훈련하는 데 Kubeflow를 사용 가능
  + [fms-hf-tuning](https://github.com/foundation-model-stack/fms-hf-tuning)과 같은 더욱 맞춤화된 라이브러리를 활용 가능

### 1.2 Kubeflow Trainer를 통한 LLM Fine-Tuning

* Kubeflow Training 오퍼레이터 및 SDK 사용
  + SFTTrainer (Hugging Face Supervised Fine-tuning Trainer)
  + LoRA/QLoRA
  + PyTorch FSDP (Fully Sharding Data Parallel)

* 최적화
  + FlashAttention 및 Liger Kernel를 통한 최적화/융합 커널를 통한 메모리 소비 개선
  + 효율적인 GPU P2P 통신
<br>
<br>

## 2. 랩 환경 구성

### 2.1 시스템 구성

* 오픈시프트 4.14+
* 오픈시프트 AI 오퍼레이터 2.19+
  + 대시보드
  + 워크벤치
  + 훈련 오퍼레이터
  + 기타 등등 활성화
* 워커 노드 상에 GPU
  + NVidia GPU (Ampere 이상의 GPU)
  + AMD 가속기 (Instinct MI300X 이상의 가속기)
* Node Feature Discovery 오퍼레이터
* GPU 오퍼레이터
  + NVidia GPU 오퍼레이터
  + AMD GPU 오퍼레이터 ([구성 방법](https://instinct.docs.amd.com/projects/gpu-operator/en/latest/installation/openshift-olm.html#configuration))

<br>
<br>

## 3. LLM Fine-Tuning

<br>
<br>

## 4. 

<br>
<br>

------
[차례](../README.md)