# RHEL AI 소개

**목차**
1. [RHEL AI 개요](./instroduction_of_rhel_ai.md#1-rhel-ai-개요)<br>
2. [RHEL AI 공통 용어](./instroduction_of_rhel_ai.md#2-rhel-ai-공통-용어)<br>
3. [InstructLAB과 RHEL AI](./instroduction_of_rhel_ai.md#3-instructlab과-rhel-ai)<br>
4. [RHEL AI 하드웨어 요구 사항](./instroduction_of_rhel_ai.md#4-rhel-ai-하드웨어-요구-사항)<br>
<br>
<br>

## 1. RHEL AI 개요

RHEL AI는 오픈 소스 형태의 대규모 언어 모델(LLM: Large-Language Models)에서 엔터프라이즈 애플리케이션을 개발할 수 있는 플랫폼입니다.

> [!NOTE]
> RHEL AI는 Red Hat InstructLab 오픈 소스 프로젝트에서 빌드되었습니다.

**RHEL AI 수행 작업**
1. LLM을 호스팅하고 대규모 언어 모델(LLM)의 오픈 소스 Granite 제품군과 상호 작용
2. LAB 방법을 사용하여 git 저장소에 자체 지식 또는 기술 데이터를 만들고 추가
3. 그런 다음 최소한의 머신 러닝 배경 지식으로 해당 데이터에 대한 모델을 미세 조정
4. 데이터로 미세 조정된 모델과 상호 작용

RHEL AI를 사용하면 대규모 언어 모델(LLM)에 직접 기여할 수 있습니다.
* 이를 통해 챗봇을 포함한 AI 기반 애플리케이션을 쉽고 효율적으로 빌드
<br>
<br>

## 2 RHEL AI 공통 용어

**InstructLab**
* ilab 명령줄 인터페이스(CLI) 도구를 사용하여 AI 대규모 언어 모델(LLM)에 쉽게 참여할 수 있는 플랫폼
* 오픈 소스 프로젝트

**Large Languages Models**
* LLM이라고도 함
* 언어 생성이나 업무 처리가 가능한 인공지능의 한 유형

**Synthetic Data Generation (SDG)**
* 대규모 LLM(대규모 언어 모델)을 사용하여 인간이 생성한 샘플을 통해 인공 데이터를 생성
* 이 데이터를 사용하여 다른 LLM을 훈련하는 프로세스

**Fine-tuning**
* 특정한 목표를 달성하기 위해 LLM을 훈련하는 기술
* 즉, 특정한 정보를 알거나 특정한 작업을 수행

**LAB**
* "Large-Scale Alignment for ChatBots"의 약자
* IBM Research에서 발명한 LAB은 LLM을 위한 새로운 합성 데이터 기반 및 다단계 학습 미세 조정 방법
* InstructLab은 합성 생성 및 학습 중에 LAB 방법을 구현

**Multi-phase training**
* LAB 방법이 구현하는 미세 조정(fine-tuning) 전략
* 이 프로세스를 진행하는 동안, 모델은 별도의 단계에서 여러 데이터 세트에 대해 미세 조정 수행
* 모델은 에포크(*Epoch*)라고 하는 여러 단계에서 학습하며, 이는 체크포인트로 저장 됨
  + 그런 다음 가장 성능이 좋은 체크포인트가 다음 단계에서 학습하는 데 사용
  + 완전히 미세 조정된 모델은 최종 단계에서 가장 성능이 좋은 체크포인트

**Serving**
* "모델 제공"이라고도 함
* LLM 또는 훈련된 모델을 서버에 배포하는 것
* 이를 통해 챗봇으로 모델과 상호 작용

**Inference**
* 모델을 제공하고 이와 대화할 때, ***추론***은 모델이 입력 데이터를 기반으로 처리, 추론 및 출력을 생성할 수 있는 것을 의미

**Taxonomy**
* LAB 방법은 정보 분류 방법인 택소노미에 의해 구동
* RHEL AI에서 택소노미 트리를 사용자 정의하여 자신의 데이터로 미세 조정된 모델을 만들 수 있음

**Granite**
* IBM에서 훈련한 오픈 소스(Apache 2.0) 대규모 언어 모델
* 사용자 정의를 위한 기본 LLM으로, RHEL AI에서 Granite 패밀리 모델을 다운로드 가능

**Pytorch**
* GPU 및 CPU에서의 딥러닝을 위한 최적화된 텐서(tensor) 라이브러리

**vLLM**
* LLM을 위한 메모리 효율적인 추론 및 제공 엔진 라이브러리

**FSDP**
* [Fully Shared Data Parallels](https://pytorch.org/tutorials/intermediate/FSDP_tutorial.html)의 약자
* Pytorch 도구 FSDP는 하드웨어의 여러 장치에 컴퓨팅 파워를 분산
* 이를 통해 학습 프로세스가 최적화되고 미세 조정이 더 빠르고 메모리 효율성이 높아짐
* 이 도구는 DeepSpeed의 기능을 공유

**DeepSpeed**
* 여러 장치에 컴퓨팅 리소스를 분산하여 LLM 학습 및 미세 조정을 최적화하는 Python 라이브러리
* 이 도구는 FSDP의 기능을 공유
* Deepspeed는 현재 nVidia 머신에 권장되는 하드웨어 오프로더
<br>
<br>

## 3. InstructLAB과 RHEL AI

InstructLab은 대규모 언어 모델에 기여할 수 있는 오픈 소스 AI 프로젝트입니다.
* RHEL AI는 InstructLab 프로젝트의 기반을 활용하여 애플리케이션에서 LLM 통합을 위한 엔터프라이즈 플랫폼을 구축

### 3.1 InstructLAB vs RHEL AI

* RHEL AI는 전용 그래픽 처리 장치(GPU)가 있는 고성능 서버 플랫폼에 구성
* InstructLab은 노트북과 개인용 컴퓨터를 포함한 소규모 플랫폼에서 사용
<br>

### 3.2 Large-scale Alignment for chatBots (LAB)

* InstructLab은 LLM을 위한 새로운 합성 데이터 기반 미세 조정 방법인 LAB(Large-scale Alignment for chatBots) 기술을 구현
* LAB 프로세스
  + 분류 기반 합성 데이터 생성 프로세스
  + 다단계 학습 프로세스
  + 미세 조정 프레임워크
* RHEL AI와 InstructLab을 사용하면 고유한 사용 사례에 맞게 도메인별 지식으로 LLM을 커스터마이징
<br>

### 3.3 InstructLAB 모델 정렬

**InstructLAB 및 도구들**
* RHEL AI 부팅 이미지에 포함
* InstructLab은 LLM 미세 조정에 대한 새로운 접근 방식으로 LAB 사용

**LAB(Large-Scale Alignment for ChatBots)**
* 고품질 합성 데이터 생성(SDG) 및 다단계 학습을 구현하는 분류 기반 시스템을 사용
* InstructLab CLI에서 빌드된 RHEL AI 명령줄 인터페이스(CLI)를 사용

**RHEL AI LLM 사용자 정의 워크플로**
1. RHEL AI 설치 및 초기화
2. CLI 및 Git 워크플로를 사용하여 택소노미 트리에 기술과 지식을 추가
3. *mixtral-8x7B-Instruct* 교사 모델을 사용하여 합성 데이터 생성(SDG)을 실행
   * SDG는 사용자가 제공한 특정 샘플을 기반으로 모델 튜닝을 위해 수백 또는 수천 개의 합성 질문-답변 쌍을 생성 가능
4. InstructLab을 사용하여 새로운 합성 생성 데이터로 기본 모델을 훈련
   * *prometheus-8x7B-V2.0* 심사 모델은 새로 학습된 모델의 성능을 평가
5. vLLM과 함께 InstructLab을 사용하여 추론을 위한 새로운 사용자 정의 모델을 제공

> [!NOTE]
> 이를 통해 고유한 도메인별 지식에서 생성된 합성 데이터에 Granite 기본 모델을 조정하여 고유한 사용자 지정 LLM을 만들 수 있습니다.
<br>
<br>

## 4. RHEL AI 하드웨어 요구 사항

### 4.1 Granite 모델 기반 end-to-end 워크플로 요구 사항

Granite 모델을 커스터마이징을 하는데 필요한 하드웨어 리소스로, 이는 합성 데이터 생성 (SDG), Multi-Phase 훈련, 및 커스텀마이징 된 Granite 모델 평가를 포함합니다.

#### 4.1.1 베어메탈

|$\color{lime}{\texttt{하드웨어 벤더}}$|$\color{lime}{\texttt{지원되는 디바이스}}$|$\color{lime}{\texttt{디바이스 메모리}}$|
|:---:|:---:|:---:|
|NVIDIA|2xA100<br>4xA100<br>8xA100|160 GiB<br>320 GiB<br>640 GiB|
|NVIDIA|2xH100<br>4xH100<br>8xH100|160 GiB<br>320 GiB<br>640 GiB|
|NVIDIA|4xL40S<br>8xL40S|192 GiB<br>384 GiB|
|INTEL|8xGaudi3|1024 GiB|
<br>

### 4.2 Granite 모델 기반 추론 모델 서비스를 위한 요구 사항

RHEL AI 상에서 Granite 모델을 가지고 추론 서비스를 위한 최소 하드웨어 리소스 입니다.

#### 4.2.1 베어메탈

|$\color{lime}{\texttt{하드웨어 벤더}}$|$\color{lime}{\texttt{지원되는 디바이스}}$|$\color{lime}{\texttt{디바이스 메모리}}$|$\color{lime}{\texttt{추가 디스크 용량}}$|
|:---:|:---:|:---:|:---:|
|NVIDIA|A100|80 GiB|1 TiB|
|NVIDIA|H100|80 GiB|1 TiB|
|NVIDIA|L40S|48 GiB|1 TiB|
|NVIDIA|L4|24 GiB|1 TiB|
|INTEL|8xGaudi3|128 GiB|1 TiB|
<br>
<br>

------
[차례](../README.md)
