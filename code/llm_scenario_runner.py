#!/usr/bin/env python3
import sys
import json
import subprocess
from pathlib import Path
from typing import List

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, GenerationConfig

# 1) scenario_generator.py 래퍼 (변경 없음)
def wrap_generate_scenario(argv: List[str]) -> str:
    p = subprocess.run([sys.executable] + argv, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip())
    stem = Path(argv[1]).stem
    disturbance = argv[argv.index("--disturbance")+1]
    return f"{stem}_{disturbance}.xosc"

# 2) 로컬 LLM 초기화
MODEL_NAME = "google/flan-t5-base"  # 공개 모델 예시
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model     = AutoModelForSeq2SeqLM.from_pretrained(
    MODEL_NAME,
    device_map="auto",
    torch_dtype=torch.float16
)
gen_config = GenerationConfig(
    temperature=0.7,
    max_new_tokens=256,
    do_sample=True
)

def call_local_llm(system: str, user: str) -> dict:
    """
    system + user 프롬프트를 합쳐서 로컬 모델에 던지고,
    JSON 포맷으로 된 plan_command 결과를 파싱해 반환.
    """
    prompt = f"""### System:
{system}

### User:
{user}

### Assistant:
위 요청을 처리하기 위한 JSON 형태의 인자를 반환하세요.  
반환 객체에는 반드시 다음 필드를 포함해야 합니다:
  - input_file (string)
  - disturbance (\"rain\"|\"snow\"|\"fallOBJ\"|\"construction\"|\"speedConstraint\")
  - distance (number)
선택필드:
  - obj_pos (\"relative\"|\"link\")
  - action (\"lanechange\"|\"stop\")
  - target_speed (number)

예시 출력: 
{{"input_file":"input.xosc","disturbance":"fallOBJ","distance":50,"obj_pos":"relative","action":"stop"}}

이제 JSON만 정확히 출력하세요:
"""
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, generation_config=gen_config)
    text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # 모델이 “Assistant:” 라인을 포함해서 내보낼 수 있으니 JSON 부분만 뽑아봅니다
    try:
        json_str = text.strip().split("\n")[-1]
        plan = json.loads(json_str)
    except Exception as e:
        raise RuntimeError(f"JSON 파싱 실패: {e}\n모델 응답 원문:\n{text}")
    return plan

def main():
    if len(sys.argv) < 3:
        print("Usage: llm_local_runner.py <input.xosc> <자연어 요청>", file=sys.stderr)
        sys.exit(1)

    input_file, user_req = sys.argv[1], sys.argv[2]

    system_prompt = (
        "당신은 scenario_generator.py를 실행하기 위한 CLI 인자를 JSON으로 설계하는 전문가입니다. "
        "실행 오류가 발생하면 JSON 수정을 반복합니다."
    )
    user_prompt = f"기반 시나리오 '{input_file}'에 '{user_req}'"

    # Plan–Execute–Feedback 루프
    messages = []
    for _ in range(3):
        # 1) Plan: 로컬 모델로 JSON 인자 생성
        plan = call_local_llm(system_prompt, user_prompt)
        argv = [
            "scenario_generator.py", plan["input_file"],
            "--disturbance", plan["disturbance"],
            "--distance", str(plan["distance"])
        ]
        if plan.get("obj_pos"):
            argv += ["--obj_pos", plan["obj_pos"]]
        if plan.get("action"):
            argv += ["--action", plan["action"]]
        if plan.get("target_speed") is not None:
            argv += ["--target-speed", str(plan["target_speed"])]
        # 2) Execute
        try:
            out = wrap_generate_scenario(argv)
            print(f"생성 성공: {out}")
            return
        except RuntimeError as e:
            # 3) Feedback: 오류 메시지를 다음 Plan 입력으로
            user_prompt = (
                f"{user_req}\n"
                f"이전 실행에서 오류가 발생했습니다:\n{e}\n"
                "JSON을 수정해 다시 제시해 주세요."
            )
    print("시나리오 생성 실패", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    main()
