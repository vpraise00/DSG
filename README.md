# 기존 OpenSCENARIO에 Disturbance 추가
랩실 서버 기준으로 코드 작성됨

python 3.10.16

---
K-City 맵만 시나리오 수정 가능

`weather_rootcause.py` 에 눈, 비 상황 xml 코드 블럭으로 만들어주는 함수 작성, 각종 수치는 [ASAM 가이드](https://publications.pages.asam.net/standards/ASAM_OpenSCENARIO/ASAM_OpenSCENARIO_XML/v1.3.0/generated/content/Weather.html) 참고하여 랜덤으로 지정.

`falling_obj_rootcause.py`에 낙하물 생성하는 코드. 현재 낙하물 생성 위치는 차량의 LinkPosition을 기반으로 하여 index를 참고하여 임의로 차량의 경로 안에 생성. Ego의 대처(대응)도 코드에 포함.

`falling_obj_rootcause_rel.py`는 낙하물물 생성하는 코드이나, RelativeObjectPosition을 기반으로 하여 Ego 차량에 상대적인 Euclidian Distance를 기반으로 낙하물 위치 생성.

`Scenario_Generator.py` 에서 `input_file` 의 파일명을 K-City 시나리오 중 하나로 변경하여 시나리오 생성 가능.

* usage:

    `python Scenario_Generator.py <file> [options]` 

      file : Input File Path (.xosc)
    
    options:

      --disturbance <disturbance> : Select the disturbance that applies to your input scenario. [rain, snow, fallOBJ]
      --action <action> : Select the Ego action after meet falling objects. [lanechange, stop]
      --obj_pos <obj_pos> : You can define Object's position in LinkPosition or RelativeObjectPosition. [relative, link]
      --distance <distance> : If you use relative position then, you can define object distance from ego. (default is 30m.)