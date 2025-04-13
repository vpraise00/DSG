# 기존 OpenSCENARIO에 Disturbance 추가
랩실 서버 기준으로 코드 작성됨

python 3.10.16

---
K-City 맵만 시나리오 수정 가능

`weather_rootcause.py` 에 눈, 비 상황 xml 코드 블럭으로 만들어주는 함수 작성, 각종 수치는 [ASAM 가이드](https://publications.pages.asam.net/standards/ASAM_OpenSCENARIO/ASAM_OpenSCENARIO_XML/v1.3.0/generated/content/Weather.html) 참고하여 랜덤으로 지정

`falling_obj_rootcause.py`에 낙하물 생성하는 코드 임시로 생성. 현재 낙하물 생성 위치는 WorldPosition으로 정의되어 수정이 필요. 차후에 차량의 LinkPosition을 기반으로 하여 index를 참고하여 임의로 차량의 경로 안에 생성시킬 예정.

`Scenario_Generator.py` 에서 `input_file` 의 파일명을 K-City 시나리오 중 하나로 변경하여 시나리오 생성 가능

* usage:

    `python Scenario_Generator.py <file> [options]` 

      file : Input File Path (.xosc)
    
    options:

      --disturbance <disturbance> : Select the disturbance that applies to your input scenario. [rain, snow, fallOBJ]
      --action <action> : Select the Ego action after meet falling objects. [lanechange, stop]