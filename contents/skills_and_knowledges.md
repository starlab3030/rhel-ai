# 기술과 지식 (Skills and Knowledges)

**목차**
1. [분류학(택소노미) 트리 커스터마이징](./skills_and_knowledges.md#1-분류학-트리-커스터마이징)<br>
2. [분류학(택소노미) 트리에 지식 추가](./skills_and_knowledges.md#2-분류학-트리에-지식-추가)<br>
3. [분류학(택소노미) 트리에 기술 추가](./skills_and_knowledges.md#3-분류학-트리에-기술-추가)<br>
4. [모델 성능 최적화를 위한 YAML 생성](./skills_and_knowledges.md#4-모델-성능-최적화를-위한-yaml-생성)<br>
5. [InstructLab의 모델 훈련 및 평가](./skills_and_knowledges.md#5-instructlab의-모델-훈련-및-평가)<br>
90. [예제 샘플](./skills_and_knowledges.md#90-예제-샘플)<br>
99. [참조](./skills_and_knowledges.md#99-참조)<br>
<br>
<br>

## 1. 분류학 트리 커스터마이징

### 1.1 RHEL AI의 데이터 세트

RHEL AI 환경에서 지식 또는 기술 데이터로 택소노미 트리를 수정하여 사용자 정의 Granite Large Language Model(LLM)을 만들 수 있습니다.
* RHEL AI에서 지식 및 기술 생성 데이터 세트는 YAML로 포맷
* YAML 구성은 qna.yaml 파일
  + "qna"는 질문과 답변을 의미
* 택소노미 트리는 qna.yaml 파일을 보관하는 분류 및 정보 분류 방법

Granite LLM을 훈련하는 데 사용할 수 있는 지식 문서 유형
* 마크다운
* PDF
<br>

### 1.2 기술과 지식(Skills & Knowledges)의 개념

기술 및 지식 세트를 사용하고 도메인별 정보를 지정하여 사용자 지정 모델을 교육할 수 있습니다.

#### 1.2.1 지식 (Knowledges)

* 정보(information)와 사실(facts)로 구성된 데이터 세트
* 모델에 대한 지식 데이터를 만들 때, 모델이 질문에 더 정확하게 답할 수 있도록 추가 데이터와 정보를 가진 데이터 세트를 제공

#### 1.2.2 기술 (Skills)

* 모델에 작업 수행 방법을 교육할 수 있는 데이터 세트

**RHEL AI의 기술 범주**

* 구성 기술: AI 모델이 특정 작업이나 기능을 수행
  + 자유형 구성 기술: 추가 ​​컨텍스트나 정보가 필요하지 않은 수행 기술
  + 근거 구성 기술
    - 추가 ​​컨텍스트가 필요한 수행 기술
    - 예를 들어, 추가 컨텍스트가 테이블 레이아웃의 예인 경우 모델에 표를 읽도록 교육할 수 있음
* 기초 기술: 기초 기술은 수학, 추론 및 코딩과 관련된 기술
<br>
<br>

## 2. 분류학 트리에 지식(Knowledges) 추가

(*스타터*) 모델이 도메인별 정보를 학습할 수 있도록 분류학(택소노미) 트리를 사용자 지정할 수 있습니다.
* RHEL AI의 경우, 지식 데이터는 Git 저장소에 호스팅
* 지식 기여는 qna.yaml 파일을 사용하여 "*모델에 가르치려는 문서*"를 읽는 방법을 학습

### 2.1 지식을 위한 *qna.yaml*

지식에 대한 qna.yaml 파일에 포함되는 ***키***-***값*** 항목 세트

$\color{lightblue}{\texttt{version}}$
* *qna.yaml* 파일에서 사용된 분류 스키마 버전
* 현재 지원되는 값은 `3`

$\color{lightblue}{\texttt{created\\_by}}$
* 기여자 또는 사용자 이름
* 예: `shadowman`

$\color{lightblue}{\texttt{domain}}$
* 지식 문서의 주제 또는 범주
* 도메인은 합성 데이터 생성 중에 교사 모델에 프롬프트를 표시하고 추가 컨텍스트를 추가
* `domain` 필드는 3개 단어를 넘지 않는 것이 좋음
  + 피식스 별자에 대한 도메인 예는 `Astronomy`
  + 건강보험 정보에 대한 지식 문서의 경우 도메인 예는 `Healthcare`

$\color{lightblue}{\texttt{seed\\_examples}}$
* 지식 문서의 맥락과 함께 "*질문과 답변*" 쌍이 들어 있는 필드
* *qna.yaml* 파일에는 최소 5개의 시드 예제가 필요
  ```yaml
  seed_examples:
    - context:
      questions_and_answers:
  ```

$\color{lightblue}{\texttt{context}}$
* 지식 문서에서 정확히 가져온 정보 덩어리
* 교사 모델을 안내하는 데 도움이 되도록 표, 단락 또는 목록을 포함한 다양한 유형의 콘텐츠를 강조 표시
* 제한 사항
  + 각 *qna.yaml*에는 5개의 컨텍스트 블록이 필요
  + 최대 토큰 수는 500개
* 예
  ```
  불사조는 남쪽 하늘의 작은 별자리입니다. 신화 속 불사조의 이름을 따서 지어졌으며, 요한 바이어가 1603년 Uranometria에서 천체 지도에 처음 묘사했습니다. 프랑스 탐험가이자 천문학자인 니콜라 루이 드 라카유는 더 밝은 별을 지도에 표시하고 1756년에 바이어 명칭을 부여했습니다.
  ```

$\color{lightblue}{\texttt{questions\\_and\\_answers}}$
* 모델이 학습할 수 있는 질문과 답변이 포함된 필드
* *qna.yaml*에는 `context` 블록당 세 개의 질문-답변 쌍이 필요
  ```yaml
  questions_and_answers:
    - question:
      answer:
  ```

$\color{lightblue}{\texttt{question}}$
* 관련 맥락과 관련이 있고 이를 기반으로 하는 질문
* 사실 기반, 추론 또는 설명을 포함하여 다양한 질문과 질문 유형을 제공
* 최대 토큰 수는 250개
* 예
  ```
  불사조 별자리를 만든 사람은 누구입니까?
  ```

$\color{lightblue}{\texttt{answer}}$
* 지정된 질문에 대한 답변
* 답변은 완전한 문장이어야 하며, 맥락 필드에서 참조되어야 함
* 최대 토큰 수는 250개
* 예
  ```
  불사조 별자리는 프랑스의 탐험가이자 천문학자 니콜라 루이 드 라카유가 기록했습니다.
  ```

$\color{lightblue}{\texttt{document\\_outline}}$
* 논문 진술과 유사한 문서의 간략한 요약
* 이는 문서 내용에 대한 높은 수준의 맥락을 제공
* 이는 자세하고 `context` 필드의 내용을 참조해야 함
* 예
  ```
  불사조 별자리에 대한 정보에는 별자리에 있는 별의 역사, 특성, 특징 등이 포함됩니다.
  ```

$\color{lightblue}{\texttt{document}}$
* 지식 데이터의 출처가 포함된 필드
* 예
  ```yaml
  document:
     repo:
     commit:
     patterns:
  ```

$\color{lightblue}{\texttt{repo}}$
* 지식 파일이 들어 있는 Git 저장소의 URL
* 예
  ```
  github.com/<profile>/<repo-name>
  ```

$\color{lightblue}{\texttt{commit}}$
* 리포지토리의 문서에 해당하는 전체 커밋 해시

$\color{lightblue}{\texttt{patterns}}$
* git 저장소의 파일을 포함
* 유효한 파일은 *.md 또는 *.pdf
* 예
  ```
  phoenix_constellation.md
  ```
<br>

### 2.2 지식을 위한 YAML 파일 생성

제공된 지식 파일로 LLM을 훈련하기 위하여, RHEL AI 도구를 사용하여 qna.yaml을 생성하는 절차를 설명합니다.

1. 택소노미를 업데이트 하면, git에 저장한 지식 파일을 체크아웃 함
2. 택소노미 폴더로 이동
   * RHEL AI는 상호작용할 수 있는 기성 택소노미 트리를 포함하고 있음
3. 택소노미 디렉토리의 지식 폴더로 이동
4. 지식 관련 *qna.yaml* 파일을 추가하기 위해, 택소노미 트리에 디렉토리와 폴더를 추가
   * 예: 택소노미 트리에 지식 관련 파일
     ```
     taxonomy/knowledge/technical_documents/product_customer_cases/qna.yaml
     ```
5. 원하는 텍스트 편집기를 사용하여 *qna.yaml* 파일을 만듦
   * YAML에는 *qna.yaml* 제목이 있어야 함
6. *qna.yaml* 파일에 필요한 키를 추가하고 변경 사항을 저장

> [!NOTE]
> SDG를 제대로 실행하려면 `questions_and_answers` 매개변수에 컨텍스트 값당 최소 5개의 컨텍스트 청크와 3개의 질문과 답변 시드를 포함해야 합니다.
<br>

### 2.3 검증

지식 관련 *qna.yaml* 파일 검증
```bash
ilab taxonomy diff
```
* 택소노미 트리와 *qna.yaml* 파일이 유효하고 올바르게 포맷되었는지 표시
* 발생한 오류를 수정할 수 있는 곳 표시

실행 결과 - 예) 유효한 택소노미 트리 및 *qna.yaml* 파일
```log
knowledge/technical_documents/product_customer_cases/qna.yaml
Taxonomy in /taxonomy/ is valid :)
```

실행 결과 - 예) 오류가 있는 잘못된 택소노미 트리 및 *qna.yaml* 파일
```log
9:15 error syntax error: mapping values are not allowed here (syntax)
Reading taxonomy failed with the following error: 1 taxonomy with errors! Exiting.
```
<br>

### 2.4 샘플: 지식 관련 YAML 스펙

지식 기여는 *qna.yaml* 파일을 사용하여 모델에 가르치고 싶은 문서를 읽는 방법을 학습
* RHEL AI에서 합성 데이터 생성(SDG) 프로세스는 qna.yaml 시드 예제를 사용하여 대량의 인공 데이터를 생성
* 이 프로세스를 통해 모델은 제공된 샘플에만 의존하는 대신 학습할 데이터가 더 많아짐

**샘플 *qna.yaml* 파일**
```yaml
version: 3 #1
domain: astronomy #2
document_outline: | #3
  불사조 별자리에 대한 정보에는 별자리에 있는 별의 역사, 특성, 특징 등이 포함됩니다.
created_by: shadowman #4
seed_examples:
  - context: | #5
      **불사조**는 남쪽 하늘의 작은 별자리입니다. 신화 속의 불사조(신화)에서 이름을 따온 이 별자리는 요한 바이어가 1603년 Uranometria에서 천체 지도에 처음 묘사했습니다. 프랑스의 탐험가이자 천문학자인 니콜라 루이 드 라카유는 1756년에 더 밝은 별을 지도에 표시하고 바이어 명칭을 부여했습니다. 이 별자리는 적위가 약 -39도에서 -57도, 적경이 23.5시에서 2.5시입니다. 불사조, 두루미, 공작, 투카나 별자리는 남방새로 알려져 있습니다.
    questions_and_answers:
      - question: | #6
          불사조 별자리는 무엇입니까?
        answer: | #7
          불사조 자리는 남쪽 하늘의 작은 별자리입니다.
      - question: |
          불사조 별자리를 만든 사람은 누구입니까?
        answer: |
          불사조 별자리는 프랑스의 탐험가이자 천문학자 니콜라 루이 드 라카유가 기록했습니다.
      - question: |
          불사조 별자리는 얼마나 멀리 뻗어 있나요?
        answer: |
          불사조 별자리는 적위가 대략 -39°에서 -57°까지이고, 적경이 23.5시에서 2.5시입니다.
  - context: |
      Phoenix는 Petrus Plancius가 Pieter Dirkszoon Keyser와 Frederick de Houtman의 관측을 통해 확립한 12개 별자리 중 가장 큰 별자리였습니다. 처음에는 Plancius가 Jodocus Hondius와 함께 암스테르담에서 1597년(또는 1598년)에 출판한 직경 35cm의 천구의에 처음 등장했습니다. 천체 지도에 이 별자리가 처음 묘사된 것은 1603년 Johann Bayer *Uranometria*에 있었습니다. De Houtman은 같은 해에 네덜란드 이름 *Den voghel Fenicx*, "The Bird Phoenix"라는 이름으로 그의 남방 별자리 카탈로그에 포함시켰는데, 이는 고전 신화의 불사조를 상징합니다. 가장 밝은 별인 Alpha Phoenicis의 이름 중 하나인 Ankaa는 아랍어 العنقاء에서 유래했으며, 로마자 표기로는 al-‘anqā’, 문자 그대로는 '불사조'를 의미하며, 별자리와 관련하여 1800년 이후에 만들어졌습니다.
    questions_and_answers:
      - question: |
          불사조 자리에서 가장 밝은 별은 무엇이라고 불리나요?
        answer: |
          알파 페니시스(Alpha Phoenicis) 또는 안카(Ankaa)는 불사조 별자리에서 가장 밝은 별입니다.
      - question: 불사조 별자리는 처음 어디에서 나타났나요?
        answer: |
          불사조 별자리는 Jodocus Hondius와 함께 Plancius가 암스테르담에서 1597년(또는 1598년)에 출판한 직경 35cm의 천구에 처음 나타났습니다.
      - question: |
          "불사조 새"는 무엇을 상징합니까?
        answer: |
          "불사조"는 고전 신화의 불사조를 상징합니다.
  - context: |
      불사조는 북쪽으로 포르낙스와 스컬프터, 서쪽으로 그루스, 남쪽으로 투카나, 남쪽으로 히드루스 모서리에 접하고, 동쪽과 남동쪽으로 에리다누스에 접한 작은 별자리입니다. 밝은 별 아케르나르가 근처에 있습니다. 국제 천문학 연맹에서 1922년에 채택한 별자리의 세 글자 약어는 "페"입니다. 벨기에 천문학자 유진 델포르트가 1930년에 정한 공식 별자리 경계는 10개의 세그먼트로 구성된 다각형으로 정의됩니다. 적도 좌표계에서 이 경계의 적경 좌표는 23<sup>h</sup> 26.5<sup>m</sup>와 02<sup>h</sup> 25.0<sup>m</sup> 사이에 있고, 적위 좌표는 −39.31°와 −57.84° 사이에 있습니다. 즉, 북반구에서 40도선 이북에 사는 사람에게는 지평선 아래에 있고, 적도 이북에 사는 사람에게는 하늘 낮은 곳에 있습니다. 남반구 늦은 봄에 호주와 남아프리카와 같은 곳에서 가장 잘 보입니다. 별자리의 대부분은 내부에 있으며, 밝은 별 Achernar, Fomalhaut 및 Beta Ceti의 삼각형을 형성하여 찾을 수 있습니다. Ankaa는 대략 이 삼각형의 중앙에 있습니다.
    questions_and_answers:
      - question: 불사조 별자리의 특징은 무엇입니까?
        answer: |
          불사조는 북쪽으로 Fornax와 Sculptor, 서쪽으로 Grus, 남쪽으로 Tucana, 남쪽으로 Hydrus의 모서리에 접하고 동쪽과 남동쪽으로 Eridanus에 접한 작은 별자리입니다. 밝은 별 Achernar가 근처에 있습니다.
      - question: |
          불사조 자리가 가장 잘 보이는 때는 언제인가요?
        answer: |
          불사조는 남반구 늦은 봄에 호주와 남아프리카와 같은 지역에서 가장 잘 보입니다.
      - question: |
          불사조 별자리의 경계는 어디인가요?
        answer: |
          벨기에의 천문학자 외젠 델포르테가 1930년에 정한 불사조의 공식 별자리 경계는 10개의 부분으로 구성된 다각형으로 정의됩니다
  - context: |
      지금까지 10개의 별에 행성이 있는 것으로 밝혀졌고, SuperWASP 프로젝트를 통해 4개의 행성계가 발견되었습니다. HD 142는 겉보기 등급이 5.7인 노란색 거성으로, 목성의 1.36배 질량의 행성(HD 142b)이 있으며, 328일마다 공전합니다. HD 2039는 겉보기 등급이 9.0인 노란색 준거성으로, 약 330광년 떨어진 곳에 있으며, 목성의 6배 질량의 행성(HD 2039)이 있습니다. WASP-18은 겉보기 등급이 9.29인 별로, 뜨거운 목성과 비슷한 행성(WASP-18b)이 있는 것으로 밝혀졌으며, 별을 공전하는 데 하루도 걸리지 않았습니다. 이 행성 때문에 WASP-18이 실제보다 더 오래되게 보이는 것으로 추정됩니다. WASP-4와 WASP-5는 태양형 노란색 별로 약 1000광년 떨어져 있으며 13등급이며 각각 목성보다 큰 행성이 ​​하나 있습니다. WASP-29는 분광형 K4V, 시각적 등급 11.3의 주황색 왜성으로 토성과 비슷한 크기와 질량의 행성 동반성이 있습니다. 이 행성은 3.9일마다 궤도를 완료합니다.
    questions_and_answers:
      - question: 불사조 별자리에는 행성을 가진 별이 몇 개나 있습니까?
        answer: |
          불사조 별자리에서 10개의 별이 행성을 가지고 있는 것으로 발견되었으며, SuperWASP 프로젝트를 통해 4개의 행성계가 발견되었습니다.
      - question: |
          HD 142는 무엇인가요?
        answer: |
          HD 142는 겉보기 등급 5.7의 황색 거성이며, 목성 질량의 1.36배인 행성(HD 142 b)을 갖고 있으며 328일마다 공전합니다.
      - question: |
          WASP-4와 WASP-5는 태양형 노란색 별인가요?
        answer: |
          네, WASP-4와 WASP-5는 태양형 노란색 별로서 거리는 약 1000광년이고 등급은 13등급이며, 각각 목성보다 큰 행성을 하나 가지고 있습니다.
  - context: |
      별자리는 은하수의 은하면에 있지 않으며, 눈에 띄는 성단은 없습니다. NGC 625는 겉보기 등급 11.0의 왜소 불규칙 은하로 약 1,270만 광년 떨어져 있습니다. 지름이 24,000광년에 불과한 이 은하는 조각가 그룹의 외곽 구성원입니다. NGC 625는 충돌에 연루된 것으로 생각되며 활발한 별 형성이 폭발적으로 일어나고 있습니다. NGC 37은 겉보기 등급 14.66의 렌즈형 은하입니다. 지름이 약 42킬로파섹 137,000광년이고 나이는 약 129억 년입니다. 불규칙 은하 NGC 87과 세 개의 나선 은하 NGC 88, NGC 89, NGC 92로 구성된 로버트 사중주는 약 1억 6천만 광년 떨어진 곳에 위치하며 충돌하고 합쳐지는 과정에 있는 네 개의 은하로 구성된 그룹입니다. 이들은 반경 1.6분각의 원 안에 있으며, 이는 약 75,000광년에 해당합니다. ESO 243-49 은하에는 중간 질량 블랙홀인 HLX-1이 있습니다. 이는 이런 종류의 블랙홀로는 처음으로 확인되었습니다. ESO 243-49와의 충돌로 흡수된 왜소 은하의 잔해로 생각됩니다. 발견되기 전에는 이 종류의 블랙홀은 가설에 불과했습니다.
    questions_and_answers:
      - question: |
          불사조 자리는 은하수의 일부인가요?
        answer: |
          불사조 별자리는 우리 은하의 은하면에 있지 않으며, 뚜렷한 별 무리도 없습니다.
      - question: |
          NGC 625는 몇 광년 떨어져 있나요?
        answer: |
          NGC 625는 지름이 24,000 광년이고 조각가 은하군의 외곽 구성원입니다.
      - question: |
          로버트 사중주는 무엇으로 구성되어 있나요?
        answer: |
          로버트의 사중주는 불규칙 은하 NGC 87과 세 개의 나선 은하 NGC 88, NGC 89, NGC 92로 구성되어 있습니다.
document:
  repo: https://github.com/shadowman/<repo-name> / #8
  commit: <commit hash> #9
  patterns:
    - phoenix_constellation.md #10
    - phoenix_history.md
```
1. 지식 관련 *qna.yaml* 형식의 버전을 지정
   * 현재 유효한 값은 `3`
2. 문서의 주제나 카테고리를 지정
   * 예) "기술 문서" 또는 "설치 가이드"
3. 문서 내용의 개요를 지정
   * `document_outline` 필드에 `context` 매개변수에 포함하는 주제를 참조하는 것이 좋음
   * 예)
     + 문서가 설치 가이드이고 각 `context`에 다른 클라우드 공급자에 대한 세부 정보가 포함된 경우
     + `document_outline`에는 "AWS, GCP 및 Azure용 설치 가이드" 입력
4. 이름 혹은 git 사용자 이름
5. 지식 데이터의 한 단락을 지정
   * 질문과 답변의 기반이 되는 콘텐츠
   * `context` 블록의 형식은 지식 파일의 형식과 일치해야 함
   * 예) 지식 문서가 마크다운 형식인 경우 컨텍스트 블록도 마크다운 형식으로 구성
6. 모델에게 할 질문을 지정
   * 질문은 `context` 필드의 정보를 기반
   * 예) "제품의 최신 버전은 무엇입니까?"
7. 모델이 답변하기를 원하는 응답을 지정
   * 답변에 대한 정보는 `context` 블록에 포함되어 있는 내용이지만 복사해서는 안 되며 완전한 문장이어야 함
   * 답변은 완전한 문장이어야 함
     + 예) "제품의 최신 버전은 버전 1.5입니다"
8. 지식 파일이 보관된 저장소의 URL 지정
9. Git 저장소에 있는 지식 파일의 커밋 SHA를 지정
10. Git 저장소의 문서를 지정
    * 유효한 문서 유형 값은 *.md 또는 *.pdf
    * 단일 *qna.yaml* 파일은 하나의 문서 유형만 참조 가능
    * 같은 *qna.yaml* 내에서 파일 유형을 혼합하는 것은 지원되지 않음
<br>

### 2.5 지식 관련 마크다운 파일 생성

RHEL AI 버전 1.4에서는 지식 문서와 데이터를 git 저장소와 마크다운 형식으로 호스팅해야 합니다.
* 표준 git 워크플로를 사용하여 파일을 만들고 저장소에 업로드 
* 다양한 오픈 소스 마크다운 변환 도구를 사용
  + Pandoc: 오픈 소스 변환 도구
  + Visual Studio Code with All in one 확장: Visual Studio Code에서 문서를 열고 Markdown All in One 확장을 사용하여 마크다운으로 변환
  + IBM Deepsearch/Docling: PDF 문서를 JSON 및 마크다운으로 변환하는 기능을 독립형 패키지로 번들로 제공

#### 2.5.1 마크다운 파일 생성 순서

1. 선호하는 git 호스팅 플랫폼을 선택
   * git과 호환되는 한 RHEL AI에서 모든 플랫폼을 사용 가능
2. 문서를 *.md 마크다운 형식으로 변환
   * 지식 데이터에 원하는 마크다운 변환 소프트웨어를 사용
3. 파일 이름과 커밋 해시를 기록
   * 이 값은 *qna.yaml* 파일에서 사용
4. *.md 파일을 만들어 git 저장소에 업로드

#### 2.5.2 지식 관련 마크다운 파일 지침

* 모든 문서는 텍스트
  - 이미지는 현재 지원되지 않음
* 문서에서 각주를 제거
* 표는 마크다운 형식
* 차트와 그래프는 현재 지원되지 않음

#### 2.5.3 지식 문서의 마크다운 샘플

```markdown
# 불사조(별자리)

**불사조**는 남쪽 하늘의 작은 별자리입니다. 신화 속 불사조의 이름을 따서 지어졌으며, 요한 바이어가 1603년 *우라노메트리아*에서 처음으로 천체 지도에 묘사했습니다. 프랑스의 탐험가이자 천문학자인 니콜라 루이 드 라카유는 1756년에 더 밝은 별을 지도에 표시하고 바이어 명칭을 부여했습니다. 이 별자리는 약 -39도에서 -57도의 적위와 23.5h에서 2.5h의 적경으로 뻗어 있습니다. 불사조, 두루미, 공작, 투카나 별자리는 남부의 새라고 불립니다.

가장 밝은 별인 알파 포에니시스는 아랍어로 '불사조'를 의미하는 안카아라는 이름이 붙었습니다. 겉보기 등급이 2.4인 주황색 거성입니다. 다음은 베타 포에니시스로, 실제로는 두 개의 노란색 거성으로 구성된 이진계로, 겉보기 등급이 3.3입니다. Nu 포에니시스는 먼지 원반을 가지고 있는 반면, 이 별자리에는 알려진 행성과 최근에 발견된 은하계 클러스터인 엘 고르도와 피닉스 클러스터가 있는 10개의 항성계가 있습니다. 각각 72억 광년과 57억 광년 떨어져 있으며, 가시 우주에서 가장 큰 두 천체입니다. 불사조는 두 개의 연간 유성우, 12월의 포에니시드와 7월의 포에니시드의 방사점입니다.

## 역사

피닉스는 피터 디르크스존 카이저와 프레데릭 드 호우트만의 관측을 통해 페트루스 플란시우스가 확립한 12개 별자리 중 가장 큰 별자리였습니다. 처음에는 플란시우스와 요도쿠스 혼디우스가 1597년(또는 1598년) 암스테르담에서 출판한 직경 35cm의 천구에 처음 등장했습니다. 천체 지도에 이 별자리가 처음 묘사된 것은 1603년 요한 바이어의 *우라노메트리아*에 나와 있습니다. 드 호우트만은 같은 해에 네덜란드어 이름인 *덴 보겔 페닉스*, "불사조"라는 이름으로 남방 별자리 카탈로그에 포함시켰는데, 이는 고전 신화의 불사조를 상징합니다. 가장 밝은 별인 알파 페니키스의 이름 중 하나인 안카는 아랍어: العنقاء, 로마자: al-‘anqā’, 문자 그대로 '피닉스'라는 별은 1800년 이후 별자리와 관련하여 만들어졌습니다.

천체 역사가 리차드 앨런은 플랑시우스와 라 카유가 도입한 다른 별자리와 달리 피닉스는 고대 천문학에서 실제 선례가 있다고 언급했습니다. 아랍인들은 이 별자리를 어린 타조 *알 리알* 또는 그리핀이나 독수리로 보았습니다. 또한, 아랍인들은 때때로 같은 별 무리를 근처 에리다누스 강에 있는 배 *알 자우락*으로 생각했습니다. 그는 "피닉스가 현대 천문학에 도입된 것은 어느 정도 발명이 아니라 채택을 통해서였다"고 말했습니다.

중국인들은 피닉스의 가장 밝은 별인 안카(알파 포에니시스)와 인접한 별자리 조각가의 별을 통합하여 새를 잡는 그물인 *바쿠이*를 묘사했습니다. 피닉스와 인접한 별자리인 그루스는 율리우스 쉴러가 함께 대제사장 아론을 묘사하는 것으로 보았습니다. 이 두 별자리는 근처의 공작자리와 큰부리자리와 함께 남쪽의 새라고 불립니다.

## 특징

피닉스는 북쪽으로 포르낙스와 조각가자리, 서쪽으로 그루스자리, 남쪽으로 투카나자리, 남쪽으로 히드루스자리 모서리에 접하고, 동쪽과 남동쪽으로 에리다누스자리로 둘러싸인 작은 별자리입니다. 밝은 별 아케르나르가 근처에 있습니다. 국제 천문학 연맹에서 1922년에 채택한 별자리의 세 글자 약어는 "페"입니다. 벨기에 천문학자 유진 델포르트가 1930년에 정한 공식 별자리 경계는 10개의 세그먼트로 구성된 다각형으로 정의됩니다. 적도 좌표계에서 이 경계의 적경 좌표는 23<sup>h</sup> 26.5<sup>m</sup>와 02<sup>h</sup> 25.0<sup>m</sup> 사이에 있고, 적위 좌표는 −39.31°와 −57.84° 사이에 있습니다. 즉, 북반구에서 40도선 이북에 사는 사람에게는 지평선 아래에 있고, 적도 이북에 사는 사람에게는 하늘 낮은 곳에 있습니다. 남반구 늦은 봄에 호주와 남아프리카와 같은 곳에서 가장 잘 보입니다. 별자리의 대부분은 내부에 있으며, 밝은 별 Achernar, Fomalhaut 및 Beta Ceti의 삼각형을 형성하여 찾을 수 있습니다. Ankaa는 대략 이 삼각형의 중앙에 있습니다.
```
<br>
<br>

## 3. 분류학 트리에 기술 추가

(*스타터*) 모델은 도메인별 기술로 *qna.yaml* 파일을 채워 사용자 지정 기술을 학습할 수 있습니다.
* 기술에 대한 각 *qna.yaml* 파일에는 다음 키가 있는 키-값 항목 세트를 포함

### 3.1 기술을 위한 *qna.yaml* 

$\color{lightblue}{\texttt{version}}$
* *qna.yaml* 파일의 버전은 SDG에 사용되는 파일 형식
* 현재 이 매개변수에 지원되는 값은 `2`

$\color{lightblue}{\texttt{created\\_by}}$
* Git 사용자 이름 또는 기여자 이름

$\color{lightblue}{\texttt{task\\_description}}$
* 기술과 그 기능에 대한 설명

$\color{lightblue}{\texttt{seed\\_examples}}$
* 키와 값 항목의 컬렉션
* 각 *qna.yaml* 파일에는 최소 5개의 시드 예제가 필요

$\color{lightblue}{\texttt{context}}$
* 접지된 기술을 사용하기 위해, 모델이 기술을 실행하는 데 필요한 정보가 포함된 추가 맥락을 제공
* `context` 필드는 근거 있는 기술에 필요
* 각 *qna.yaml*에는 5개의 컨텍스트 블록이 필요하고 최대 토큰 수는 500개

$\color{lightblue}{\texttt{question}}$
* 모델에 대한 질문을 지정
* 각 *qna.yaml* 파일에는 최소 5개의 질문과 답변 쌍이 필요하며, 최대 토큰 수는 250개

$\color{lightblue}{\texttt{answer}}$
* 모델에 대한 답을 지정
* 각 *qna.yaml* 파일에는 최소 5개의 질문과 답변 쌍이 필요하며, 최대 토큰 수는 250개
<br>

### 3.2 스킬 관련 YAML 파일 생성

원하는 사용 사례에 대해 모델이 새로운 기술을 학습할 수 있도록 택소노미 트리를 사용자 지정할 수 있습니다

#### 3.2.1 스킬 *qna.yaml* 파일을 담고 있는 택소노미 트리 생성 절차

1. 택소노미 디렉토리의 `compositional_skills` 폴더로 이동
2. 트리에 있는 디렉토리를 기반으로, 트리에서 스킬 *qna.yaml* 파일을 추가할 위치를 선택
   ```
   taxonomy/compositional_skills/grounded/<add_example>/qna.yaml
   ```
3. 텍스트 편집기를 사용하여 *qna.yaml* 파일을 생성
4. *qna.yaml* 파일에 필요한 키를 추가하고 변경 사항을 저장

> [!NOTE]
> SDG를 제대로 실행하려면 *qna.yaml* 파일에 최소 5개의 질문과 답변 쌍 예를 포함해야 합니다.

#### 3.2.2 검증

기술 관련 *qna.yaml* 파일 검증
```bash
ilab taxonomy diff
```
* 택소노미 트리와 *qna.yaml* 파일이 유효하고 올바르게 포맷되었는지 표시
* 발생한 오류를 수정할 수 있는 곳 표시

실행 결과 - 예) 유효한 택소노미 트리 및 *qna.yaml* 파일
```log
compositional_skills/writing/freeform/<example>/qna.yaml
Taxonomy in /taxonomy/ is valid :)
```

실행 결과 - 예) 오류가 있는 잘못된 택소노미 트리 및 *qna.yaml* 파일
```log
6:11 error syntax error: mapping values are not allowed here (syntax)
Reading taxonomy failed with the following error: 1 taxonomy with errors! Exiting.
```
<br>

### 3.3 스킬 관련 YAML 스펙 샘플

스킬은 지식 YAML 파일과 유사한 질문과 답변 레이아웃을 공유합니다.

RHEL AI에서 합성 데이터 생성(SDG) 프로세스는 사용자 생성 데이터에만 의존하는 대신 qna.yaml 시드 예제를 사용하여 모델이 학습할 수 있는 대규모 인공 데이터 세트를 만듭니다.
* 질문, 답변 및 컨텍스트 쌍의 순서는 SDG 또는 교육 프로세스에 영향을 미치지 않음
* 자유형, 근거 및 기초 스킬의 범주로 구분된 여러 유형의 스킬이 있음

#### 3.3.1 샘플: 자유형 구성 기술 *qna.yaml* 파일

```yaml
version: 2 #1
created_by: shadowman #2
task_description: '모델에게 운율을 맞추는 방법을 가르쳐 주세요.' #3
seed_examples:
  - question: horn과 운율이 맞는 단어 5개는 무엇입니까? #4 
    answer: warn, torn, born, thorn, 그리고 corn. #5
  - question: cat과 운율이 맞는 단어 5개는 무엇입니까?
    answer: bat, gnat, rat, vat, 그리고 mat.
  - question: 'poor'와 운율이 맞는 단어 5개는 무엇입니까?
    answer: door, shore, core, bore, 그리고 tore.
  - question: bank와 운율이 맞는 단어 5개는 무엇입니까?
    answer: tank, rank, prank, sank, 그리고 drank.
  - question: bake와 운율이 맞는 단어 5개는 무엇입니까?
    answer: wake, lake, steak, make, 그리고 quake.
```
1. 스킬 *qna.yaml* 형식의 버전을 지정
2. 이름이나 git 사용자 이름을 지정
3. 귀하의 기술과 그 기능에 대한 설명을 명시
4. 모델에게 할 질문을 지정
5. 모델에게 원하는 응답을 지정

#### 3.3.2 샘플: 접지된 구성 기술 *qna.yaml* 파일

```yaml
version: 2 #1
created_by: shadowman #2
task_description: 이 기술은 마크다운으로 포맷된 표를 읽을 수 있는 능력을 제공합니다. #3
seed_examples:
  - context: | #4
      | **품종**      | **크기**      | **짚는 소리** | **에너지** |
      |---------------|---------------|--------------|------------|
      | 아프간 하운드 | 25-27 인치     | 3/5          | 4/5        |
      | 래브라도      | 22.5-24.5 인치 | 3/5          | 5/5        |
      | 코커 스패니얼 | 14.5-15.5 인치 | 3/5          | 4/5        |
      | 푸들 (토이)   | <= 10 인치     | 4/5          | 4/5        |
    question: | #5
      어느 품종이 가장 에너지가 많나요?
    answer: | #6
      가장 에너지가 넘치는 품종은 래브라도입니다.
  - context: |
      | **이름** | **날짜** | **색깔** | **문자** | **숫자** |
      |----------|-----------|--------|----------|----------|
      | George   | 3월 5일   | 녹색   | A        | 1        |
      | Gráinne  | 12월 31일 | 빨간색 | B        | 2        |
      | Abigail  | 1월 17일  | 노란색 | C        | 3        |
      | Bhavna   | 4월 29일  | 보라색 | D        | 4        |
      | Rémy     | 9월 9일   | 파란색 | E        | 5        |
    question: |
      그레인의 문자는 무엇이고, 그녀의 색깔은 무엇입니까?
    answer: |
      Gráinne의 문자는 B이고 색상은 빨간색입니다.
  - context: |
      | 바나나 | 사과        | 블루베리  | 딸기      |
      |--------|-------------|----------|-----------|
      | 노락색 | 빨간색, 녹색 | 파란색   | 빨간색    |
      | 대형   | 중형        | 소형      | 소형      |
      | 껍질   | 껍질        | 껍질 없음 | 껍질 없음 |
    question: |
      어떤 과일이 파랗고 작으며 껍질이 없나요?
    answer: |
      블루베리는 파랗고 작으며 껍질이 없습니다.
```
1. 스킬 *qna.yaml* 형식의 버전을 지정
2. 이름이나 git 사용자 이름을 지정
3. 귀하의 기술과 그 기능에 대한 설명을 명시
4. 모델이 스킬을 실행하기 위해 알아야 하는 정보가 포함된 추가 컨텍스트를 지정
   * 접지된 스킬에 필요
5. 모델에게 할 질문을 지정
6. 모델에게 원하는 응답을 지정
<br>
<br>

## 4. 모델 성능 최적화를 위한 YAML 생성

택소노미 트리에 지식 및 기술을 추가하는 YAML 파일을 개선하여 생성된 합성 데이터를 최적화하고 더 높은 품질의 모델을 만들 수 있는 방법이 있습니다.

### 4.1 YAML 파일의 `context` 필드에 있는 다양하고 포괄적인 콘텐츠

각 `context` 블록에는 문서의 다양한 정보와 형식 유형이 포함되어야 합니다.
* 이를 통해 모델은 다양한 정보 표현 방법을 학습
* 이러한 다양한 정보 표현 유형에는 다음 항목을 포함
  + 문단
  + 다양한 유형의 표
  + 목록, 절차 및 정의
* `context` 블록은 문서의 포괄적인 예
  + `context` 콘텐츠와 Q&A 쌍의 총 길이는 750개 토큰이 최대
<br>

### 4.2 효과적인 질문 작성

질문은 모델이 답할 수 있는 질문 유형과 일치해야 합니다.
* 각 질문은 고유해야 하며 `context` 필드의 정보를 참조
* 전체 문장 질문을 포함하면,
  + 생성된 합성 데이터가 개선
  + 모델 응답 품질이 향상
<br>

### 4.3 효과적인 답변 작성

답변은 질문에 직접 응답해야 하며 모델이 제공할 수 있는 답변 유형을 반영해야 합니다.
* 답변은 완전한 문장이어야 하며 원래 질문을 참조
* 완전한 문장 답변을 포함하면,
  + 생성된 합성 데이터가 개선
  + 모델 응답 품질이 향상
* 답변은 `context` 블록에서 직접 복사하면 안됨
  + 직접 복사하면 모델이 추론 대신 추출을 학습하게 될 수 있음
* 질문에 답하는 정보는 `context` 블록에 있어야 함
  + 정보가 별도의 컨텍스트 블록에 있거나 전혀 참조되지 않으면 모델이 환각(hallucination)을 볼 수 있음
<br>

### 4.4 고품질 질문 & 답변 쌍의 예

```yaml
- question: 초콜릿칩 쿠키 24개를 만들려면 계란이 몇 개 필요할까요?
  answer: 초콜릿칩 쿠키 24개를 만들려면 계란 2개 정도가 필요합니다.
```
<br>

### 4.5 여러 문서 또는 여러 *qna.yaml* 파일을 사용해야 하는 경우

* 여러 문서가 유사한 주제나 도메인과 관련된 경우 단일 *qna.yaml* 파일을 사용
* 각 *qna.yaml* 파일에는 단일 문서 유형이 포함
  + YAML 파일에서 문서 유형을 혼합할 수 없음
* 문서가 관련이 없는 경우 별도의 *qna.yaml* 파일을 사용
<br>

### 4.6 YAML 파일에 링크 추가

* 모델은 링크를 기억할 수 있으므로 YAML 파일에 추가 가능
* 그러나 자주 변경되는 경우 하이퍼링크를 추가하지 않는 것이 좋음
<br>
<br>

## 5. InstructLab의 모델 훈련 및 평가

### 5.1 모델 훈련 & 평가

#### 5.1.1 모델 훈련

**모델 훈련 구성**
```bash
yq '.train' .config/instructlab/config.yaml
```

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

#### 5.1.2 모델 평가

**모델 평가 구성**
```bash
 yq '.evaluate' .config/instructlab/config.yaml
```

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
<br>

### 5.2 모델 훈련 및 평가 디렉토리

#### 5.2.1 택소노미 트리

```bash
tree -F -L 2 .local/share/instructlab/taxonomy/
```

```
[instruct@bastion ~]$ tree -F -L 2 .local/share/instructlab/taxonomy/
.local/share/instructlab/taxonomy/
|-- CODE_OF_CONDUCT.md
|-- CONTRIBUTING.md
|-- CONTRIBUTOR_ROLES.md
|-- LICENSE
|-- MAINTAINERS.md
|-- Makefile
|-- README.md
|-- SECURITY.md
|-- compositional_skills/
|   |-- arts/
|   |-- engineering/
|   |-- geography/
|   |-- grounded/
|   |-- history/
|   |-- linguistics/
|   |-- miscellaneous_unknown/
|   |-- philosophy/
|   |-- religion/
|   |-- science/
|   `-- technology/
|-- docs/
|   |-- KNOWLEDGE_GUIDE.md
|   |-- README.md
|   |-- SKILLS_GUIDE.md
|   |-- assets/
|   |-- contributing_via_GH_UI.md
|   |-- knowledge-contribution-guide.md
|   |-- taxonomy_diagram.md
|   |-- taxonomy_diagram.png
|   |-- template_qna.yaml
|   `-- triaging/
|-- foundational_skills/
|   `-- reasoning/
|-- governance.md
|-- knowledge/
|   |-- arts/
|   |-- engineering/
|   |-- geography/
|   |-- history/
|   |-- linguistics/
|   |-- mathematics/
|   |-- miscellaneous_unknown/
|   |-- philosophy/
|   |-- religion/
|   |-- science/
|   `-- technology/
`-- scripts/
    |-- check-yaml.py*
    `-- requirements.txt

30 directories, 19 files

[instruct@bastion ~]$
```

#### 5.2.2 데이터 세트

```bash
tree -F -L 2 .local/share/instructlab/datasets/
```

```
[instruct@bastion ~]$ tree -F -L 2 .local/share/instructlab/datasets/
.local/share/instructlab/datasets/

0 directories, 0 files

[instruct@bastion ~]$
```
<br>
<br>

## 90. 예제 샘플

### 90.1 불사조 별자리

#### 90.1.1 지식을 위한 *qna.yaml* 파일 준비

실행 명령어
```bash
mkdir -pv .local/
```

실행 결과
```
[instruct@bastion ~]$ cd .local/share/instructlab/taxonomy/knowledge/

[instruct@bastion knowledge]$ mkdir -pv science/astronomy/constellation/phoenix
mkdir: created directory 'science/astronomy'
mkdir: created directory 'science/astronomy/constellation'
mkdir: created directory 'science/astronomy/constellation/phoenix'

[instruct@bastion knowledge]$ ls -lh science/astronomy/constellation/phoenix/qna.yaml
-rw-r--r--. 1 instruct users 9.2K Mar 23 12:04 science/astronomy/constellation/phoenix/qna.yaml

[instruct@bastion knowledge]$
```
* 도메인 기반 디렉터리 생성
* *qna.yaml* 파일 생성

#### 90.1.2 지식을 위한 [*qna.yaml*](https://github.com/starlab3030/taxonomy_for_instructlab/blob/main/knowledge/science/astronomy/constellation/phoenix/qna.yaml) 파일 확인

실행 명령어
```bash
cat .local/share/instructlab/taxonomy/knowledge/science/astronomy/constellation/phoenix/qna.yaml
```

실행 결과
```yaml
version: 3
domain: astronomy
document_outline: |
  불사조 별자리에 대한 정보에는 별자리에 있는 별의 역사, 특성, 특징 등이 포함됩니다.
created_by: shadowman
seed_examples:
  - context: |
      **불사조**는 남쪽 하늘의 작은 별자리입니다. 신화 속의 불사조(신화)에서 이름을 따온 이 별자리는 요한 바이어가 1603년 Uranometria에서 천체 지도에 처음 묘사했습니다. 프랑스의 탐험가이자 천문학자인 니콜라 루이 드 라카유는 1756년에 더 밝은 별을 지도에 표시하고 바이어 명칭을 부여했습니다. 이 별자리는 적위가 약 -39도에서 -57도, 적경이 23.5시에서 2.5시입니다. 불사조, 두루미, 공작, 투카나 별자리는 남방새로 알려져 있습니다.
    questions_and_answers:
      - question: |
          불사조 별자리는 무엇입니까?
        answer: |
          불사조 자리는 남쪽 하늘의 작은 별자리입니다.
      - question: |
          불사조 별자리를 만든 사람은 누구입니까?
        answer: |
          불사조 별자리는 프랑스의 탐험가이자 천문학자 니콜라 루이 드 라카유가 기록했습니다.
      - question: |
          불사조 별자리는 얼마나 멀리 뻗어 있나요?
        answer: |
          불사조 별자리는 적위가 대략 -39°에서 -57°까지이고, 적경이 23.5시에서 2.5시입니다.
  - context: |
      불사조는 Petrus Plancius가 Pieter Dirkszoon Keyser와 Frederick de Houtman의 관측을 통해 확립한 12개 별자리 중 가장 큰 별자리였습니다. 처음에는 Plancius가 Jodocus Hondius와 함께 암스테르담에서 1597년(또는 1598년)에 출판한 직경 35cm의 천구의에 처음 등장했습니다. 천체 지도에 이 별자리가 처음 묘사된 것은 1603년 Johann Bayer *Uranometria*에 있었습니다. De Houtman은 같은 해에 네덜란드 이름 *Den voghel Fenicx*, "The Bird Phoenix"라는 이름으로 그의 남방 별자리 카탈로그에 포함시켰는데, 이는 고전 신화의 불사조를 상징합니다. 가장 밝은 별인 Alpha Phoenicis의 이름 중 하나인 Ankaa는 아랍어 العنقاء에서 유래했으며, 로마자 표기로는 al-‘anqā’, 문자 그대로는 '불사조'를 의미하며, 별자리와 관련하여 1800년 이후에 만들어졌습니다.
    questions_and_answers:
      - question: |
          불사조 자리에서 가장 밝은 별은 무엇이라고 불리나요?
        answer: |
          알파 페니시스(Alpha Phoenicis) 또는 안카(Ankaa)는 불사조 별자리에서 가장 밝은 별입니다.
      - question: 불사조 별자리는 처음 어디에서 나타났나요?
        answer: |
          불사조 별자리는 Jodocus Hondius와 함께 Plancius가 암스테르담에서 1597년(또는 1598년)에 출판한 직경 35cm의 천구에 처음 나타났습니다.
      - question: |
          "불사조 새"는 무엇을 상징합니까?
        answer: |
          "불사조"는 고전 신화의 불사조를 상징합니다.
  - context: |
      불사조는 북쪽으로 포르낙스와 스컬프터, 서쪽으로 그루스, 남쪽으로 투카나, 남쪽으로 히드루스 모서리에 접하고, 동쪽과 남동쪽으로 에리다누스에 접한 작은 별자리입니다. 밝은 별 아케르나르가 근처에 있습니다. 국제 천문학 연맹에서 1922년에 채택한 별자리의 세 글자 약어는 "페"입니다. 벨기에 천문학자 유진 델포르트가 1930년에 정한 공식 별자리 경계는 10개의 세그먼트로 구성된 다각형으로 정의됩니다. 적도 좌표계에서 이 경계의 적경 좌표는 23<sup>h</sup> 26.5<sup>m</sup>와 02<sup>h</sup> 25.0<sup>m</sup> 사이에 있고, 적위 좌표는 −39.31°와 −57.84° 사이에 있습니다. 즉, 북반구에서 40도선 이북에 사는 사람에게는 지평선 아래에 있고, 적도 이북에 사는 사람에게는 하늘 낮은 곳에 있습니다. 남반구 늦은 봄에 호주와 남아프리카와 같은 곳에서 가장 잘 보입니다. 별자리의 대부분은 내부에 있으며, 밝은 별 Achernar, Fomalhaut 및 Beta Ceti의 삼각형을 형성하여 찾을 수 있습니다. Ankaa는 대략 이 삼각형의 중앙에 있습니다.
    questions_and_answers:
      - question: 불사조 별자리의 특징은 무엇입니까?
        answer: |
          불사조는 북쪽으로 Fornax와 Sculptor, 서쪽으로 Grus, 남쪽으로 Tucana, 남쪽으로 Hydrus의 모서리에 접하고 동쪽과 남동쪽으로 Eridanus에 접한 작은 별자리입니다. 밝은 별 Achernar가 근처에 있습니다.
      - question: |
          불사조 자리가 가장 잘 보이는 때는 언제인가요?
        answer: |
          불사조는 남반구 늦은 봄에 호주와 남아프리카와 같은 지역에서 가장 잘 보입니다.
      - question: |
          불사조 별자리의 경계는 어디인가요?
        answer: |
          벨기에의 천문학자 외젠 델포르테가 1930년에 정한 불사조의 공식 별자리 경계는 10개의 부분으로 구성된 다각형으로 정의됩니다
  - context: |
      지금까지 10개의 별에 행성이 있는 것으로 밝혀졌고, SuperWASP 프로젝트를 통해 4개의 행성계가 발견되었습니다. HD 142는 겉보기 등급이 5.7인 노란색 거성으로, 목성의 1.36배 질량의 행성(HD 142b)이 있으며, 328일마다 공전합니다. HD 2039는 겉보기 등급이 9.0인 노란색 준거성으로, 약 330광년 떨어진 곳에 있으며, 목성의 6배 질량의 행성(HD 2039)이 있습니다. WASP-18은 겉보기 등급이 9.29인 별로, 뜨거운 목성과 비슷한 행성(WASP-18b)이 있는 것으로 밝혀졌으며, 별을 공전하는 데 하루도 걸리지 않았습니다. 이 행성 때문에 WASP-18이 실제보다 더 오래되게 보이는 것으로 추정됩니다. WASP-4와 WASP-5는 태양형 노란색 별로 약 1000광년 떨어져 있으며 13등급이며 각각 목성보다 큰 행성이 ​​하나 있습니다. WASP-29는 분광형 K4V, 시각적 등급 11.3의 주황색 왜성으로 토성과 비슷한 크기와 질량의 행성 동반성이 있습니다. 이 행성은 3.9일마다 궤도를 완료합니다.
    questions_and_answers:
      - question: 불사조 별자리에는 행성을 가진 별이 몇 개나 있습니까?
        answer: |
          불사조 별자리에서 10개의 별이 행성을 가지고 있는 것으로 발견되었으며, SuperWASP 프로젝트를 통해 4개의 행성계가 발견되었습니다.
      - question: |
          HD 142는 무엇인가요?
        answer: |
          HD 142는 겉보기 등급 5.7의 황색 거성이며, 목성 질량의 1.36배인 행성(HD 142 b)을 갖고 있으며 328일마다 공전합니다.
      - question: |
          WASP-4와 WASP-5는 태양형 노란색 별인가요?
        answer: |
          네, WASP-4와 WASP-5는 태양형 노란색 별로서 거리는 약 1000광년이고 등급은 13등급이며, 각각 목성보다 큰 행성을 하나 가지고 있습니다.
  - context: |
      별자리는 은하수의 은하면에 있지 않으며, 눈에 띄는 성단은 없습니다. NGC 625는 겉보기 등급 11.0의 왜소 불규칙 은하로 약 1,270만 광년 떨어져 있습니다. 지름이 24,000광년에 불과한 이 은하는 조각가 그룹의 외곽 구성원입니다. NGC 625는 충돌에 연루된 것으로 생각되며 활발한 별 형성이 폭발적으로 일어나고 있습니다. NGC 37은 겉보기 등급 14.66의 렌즈형 은하입니다. 지름이 약 42킬로파섹 137,000광년이고 나이는 약 129억 년입니다. 불규칙 은하 NGC 87과 세 개의 나선 은하 NGC 88, NGC 89, NGC 92로 구성된 로버트 사중주는 약 1억 6천만 광년 떨어진 곳에 위치하며 충돌하고 합쳐지는 과정에 있는 네 개의 은하로 구성된 그룹입니다. 이들은 반경 1.6분각의 원 안에 있으며, 이는 약 75,000광년에 해당합니다. ESO 243-49 은하에는 중간 질량 블랙홀인 HLX-1이 있습니다. 이는 이런 종류의 블랙홀로는 처음으로 확인되었습니다. ESO 243-49와의 충돌로 흡수된 왜소 은하의 잔해로 생각됩니다. 발견되기 전에는 이 종류의 블랙홀은 가설에 불과했습니다.
    questions_and_answers:
      - question: |
          불사조 자리는 은하수의 일부인가요?
        answer: |
          불사조 별자리는 우리 은하의 은하면에 있지 않으며, 뚜렷한 별 무리도 없습니다.
      - question: |
          NGC 625는 몇 광년 떨어져 있나요?
        answer: |
          NGC 625는 지름이 24,000 광년이고 조각가 은하군의 외곽 구성원입니다.
      - question: |
          로버트 사중주는 무엇으로 구성되어 있나요?
        answer: |
          로버트의 사중주는 불규칙 은하 NGC 87과 세 개의 나선 은하 NGC 88, NGC 89, NGC 92로 구성되어 있습니다.
document:
  repo: https://github.com/starlab3030/knowledges_for_instructlab
  commit: 9f8143ace51b0423922b90c0dc2d608055d84340
  patterns:
    - phoenix_constellation.md
```

#### 90.1.3 지식을 위한 *qna.yaml* 파일 내 관련 마크다운 문서 확인

[phoenix_constellation.md](https://github.com/starlab3030/knowledges_for_instructlab/blob/main/phoenix_constellation.md)
```md
# 불사조(별자리)

**불사조**는 남쪽 하늘의 작은 별자리입니다. 신화 속 불사조의 이름을 따서 지어졌으며, 요한 바이어가 1603년 *우라노메트리아*에서 처음으로 천체 지도에 묘사했습니다. 프랑스의 탐험가이자 천문학자인 니콜라 루이 드 라카유는 1756년에 더 밝은 별을 지도에 표시하고 바이어 명칭을 부여했습니다. 이 별자리는 약 -39도에서 -57도의 적위와 23.5h에서 2.5h의 적경으로 뻗어 있습니다. 불사조, 두루미, 공작, 투카나 별자리는 남부의 새라고 불립니다.

가장 밝은 별인 알파 포에니시스는 아랍어로 '불사조'를 의미하는 안카아라는 이름이 붙었습니다. 겉보기 등급이 2.4인 주황색 거성입니다. 다음은 베타 포에니시스로, 실제로는 두 개의 노란색 거성으로 구성된 이진계로, 겉보기 등급이 3.3입니다. Nu 포에니시스는 먼지 원반을 가지고 있는 반면, 이 별자리에는 알려진 행성과 최근에 발견된 은하계 클러스터인 엘 고르도와 피닉스 클러스터가 있는 10개의 항성계가 있습니다. 각각 72억 광년과 57억 광년 떨어져 있으며, 가시 우주에서 가장 큰 두 천체입니다. 불사조는 두 개의 연간 유성우, 12월의 포에니시드와 7월의 포에니시드의 방사점입니다.

## 역사

피닉스는 피터 디르크스존 카이저와 프레데릭 드 호우트만의 관측을 통해 페트루스 플란시우스가 확립한 12개 별자리 중 가장 큰 별자리였습니다. 처음에는 플란시우스와 요도쿠스 혼디우스가 1597년(또는 1598년) 암스테르담에서 출판한 직경 35cm의 천구에 처음 등장했습니다. 천체 지도에 이 별자리가 처음 묘사된 것은 1603년 요한 바이어의 *우라노메트리아*에 나와 있습니다. 드 호우트만은 같은 해에 네덜란드어 이름인 *덴 보겔 페닉스*, "불사조"라는 이름으로 남방 별자리 카탈로그에 포함시켰는데, 이는 고전 신화의 불사조를 상징합니다. 가장 밝은 별인 알파 페니키스의 이름 중 하나인 안카는 아랍어: العنقاء, 로마자: al-‘anqā’, 문자 그대로 '피닉스'라는 별은 1800년 이후 별자리와 관련하여 만들어졌습니다.

천체 역사가 리차드 앨런은 플랑시우스와 라 카유가 도입한 다른 별자리와 달리 피닉스는 고대 천문학에서 실제 선례가 있다고 언급했습니다. 아랍인들은 이 별자리를 어린 타조 *알 리알* 또는 그리핀이나 독수리로 보았습니다. 또한, 아랍인들은 때때로 같은 별 무리를 근처 에리다누스 강에 있는 배 *알 자우락*으로 생각했습니다. 그는 "피닉스가 현대 천문학에 도입된 것은 어느 정도 발명이 아니라 채택을 통해서였다"고 말했습니다.

중국인들은 피닉스의 가장 밝은 별인 안카(알파 포에니시스)와 인접한 별자리 조각가의 별을 통합하여 새를 잡는 그물인 *바쿠이*를 묘사했습니다. 피닉스와 인접한 별자리인 그루스는 율리우스 쉴러가 함께 대제사장 아론을 묘사하는 것으로 보았습니다. 이 두 별자리는 근처의 공작자리와 큰부리자리와 함께 남쪽의 새라고 불립니다.

## 특징

피닉스는 북쪽으로 포르낙스와 조각가자리, 서쪽으로 그루스자리, 남쪽으로 투카나자리, 남쪽으로 히드루스자리 모서리에 접하고, 동쪽과 남동쪽으로 에리다누스자리로 둘러싸인 작은 별자리입니다. 밝은 별 아케르나르가 근처에 있습니다. 국제 천문학 연맹에서 1922년에 채택한 별자리의 세 글자 약어는 "페"입니다. 벨기에 천문학자 유진 델포르트가 1930년에 정한 공식 별자리 경계는 10개의 세그먼트로 구성된 다각형으로 정의됩니다. 적도 좌표계에서 이 경계의 적경 좌표는 23<sup>h</sup> 26.5<sup>m</sup>와 02<sup>h</sup> 25.0<sup>m</sup> 사이에 있고, 적위 좌표는 −39.31°와 −57.84° 사이에 있습니다. 즉, 북반구에서 40도선 이북에 사는 사람에게는 지평선 아래에 있고, 적도 이북에 사는 사람에게는 하늘 낮은 곳에 있습니다. 남반구 늦은 봄에 호주와 남아프리카와 같은 곳에서 가장 잘 보입니다. 별자리의 대부분은 내부에 있으며, 밝은 별 Achernar, Fomalhaut 및 Beta Ceti의 삼각형을 형성하여 찾을 수 있습니다. Ankaa는 대략 이 삼각형의 중앙에 있습니다.
```

#### 90.1.4 지식을 위한 *qna.yaml* 파일 검증

실행 명령어
```
ilab taxonomy diff
```

실행 결과
```
[instruct@bastion ~]$ ilab taxonomy diff
compositional_skills/grounded/linguistics/inclusion/qna.yaml
compositional_skills/grounded/linguistics/writing/rewriting/qna.yaml
compositional_skills/linguistics/synonyms/qna.yaml
knowledge/arts/music/fandom/swifties/qna.yaml
knowledge/science/animals/birds/black_capped_chickadee/qna.yaml
knowledge/science/astronomy/constellation/phoenix/qna.yaml
ERROR 2025-03-23 12:02:24,777 instructlab.schema.taxonomy:134: var/home/instruct/.local/share/instructlab/taxonomy/knowledge/science/astronomy/constellation/phoenix/qna.yaml:83:3 wrong indentation: expected 4 but found 2 (indentation)
ERROR 2025-03-23 12:02:24,777 instructlab.schema.taxonomy:134: var/home/instruct/.local/share/instructlab/taxonomy/knowledge/science/astronomy/constellation/phoenix/qna.yaml:83:29 trailing spaces (trailing-spaces)
Reading taxonomy failed with the following error: 2 total errors found across 6 taxonomy files!

[instruct@bastion ~]$ ilab taxonomy diff
compositional_skills/grounded/linguistics/inclusion/qna.yaml
compositional_skills/grounded/linguistics/writing/rewriting/qna.yaml
compositional_skills/linguistics/synonyms/qna.yaml
knowledge/arts/music/fandom/swifties/qna.yaml
knowledge/science/animals/birds/black_capped_chickadee/qna.yaml
knowledge/science/astronomy/constellation/phoenix/qna.yaml
ERROR 2025-03-23 12:03:56,695 instructlab.schema.taxonomy:134: var/home/instruct/.local/share/instructlab/taxonomy/knowledge/science/astronomy/constellation/phoenix/qna.yaml:83:31 trailing spaces (trailing-spaces)
Reading taxonomy failed with the following error: 1 total errors found across 6 taxonomy files!

[instruct@bastion ~]$ ilab taxonomy diff
compositional_skills/grounded/linguistics/inclusion/qna.yaml
compositional_skills/grounded/linguistics/writing/rewriting/qna.yaml
compositional_skills/linguistics/synonyms/qna.yaml
knowledge/arts/music/fandom/swifties/qna.yaml
knowledge/science/animals/birds/black_capped_chickadee/qna.yaml
knowledge/science/astronomy/constellation/phoenix/qna.yaml
Taxonomy in /var/home/instruct/.local/share/instructlab/taxonomy is valid :)

[instruct@bastion ~]$
```
* *qna.yaml* 파일은 YAML 형식을 따라야 함
* *qna.yaml* 파일의 항목에 끝에 스페이스가 추가되어서도 안됨
<br>
<br>

## 99. 참조

### 99.1 참조 사이트

**참조 URL**
* [InstructLab](https://github.com/instructlab)
  + [taxonomy](https://github.com/instructlab/taxonomy)
<br>

### 99.2 샘플 GitHub

**STARLab GitHub**
* [샘플 택소노미 트리](https://github.com/starlab3030/taxonomy_for_instructlab/tree/main)
* [샘플 마크다운 문서](https://github.com/starlab3030/knowledges_for_instructlab/tree/main)
<br>
<br>

------
[차례](../README.md)