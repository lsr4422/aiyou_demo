from fastapi import FastAPI, Query
from pydantic import BaseModel
#from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, GenerationConfig

from fastapi import Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
import io
import os
import time
import requests
# import jsonify

app = FastAPI()


# React build 파일을 정적 파일로 서빙
app.mount("/static", StaticFiles(directory="./build/static"), name="static")


templates = Jinja2Templates(directory="./build")


@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html"
    )




@app.post('/generate-file')
async def generate_file(text: str = Form(...)):
    try:
        input_text = text
        print(input_text)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Error in input processing: {e}"})

    try:
        # 외부 API에 POST 요청 보내기
        print('try')
        response = requests.post('http://aiyou_con:8000/ai', params={'prompt': input_text})

        response.raise_for_status()  # 요청이 성공적인지 확인

        # ZIP 파일을 반환하는 경우
        if response.headers['Content-Type'] == 'application/zip':
            # 응답 데이터를 바이너리 스트림으로 변환
            zip_file = io.BytesIO(response.content)

            # StreamingResponse로 클라이언트에 반환
            return StreamingResponse(zip_file, media_type='application/zip', headers={
                "Content-Disposition": "attachment; filename=generated_file.zip"
            })
        # 다른 처리 방식이 필요할 경우 여기에 추가 로직
        else:
            raise HTTPException(status_code=400, detail="Unexpected content type")
    except requests.exceptions.RequestException as e:
        # 오류 발생 시 클라이언트에 에러 메시지 반환
        print('bad')
        raise HTTPException(status_code=500, detail=str(e))
    


@app.get("/getsound")
async def get_sound():
    file_path = "./static/sounds/audio.wav"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(path=file_path, media_type="audio/wav", filename="audio.wav")

