# RHSC 키노트 데모 소개

목차
* [Large Language Model (LLM)은 무엇 인가?](./introdution-of-lab.md#large-language-model-llm은-무엇-인가)<br>
* [LLM은 어떻게 훈련 되는 가?](./introdution-of-lab.md#llm은-어떻게-훈련-되는-가)<br>
* [LLM이 InstructLab과 어떤 관련이 있는가?](./introdution-of-lab.md#llm이-instructlab과-어떤-관련이-있는가)<br>

<hr>

해당 랩에서는 **RHEL AI**가 무엇인지, 여러 분의 비즈니스에 어떻게 가치를 제공할 것인가에 대하여 설명할 것 입니다. 또한 **RHEL AI**를 이용하여 Large Language Model (LLM)을 향상 시키고, 합성 데이터 생성을 사용하여 이를 학습 시키는 것에 대하여 배울 것 입니다.

**RHEL AI**는 몇 개의 핵심 요소로 구성되어 있습니다.
1. RHEL 이미지 모드
2. Granite Large Language Models (LLMs)
3. 모델 정렬을 위한 InstructLab
4. 레드햇의 지원 및 보상

InstructLab은 레드햇과 MIT-IBM Watson AI Lab의 완전 오픈소스 프로젝트로, "Large-scale Alignment for ChatBots (LAB)"을 소개합니다. 이 프로젝트의 혁신은 LLM 학습 중 교육-튜닝(instruction-tuning) 단계에서 도움이 됩니다. 그러나 이 프로젝트의 이점을 완전히 이해하려면 *LLM이 무엇인지에 대한 몇 가지 기본 개념*과 *모델을 교육하는 데 따른 어려움과 비용*에 대해 잘 알고 있어야 합니다.
<br>

## Large Language Model (LLM)은 무엇 인가?

LLM은 딥 러닝 기술을 사용하여 입력 데이터를 기반으로 인간과 유사한 텍스트를 이해하고 생성하는 인공 지능(AI) 모델의 한 유형입니다. 이러한 모델은 방대한 양의 텍스트 데이터를 분석하고 데이터 내의 패턴, 관계 및 구조를 학습하도록 설계되었습니다.

LLM은 다음과 같은 다양한 자연어 처리(NLP: Natural Language Processing) 작업에 사용할 수 있습니다.
* 텍스트 분류 (Text Classification)
  - 스팸 감지 또는 감정 분석과 같이 텍스트를 콘텐츠에 따라 분류
* 텍스트 요약 (Text Summarization)
  - 뉴스 기사나 연구 논문과 같이 긴 텍스트의 간결한 요약을 생성
* 기계 번역 (Machine Translation)
  - 영어에서 프랑스어로 또는 독일어에서 중국어로와 같이 텍스트를 한 언어에서 다른 언어로 번역
* 질의 응답 (Question Answering)
  - 주어진 맥락이나 문서 집합을 기반으로 질문에 대답
* 텍스트 생성 (Text Generation)
  - 기사, 스토리 또는 시를 쓰는 것과 같이 일관성 있고 맥락적으로 관련성이 있으며 문법적으로 올바른 새로운 텍스트를 만듦

LLM은 일반적으로 복잡한 언어 패턴과 데이터 관계를 포착할 수 있는 많은 매개변수(수백만에서 수십억)를 갖습니다. 이러한 모델은 감독되지 않은(unsupervised) 사전 학습(pre-training) 및 감독(supervised)하의 미세 조정(fine-tuning)과 같은 기술을 사용하여 책, 기사 및 웹사이트와 같은 대규모 데이터 세트에서 학습됩니다. 일부 인기 있는 LLM에는 GPT-4, Llama 및 Mistral이 있습니다.

**요약**
* LLM은 딥 러닝 기술을 사용하여 입력 데이터를 기반으로 인간과 유사한 텍스트를 이해하고 생성하는 인공 지능 모델
* LLM은 방대한 양의 텍스트 데이터를 분석하고 데이터 내의 패턴, 관계 및 구조를 학습하도록 설계되었으며 다양한 자연어 처리 작업에 사용 가능
<br>

## LLM은 어떻게 훈련 되는 가?

LLM은 일반적으로 딥 러닝 기술과 대규모 데이터 세트를 사용하여 학습합니다. 

학습 프로세스에는 여러 단계가 포함됩니다.
1. 데이터 수집 (Data Collection)
   - 책, 기사, 웹사이트, 데이터베이스와 같은 다양한 소스에서 방대한 양의 텍스트 데이터를 수집
   - 모델이 일반화를 잘 수행할 수 있도록 데이터에는 다양한 언어, 도메인, 스타일이 포함될 수 있음
2. 사전 처리 (Pre-Processing)
   - 원시 텍스트 데이터는 노이즈, 불일치, 관련 없는 정보를 제거하기 위해 사전 처리됨
   - 여기에는 토큰화, 소문자화, 어간 추출(stemming), 어근화(lemmatization), 인코딩이 포함될 수 있음
3. 토큰화 (Tokenization)
   - 사전 처리된 텍스트 데이터는 모델의 입력 및 출력으로 사용할 수 있는 토큰(단어 또는 하위 단어)으로 변환
   - 일부 모델은 바이트 쌍 인코딩(BPE:Byte-Pair Encoding) 또는 하위 단어 분할을 사용하여 어휘에서 벗어난 단어를 처리하고 문맥 정보를 유지할 수 있는 토큰을 만듦
4. 사전 학습 (Pre-Training)
   - 모델은 데이터의 패턴과 구조를 학습하기 위해 감독 없이 (unsupervised) 또는 자체 감독(self-supervised) 방식으로 학습됨
5. 모델 정렬 (Model Alignment)
   - 지시 튜닝(instruction tuning) 및 선호도 튜닝(preference tuning)
   - 인간의 가치와 목표를 LLM으로 인코딩하여 가능한 한 유용하고 안전하며 신뢰할 수 있게 만드는 프로세스
   - 이 단계는 다른 단계 일부와는 다르게 컴퓨팅 집약적이지 않음
<br>

## LLM이 InstructLab과 어떤 관련이 있는가?

**InstructLab**은 분류법에 따른 합성 데이터 생성 프로세스와 다단계 튜닝 프레임워크를 활용합니다. 이를 통해 InstructLab은 값비싼 인간 주석에 대한 의존도를 크게 줄여 LLM에 기여하는 것을 쉽고 접근하기 쉽게 만듭니다.
* 즉, InstructLab은 LLM을 사용하여 데이터를 생성한 다음 이를 사용하여 LLM을 추가로 훈련할 수 있음
* 또한 정렬 단계가 대부분 사용자가 지식을 기여하는 시작점이 됨

LAB (Large-scale Alignment for ChatBots) 기술 이전에는 사용자가 일반적으로 LLM 훈련에 직접 관여하지 않았습니다. 복잡하게 들릴 수 있지만, 계속해 보면 얼마나 사용하기 쉬운지 알게 될 것입니다.

InstructLab을 사용하면 기술(skills)과 지식(knowledge)이라는 용어를 보게 될 것입니다. 기술과 지식의 차이점은 무엇입니까? 간단한 비유로 **기술**은 *누군가에게 낚시하는 법을 가르치는 것*으로 생각하면 됩니다. 반면 **지식**은 *해가 질 때, 둑을 따라 나무 줄기 근처에 줄을 던지면서 농어를 잡기에 가장 좋은 장소라는 것을 아는 것*입니다.
<br>
<br>

------
[차례](../README.md) &nbsp;&nbsp;&nbsp;&nbsp; [>> InstructLab 시작 >>](./start-with-instructlab.md)