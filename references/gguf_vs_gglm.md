# GGUF와 GGML의 차이

**차례**
1. [PT-Generated Unified Format(GGUF)란](gguf_vs_gglm.md#1-pt-generated-unified-formatgguf란)
2. [GGUF와 GGML의 차이](gguf_vs_gglm.md#2-gguf와-ggml의-차이)
3. [GGUF로 전환](gguf_vs_gglm.md#3-gguf로-전환)
4. []()


## 1. PT-Generated Unified Format(GGUF)란

GPT-Generated Unified Format(GGUF)은 대규모 언어 모델(LLM)의 사용 및 배포를 간소화하는 파일 형식입니다. GGUF는 추론 모델을 저장하고 소비자 등급 컴퓨터 하드웨어에서 우수한 성능을 발휘하도록 특별히 설계되었습니다.

**GGUF 특징**
* 효율적인 실행을 위해 모델 매개변수(가중치 및 편향)를 추가 메타데이터와 결합하여 이를 달성
* GGUF는 명확하고 확장 가능하며 다재다능하며 이전 모델과의 호환성을 깨지 않고도 새로운 정보를 통합
* GGUF는 이전 파일 형식인 GGML에서 구축한 기반을 바탕으로 한 최근 개발된 형식
  + 모델의 빠른 로딩 및 저장을 위해 명확하게 설계된 바이너리 형식
  + Python 및 R과 같은 다양한 프로그래밍 언어와 호환 (-> 이 때문에 GGUF는 형식의 인기를 더함)
  + 미세 조정을 지원하므로 사용자는 LLM을 특수 애플리케이션에 맞게 조정
  + 애플리케이션 간 모델 배포를 위한 프롬프트 템플릿을 저장
* GGML은 여전히 ​​사용되고 있지만 지원은 GGUF로 대체됨
<br>
<br>

## 2. GGUF와 GGML의 차이


<br>
<br>

## 3. GGUF로 전환

<br>
<br>

## 4. 





<br>
<br>

<hr>

[차례](../README.md)